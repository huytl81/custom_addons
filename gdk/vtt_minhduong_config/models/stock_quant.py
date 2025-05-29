# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    vtt_expiration_date = fields.Datetime('Expiration Date', related='lot_id.expiration_date', store=True, readonly=True)
    vtt_use_date = fields.Datetime('Use Date', related='lot_id.use_date', store=True, readonly=True)
    vtt_current_expiration_percentage = fields.Float('Current % Expiration', compute='_compute_expiration_percentage')
    vtt_is_expired = fields.Boolean('Is Expired?', related='lot_id.vtt_is_expired', store=True, readonly=True)

    vtt_tag_ids = fields.Many2many('vtt.product.tag', string='Tags', compute='_compute_product_tags', store=True)

    product_default_code = fields.Char('Product Default Code', related='product_id.default_code')
    product_name = fields.Char('Product Name', related='product_id.name')

    location_sequence = fields.Integer('Sequence', related='location_id.sequence', store=True)

    pack_barcode = fields.Char('Packing Barcode', related='product_id.pack_barcode', store=True)
    product_barcode = fields.Char('Product Barcode', related='product_id.product_barcode', store=True)

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == 'fifo':
            return 'in_date ASC, location_sequence, id'
        elif removal_strategy == 'lifo':
            return 'in_date DESC, location_sequence, id DESC'
        elif removal_strategy == 'closest':
            return 'location_id ASC, id DESC'
        elif removal_strategy == 'fefo':
            return 'removal_date, location_sequence, in_date, id'
        raise UserError(_('Removal strategy %s not implemented.') % (removal_strategy,))
        # return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)

    @api.depends('product_id', 'product_id.vtt_tag_ids')
    def _compute_product_tags(self):
        for q in self:
            q.vtt_tag_ids = q.product_id.vtt_tag_ids.ids

    def _compute_expiration_percentage(self):
        date = datetime.now()
        for q in self:
            cur_perc = 100
            if q.vtt_expiration_date:
                if not q.product_id.vtt_use_production_date:
                    product_expiration_time = q.product_id.expiration_time
                elif q.product_id.vtt_use_production_date and q.lot_id.vtt_production_date:
                    production_date = fields.Datetime.to_datetime(q.lot_id.vtt_production_date)
                    product_expiration_time = (q.vtt_expiration_date - production_date).days
                else:
                    product_expiration_time = (q.vtt_expiration_date - q.lot_id.create_date).days

                date_diff = (q.vtt_expiration_date - date).days

                if product_expiration_time:
                    date_diff_percentage = date_diff / product_expiration_time * 100
                    cur_perc = date_diff_percentage

            q.vtt_current_expiration_percentage = cur_perc

    def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
        res = super(StockQuant, self)._gather(product_id, location_id, lot_id, package_id, owner_id, strict)
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        context = self.env.context
        check_block_expired = context.get('vtt_block_expired_lot', False)
        # removal_strategy_order = self._get_removal_strategy_order(removal_strategy)
        if removal_strategy == 'fefo' and check_block_expired:
            res = res.filtered(lambda q: not q.lot_id.vtt_is_expired)
        return res

    def action_multi_apply_inventory_by_sv(self):
        quants = self.filtered(lambda q: q.inventory_quantity)
        quants.action_apply_inventory()
