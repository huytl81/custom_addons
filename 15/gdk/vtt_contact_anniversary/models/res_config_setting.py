# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vtt_anniversary_activity_interval = fields.Integer('Days to Anniversary', default='7')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['vtt_anniversary_activity_interval'] = self.env['ir.config_parameter'].sudo().get_param('vtt_contact_anniversary.anniversary_activity_interval', default='7')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('vtt_contact_anniversary.anniversary_activity_interval', self.vtt_anniversary_activity_interval)

        super(ResConfigSettings, self).set_values()