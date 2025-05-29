# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def update_price_by_display_qty(self):
        for line in self.order_line:
            line.onchange_display_qty()