# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _


class VttCarRepairReport(models.Model):
    _name = 'vtt.car.repair.order.report'
    _description = 'Car Repair Order Report'
    _order = 'dt_receive desc'
    _auto = False

    name = fields.Char('Order Reference', readonly=True)

    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    product_uom_qty = fields.Float('Qty Ordered', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)

    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    # partner_phone = fields.Char('Customer Phone', readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', readonly=True)
    vehicle_brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Brand', readonly=True)
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', 'Model', readonly=True)
    # vehicle_license_plate = fields.Char('License Plate', readonly=True)

    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    price_total = fields.Float('Total', readonly=True)
    # price_tax = fields.Float('Taxed Amount', readonly=True)
    price_subtotal = fields.Float('Untaxed Total', readonly=True)
    # price_unit = fields.Float('Unit Price', readonly=True)
    discount = fields.Float('Discount %', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)

    nbr = fields.Integer('# of Lines', readonly=True)
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('under_repair', 'Under Repair'),
        ('repaired', 'Repaired'),
        ('done', 'Repaired'),
        ('cancel', 'Cancelled')], string='Status', readonly=True)
    order_id = fields.Many2one('vtt.car.repair.order', 'Order #', readonly=True)

    dt_receive = fields.Datetime('Receive Date', readonly=True)
    dt_confirmed = fields.Datetime('Confirmed Date', readonly=True)
    # dt_start_repair = fields.Datetime('Start Repair', readonly=True)
    # dt_end_repair = fields.Datetime('End Repair', readonly=True)

    # total_repair_time = fields.Float('Total Repair Time', readonly=True)

    receive_user_id = fields.Many2one('res.users', 'Receiver', readonly=True)
    technical_user_id = fields.Many2one('res.users', 'Technical', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        # with_ = ("WITH %s" % with_clause) if with_clause else ""
        with_ = ""

        select_ = """
            coalesce(min(l.id), -s.id) as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END as product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_subtotal / 1.0) ELSE 0 END as price_subtotal,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_total / 1.0) ELSE 0 END as price_total,
            count(*) as nbr,
            s.name as name,
            s.dt_receive as dt_receive,
            s.dt_confirmed as dt_confirmed,
            s.state as state,
            s.partner_id as partner_id,
            s.receive_user_id as receive_user_id,
            s.technical_user_id as technical_user_id,
            s.company_id as company_id,
            s.vehicle_id as vehicle_id,
            v.brand_id as vehicle_brand_id,
            v.model_id as vehicle_model_id,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            p.product_tmpl_id,
            l.discount as discount,
            s.id as order_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                vtt_car_repair_order_line l
                      right outer join vtt_car_repair_order s on (s.id=l.repair_id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                        left join fleet_vehicle v on s.vehicle_id = v.id
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause

        groupby_ = """
            s.vehicle_id,
            l.product_id,
            l.repair_id,
            t.uom_id,
            t.categ_id,
            s.name,
            s.dt_receive,
            s.dt_confirmed,
            s.partner_id,
            s.receive_user_id,
            s.technical_user_id,
            s.state,
            s.company_id,
            s.pricelist_id,
            p.product_tmpl_id,
            v.brand_id,
            v.model_id,
            l.discount,
            s.id %s
        """ % (groupby)

        return '%sSELECT %s FROM %s GROUP BY %s' % (with_, select_, from_, groupby_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as %s""" % (self._table, self._query()))