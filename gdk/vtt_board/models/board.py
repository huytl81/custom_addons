# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Board(models.AbstractModel):
    _inherit = 'board.board'

    def get_global_view_domain(self, view_id):
        domain = [('vtt_is_global', '!=', False), ('ref_id', '=', view_id)]
        return domain

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Board, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        # Check Global view
        global_view = self.env['ir.ui.view.custom'].search(self.get_global_view_domain(view_id), limit=1)
        if global_view:
            old_uid = "'uid': %s" % str(global_view.user_id.id)
            new_uid = "'uid': %s" % str(self.env.user.id)
            arch = global_view.arch.replace(old_uid, new_uid)
            arch = self._arch_preprocessing(arch)
            res.update({
                'custom_view_id': global_view.id,
                'arch': arch
            })

        return res