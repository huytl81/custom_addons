# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, tools


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _default_favicon(self):
        with tools.file_open('vtt_base_setup/static/img/favicon.png', 'rb') as f:
            return base64.b64encode(f.read())

    favicon = fields.Binary(string="Company Favicon",
                            help="This field holds the image used to display a favicon on tab.",
                            default=_default_favicon)

    brand_title = fields.Char('Brand Title', help='Company Browser Brand Title')