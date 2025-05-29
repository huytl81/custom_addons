# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.http import request
from odoo import http


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_user(cls):
        maintenance_mode = request.env['ir.config_parameter'].sudo().get_param('hspl.maintenance_mode', False)
        maintainer_user_ids = request.env.ref('base.group_system').sudo().users.ids
        is_maintainer = True if request.session.uid in maintainer_user_ids else False
        request.uid = request.session.uid
        if bool(maintenance_mode) and not is_maintainer:
            raise http.SessionExpiredException("Session expired")
        if not request.uid:
            raise http.SessionExpiredException("Session expired")
