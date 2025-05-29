# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vtt_car_repair_notes = fields.Text('Quotation Notes', help='Default Quotation Notes')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['vtt_car_repair_notes'] = self.env['ir.config_parameter'].sudo().get_param('vtt_car_repair.order_notes', default='')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('vtt_car_repair.order_notes', self.vtt_car_repair_notes)

        super(ResConfigSettings, self).set_values()