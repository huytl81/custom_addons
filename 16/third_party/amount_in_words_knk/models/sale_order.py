# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_amount_to_words(self):
        for order in self:
                order.amount_words = str(order.currency_id.amount_to_text(order.amount_total))

    amount_words = fields.Char(string="Total(In words):", compute='_compute_amount_to_words')
