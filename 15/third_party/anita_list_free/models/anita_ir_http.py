# -*- coding: utf-8 -*-

import base64
import hashlib
import json

import odoo
from odoo import api, http, models
from odoo.http import request


class AnitaHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super(AnitaHttp, self).session_info()
        # global or local
        session_info['anita_list_mode'] = request.env[
            'ir.config_parameter'].sudo().get_param('anita_list_free.mode', 'global')
        return session_info
