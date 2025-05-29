# -*- coding: utf-8 -*-

from odoo import models, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def custom_import_moves(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Import From EXCEL'),
            'res_model': 'vtt.stock.picking.move.import.wz',
            # 'views': [[self.env.ref('mrp_workorder.view_mrp_workorder_additional_product_wizard').id, 'form']],
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_picking_id': self.id,
            }
        }