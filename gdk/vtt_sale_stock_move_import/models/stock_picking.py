# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    vtt_special_import = fields.Boolean('Special Import Picking', default=False)

    def open_move_import_wz(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Move Import'),
            'view_mode': 'form',
            'res_model': 'vtt.stock.move.import.wz',
            'target': 'new',
            'context': {'default_stock_picking_id': self.id}
        }