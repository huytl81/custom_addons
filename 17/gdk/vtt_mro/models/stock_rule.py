# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['repair_line_id']
        return fields