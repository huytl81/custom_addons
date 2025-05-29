# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def action_stock_custom_import_wz(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Import From EXCEL'),
            'res_model': 'vtt.stock.custom.import.wz',
            # 'views': [[self.env.ref('mrp_workorder.view_mrp_workorder_additional_product_wizard').id, 'form']],
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_type': self.code,
                'default_picking_type_id': self.id
            }
        }