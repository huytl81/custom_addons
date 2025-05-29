# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    # repair_order_id = fields.Many2one('vtt.repair.order', 'Repair Order')
    repair_line_id = fields.Many2one('vtt.repair.order.line', 'Repair Line', index='btree_not_null')

    # def _get_source_document(self):
    #     return self.repair_order_id or super()._get_source_document()