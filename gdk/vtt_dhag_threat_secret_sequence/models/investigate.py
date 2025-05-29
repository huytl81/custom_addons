# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InvestigateInvestigate(models.Model):
    _inherit = 'investigate.investigate'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.investigate.investigate')
        return super(InvestigateInvestigate, self).create(vals)