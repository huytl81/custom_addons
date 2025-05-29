# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models


class Account(models.Model):
    _inherit = 'account.move'

    def _compute_amount_to_words(self):
        for move in self:
                move.amount_words = str(move.currency_id.amount_to_text(move.amount_total))

    amount_words = fields.Char(string="Total(In words): ", compute='_compute_amount_to_words')
