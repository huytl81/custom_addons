# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuantityHistory(models.TransientModel):
    _inherit = 'stock.quantity.history'

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')

    def open_at_date(self):
        action = super(StockQuantityHistory, self).open_at_date()
        if self.warehouse_id:
            action['context'].update({
                'warehouse': self.warehouse_id.id
            })
        return action