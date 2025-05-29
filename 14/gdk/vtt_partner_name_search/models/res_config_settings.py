# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vtt_contact_name_search_fields = fields.Char('Name Search Fields', help='Fields used to quick search a Partner, separate by comma (",")')
    vtt_contact_name_get_fields = fields.Char('Name Get Fields', help='Addition information, separate by comma (",")')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['vtt_contact_name_search_fields'] = self.env['ir.config_parameter'].sudo().get_param('vtt_partner_name_search.vtt_contact_name_search_fields', default='')
        res['vtt_contact_name_get_fields'] = self.env['ir.config_parameter'].sudo().get_param('vtt_partner_name_search.vtt_contact_name_get_fields', default='')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('vtt_partner_name_search.vtt_contact_name_search_fields', self.vtt_contact_name_search_fields)
        self.env['ir.config_parameter'].sudo().set_param('vtt_partner_name_search.vtt_contact_name_get_fields', self.vtt_contact_name_get_fields)
        super(ResConfigSettings, self).set_values()