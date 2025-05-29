# -*- coding: utf-8 -*-

from odoo import exceptions, SUPERUSER_ID
from odoo.http import request, route, Controller


class Main(Controller):

    @route('/web/client/user-documentation', auth="user", website=True)
    def client_user_documentation(self, **kwargs):
        # return request.env['res.partner'].action_open_user_document()
        action = request.env.ref("vtt_minhduong_config.vtt_act_window_ir_attachment_user_document")
        return request.redirect('/web?#&view_type=list&model=ir.attachment&action=%s' % action.id)