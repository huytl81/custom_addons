# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    land_plot_id = fields.Many2one('vtt.land.plot', 'Plot')
    land_contract_id = fields.Many2one('vtt.land.contract', 'Land Contract')

    def _prepare_renewal_order_values(self, discard_product_ids=False, new_lines_ids=False):
        res = super(SaleSubscription, self)._prepare_renewal_order_values(discard_product_ids, new_lines_ids)
        for subscription in self:
            res[subscription.id]['land_contract_id'] = subscription.land_contract_id.id
        return res