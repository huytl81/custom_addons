# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    vtt_warehouse_code = fields.Char('Warehouse Code')

    _sql_constraints = [
        ('unique_warehouse_code', 'UNIQUE(vtt_warehouse_code)', 'One Warehouse should only have one Warehouse Code.')
    ]

    def _get_picking_type_create_values(self, max_sequence):
        res = super()._get_picking_type_create_values(max_sequence)
        # res['in_type_id']['show_operations'] = True
        return res