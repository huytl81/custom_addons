# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vtt_special_import_show = fields.Boolean('Special Import Picking', compute='_compute_special_import_show')

    def _compute_special_import_show(self):
        for so in self:
            sp = False
            if so.state in ['sale']:
                if not so.picking_ids.filtered(lambda p: p.vtt_special_import and p.state != 'cancel'):
                    sp = True
            so.vtt_special_import_show = sp

    def open_move_import_wz(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product Move Import'),
            'view_mode': 'form',
            'res_model': 'vtt.stock.move.import.wz',
            'target': 'new',
            'context': {'default_sale_order_id': self.id}
        }