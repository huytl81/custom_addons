# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_compare_alternative_lines(self):
        res = super(PurchaseOrder, self).action_compare_alternative_lines()
        res['context'].update({
            'search_default_groupby_product': False,
            'search_default_order_reference': True,
        })
        return res