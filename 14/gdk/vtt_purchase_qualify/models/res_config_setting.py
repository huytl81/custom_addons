# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vtt_po_responsible_method = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Full automatic')
    ], string='Responsible Method',
        help="* The \'Manual\' mean all responsible in order need to fill manually.\n"
             "* The \'Full automatic\' is used when all responsible have to fill-up by workflow action.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['vtt_po_responsible_method'] = self.env['ir.config_parameter'].sudo().get_param('vtt_purchase_qualify.po_responsible_method', default='manual')

        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('vtt_purchase_qualify.po_responsible_method', self.vtt_po_responsible_method)

        super(ResConfigSettings, self).set_values()