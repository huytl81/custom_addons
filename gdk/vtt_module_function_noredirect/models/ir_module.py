# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrModule(models.Model):
    _inherit = 'ir.module.module'

    def _button_immediate_function(self, function):
        res = super(IrModule, self)._button_immediate_function(function)
        # env = api.Environment(self._cr, self._uid, self._context)
        # menu = env['ir.ui.menu'].search([('parent_id', '=', False)])[:1]
        # alt_res = {k: v for k, v in res.items() if k != 'params'}
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            # 'params': {'menu_id': menu.id},
        }