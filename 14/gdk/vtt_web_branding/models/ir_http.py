# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        params = request.env['ir.config_parameter'].sudo()
        page_title = params.get_param('vtt_web_branding.page_title', default='')
        page_documentation = params.get_param('vtt_web_branding.page_documentation', default='')
        page_support = params.get_param('vtt_web_branding.page_support', default='')
        result['vtt_page_title'] = page_title
        result.update({
            'vtt_page_title': page_title,
            'vtt_page_documentation': page_documentation,
            'vtt_page_support': page_support
        })
        return result