# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttUserCopyBoardWizard(models.TransientModel):
    _name = 'vtt.user.copy.board.wz'
    _description = 'User Copy Board Wizard'

    def _get_default_users(self):
        res = self.env['res.users'].browse(self._context['active_ids'])
        return res

    user_id = fields.Many2one('res.users', 'User')
    user_ids = fields.Many2many('res.users', string='Copy to', default=_get_default_users)
    board_view_id = fields.Integer('View ID')

    def do_copy_board(self):
        view_id = self.env.ref('board.board_my_dash_view').id
        # view_id = self.board_view_id
        board = self.env['ir.ui.view.custom'].search([
            ('user_id', '=', self.user_id.id),
            ('ref_id', '=', view_id)
        ], limit=1)
        old_uid = "'uid': %s" % str(self.user_id.id)
        if board and self.user_ids:
            vals = []
            for u in self.user_ids:
                new_uid = "'uid': %s" % str(u.id)
                new_arch = board.arch.replace(old_uid, new_uid)
                vals.append({
                    'user_id': u.id,
                    'ref_id': view_id,
                    'arch': new_arch,
                })
            return self.env['ir.ui.view.custom'].sudo().create(vals)