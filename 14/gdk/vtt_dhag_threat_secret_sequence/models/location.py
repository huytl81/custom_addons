# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InvestigateLocation(models.Model):
    _inherit = 'investigate.location'

    @api.model
    def create(self, vals):
        if not vals.get('ss_code', False):
            vals['ss_code'] = self.env['ir.sequence'].next_by_code('ss.investigate.location')
        return super(InvestigateLocation, self).create(vals)