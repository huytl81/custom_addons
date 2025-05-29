# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InvestigateCampaign(models.Model):
    _inherit = 'investigate.campaign'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.investigate.campaign')
        return super(InvestigateCampaign, self).create(vals)