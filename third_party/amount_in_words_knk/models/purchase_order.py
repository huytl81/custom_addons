# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _compute_amount_to_words(self):
        for po in self:
                po.amount_words = str(po.currency_id.amount_to_text(po.amount_total))

    amount_words = fields.Char(string="Total(In words): ", compute='_compute_amount_to_words')
