# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Board(models.AbstractModel):
    _inherit = 'board.board'

    def get_global_view_domain(self, view_id):
        domain = super(Board, self).get_global_view_domain(view_id)
        user = self.env.user
        domain += [('vtt_department_id', '=', user.department_id.id)]
        return domain