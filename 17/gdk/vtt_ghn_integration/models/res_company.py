# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    district_id = fields.Many2one('res.district', store=True, string='District', domain="[('state_id', '=', state_id)]")
    ward_id = fields.Many2one('res.ward', store=True, string='Ward', domain="[('district_id', '=', district_id)]")

    # @api.onchange('district_id')
    # def onchange_district_id(self):
    #     self.city = self.district_id.name