# coding: utf-8 -*-

import functools
import psycopg2

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _order = 'expiration_date desc, name, id'

    vtt_is_expired = fields.Boolean('Is Expired?')

    vtt_tag_ids = fields.Many2many('vtt.product.tag', string='Tags', compute='_compute_product_tags', store=True)

    product_qty_available = fields.Boolean('Quantity Available', compute='_compute_qty_available',
                                           search='_value_search_qty_available')

    pack_barcode = fields.Char('Packing Barcode', related='product_id.pack_barcode', store=True)
    product_barcode = fields.Char('Product Barcode', related='product_id.product_barcode', store=True)

    @api.depends('quant_ids', 'quant_ids.quantity')
    def _compute_qty_available(self):
        for lot in self:
            # We only care for the quants in internal or transit locations.
            quants = lot.quant_ids.filtered(lambda q: q.location_id.usage == 'internal' or (q.location_id.usage == 'transit' and q.location_id.company_id))
            product_qty = sum(quants.mapped('quantity'))
            if product_qty:
                lot.product_qty_available = True
            else:
                lot.product_qty_available = False

    @api.model
    def _value_search_qty_available(self, operator, value):
        recs = self.search([]).filtered(lambda x: x.product_qty_available is True)

        return [('id', 'in', [x.id for x in recs])]

    def name_get(self):
        result = []
        for lot in self:
            name = lot.name
            if lot.expiration_date:
                dt = self.env["res.lang"].datetime_formatter(lot.expiration_date)[:10]
                name += f' - {dt}'
            result.append((lot.id, name))
        return result

    @api.depends('product_id', 'product_id.vtt_tag_ids')
    def _compute_product_tags(self):
        for lot in self:
            lot.vtt_tag_ids = lot.product_id.vtt_tag_ids.ids

    # Override for total unique LN
    @api.constrains('name')
    def _check_unique_lot(self):
        domain = [('product_id', 'in', self.product_id.ids),
                  ('company_id', 'in', self.company_id.ids),
                  ('name', 'in', self.mapped('name'))]
        fields = ['company_id', 'product_id', 'name']
        groupby = ['name']
        records = self.read_group(domain, fields, groupby, lazy=False)
        error_message_lines = []
        for rec in records:
            if rec['__count'] != 1:
                product_name = self.env['product.product'].browse(rec['product_id'][0]).display_name
                error_message_lines.append(_(" - Product: %s, Serial Number: %s", product_name, rec['name']))
        if error_message_lines:
            raise ValidationError(_(
                'The serial number must be unique.\nFollowing combination contains duplicates:\n') + '\n'.join(
                error_message_lines))

    # ===================== Merge Production Lot
    def _get_fk_on(self, table):
        """ return a list of many2one relation with the given table.
            :param table : the name of the sql table to return relations
            :returns a list of tuple 'table name', 'column name'.
        """
        query = """
            SELECT cl1.relname as table, att1.attname as column
            FROM pg_constraint as con, pg_class as cl1, pg_class as cl2, pg_attribute as att1, pg_attribute as att2
            WHERE con.conrelid = cl1.oid
                AND con.confrelid = cl2.oid
                AND array_lower(con.conkey, 1) = 1
                AND con.conkey[1] = att1.attnum
                AND att1.attrelid = cl1.oid
                AND cl2.relname = %s
                AND att2.attname = 'id'
                AND array_lower(con.confkey, 1) = 1
                AND con.confkey[1] = att2.attnum
                AND att2.attrelid = cl2.oid
                AND con.contype = 'f'
        """
        self._cr.execute(query, (table,))
        return self._cr.fetchall()

    @api.model
    def _update_foreign_keys(self, src_partners, dst_partner):
        """ Update all foreign key from the src_partner to dst_partner. All many2one fields will be updated.
            :param src_partners : merge source res.partner recordset (does not include destination one)
            :param dst_partner : record of destination res.partner
        """

        # find the many2one relation to a partner
        # Partner = self.env['res.partner']
        relations = self._get_fk_on('stock_production_lot')

        self.flush()

        for table, column in relations:
            if 'base_partner_merge_' in table:  # ignore two tables
                continue

            # get list of columns of current table (exept the current fk column)
            query = "SELECT column_name FROM information_schema.columns WHERE table_name LIKE '%s'" % (table)
            self._cr.execute(query, ())
            columns = []
            for data in self._cr.fetchall():
                if data[0] != column:
                    columns.append(data[0])

            # do the update for the current table/column in SQL
            query_dic = {
                'table': table,
                'column': column,
                'value': columns[0],
            }
            if len(columns) <= 1:
                # unique key treated
                query = """
                            UPDATE "%(table)s" as ___tu
                            SET "%(column)s" = %%s
                            WHERE
                                "%(column)s" = %%s AND
                                NOT EXISTS (
                                    SELECT 1
                                    FROM "%(table)s" as ___tw
                                    WHERE
                                        "%(column)s" = %%s AND
                                        ___tu.%(value)s = ___tw.%(value)s
                                )""" % query_dic
                for partner in src_partners:
                    self._cr.execute(query, (dst_partner.id, partner.id, dst_partner.id))
            else:
                try:
                    with mute_logger('odoo.sql_db'), self._cr.savepoint():
                        query = 'UPDATE "%(table)s" SET "%(column)s" = %%s WHERE "%(column)s" IN %%s' % query_dic
                        self._cr.execute(query, (dst_partner.id, tuple(src_partners.ids),))

                        # handle the recursivity with parent relation
                        # if column == Partner._parent_name and table == 'res_partner':
                        #     query = """
                        #             WITH RECURSIVE cycle(id, parent_id) AS (
                        #                     SELECT id, parent_id FROM res_partner
                        #                 UNION
                        #                     SELECT  cycle.id, res_partner.parent_id
                        #                     FROM    res_partner, cycle
                        #                     WHERE   res_partner.id = cycle.parent_id AND
                        #                             cycle.id != cycle.parent_id
                        #             )
                        #             SELECT id FROM cycle WHERE id = parent_id AND id = %s
                        #         """
                        #     self._cr.execute(query, (dst_partner.id,))
                        #     # NOTE JEM : shouldn't we fetch the data ?
                except psycopg2.Error:
                    # updating fails, most likely due to a violated unique constraint
                    # keeping record with nonexistent partner_id is useless, better delete it
                    query = 'DELETE FROM "%(table)s" WHERE "%(column)s" IN %%s' % query_dic
                    self._cr.execute(query, (tuple(src_partners.ids),))

        self.invalidate_cache()

    @api.model
    def _update_reference_fields(self, src_partners, dst_partner):
        """ Update all reference fields from the src_partner to dst_partner.
            :param src_partners : merge source res.partner recordset (does not include destination one)
            :param dst_partner : record of destination res.partner
        """

        def update_records(model, src, field_model='model', field_id='res_id'):
            Model = self.env[model] if model in self.env else None
            if Model is None:
                return
            records = Model.sudo().search([(field_model, '=', 'stock.production.lot'), (field_id, '=', src.id)])
            try:
                with mute_logger('odoo.sql_db'), self._cr.savepoint():
                    records.sudo().write({field_id: dst_partner.id})
                    records.flush()
            except psycopg2.Error:
                # updating fails, most likely due to a violated unique constraint
                # keeping record with nonexistent partner_id is useless, better delete it
                records.sudo().unlink()

        update_records = functools.partial(update_records)

        for partner in src_partners:
            update_records('calendar', src=partner, field_model='model_id.model')
            update_records('ir.attachment', src=partner, field_model='res_model')
            update_records('mail.followers', src=partner, field_model='res_model')
            update_records('mail.activity', src=partner, field_model='res_model')
            update_records('mail.message', src=partner)
            update_records('ir.model.data', src=partner)

        records = self.env['ir.model.fields'].sudo().search([('ttype', '=', 'reference')])
        for record in records:
            try:
                Model = self.env[record.model]
                field = Model._fields[record.name]
            except KeyError:
                # unknown model or field => skip
                continue

            if field.compute is not None:
                continue

            for partner in src_partners:
                records_ref = Model.sudo().search([(record.name, '=', 'stock.production.lot,%d' % partner.id)])
                values = {
                    record.name: 'stock.production.lot,%d' % dst_partner.id,
                }
                records_ref.sudo().write(values)

        self.flush()

    def _merge(self, partner_ids, dst_partner=None, lot_name=None):
        Partner = self.env['stock.production.lot']
        # Partner = self.env
        partner_ids = Partner.browse(partner_ids.ids).exists()
        if len(partner_ids) < 2:
            return

        partner_ids.sorted(lambda p: p.create_date)
        if dst_partner and dst_partner in partner_ids:
            src_partners = partner_ids - dst_partner
        else:
            dst_partner = partner_ids[0]
            src_partners = partner_ids[1:]

        self._update_foreign_keys(src_partners, dst_partner)
        self._update_reference_fields(src_partners, dst_partner)

        src_partners.unlink()
        if lot_name:
            dst_partner.name = lot_name

    # ========================== End of Function
