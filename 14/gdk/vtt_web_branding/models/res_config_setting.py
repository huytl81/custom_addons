# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vtt_page_title = fields.Char('Page Title', help='Branding page Title')
    vtt_page_documentation = fields.Char('Documentation', help='Documentation Link')
    vtt_page_support = fields.Char('Suport', help='Support Link')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['vtt_page_title'] = self.env['ir.config_parameter'].sudo().get_param('vtt_web_branding.page_title', default='')
        res['vtt_page_documentation'] = self.env['ir.config_parameter'].sudo().get_param('vtt_web_branding.page_documentation', default='')
        res['vtt_page_support'] = self.env['ir.config_parameter'].sudo().get_param('vtt_web_branding.page_support', default='')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('vtt_web_branding.page_title', self.vtt_page_title)
        self.env['ir.config_parameter'].sudo().set_param('vtt_web_branding.page_documentation', self.vtt_page_documentation)
        self.env['ir.config_parameter'].sudo().set_param('vtt_web_branding.page_support', self.vtt_page_support)

        super(ResConfigSettings, self).set_values()