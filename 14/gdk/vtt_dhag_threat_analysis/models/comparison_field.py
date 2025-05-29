# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from . import analysis_tools


class ThreatComparisonField(models.Model):
    _name = 'threat.comparison.field'
    _description = 'Threat Comparison Field'
    _inherit = ['threat.sync.mixin']

    compare_id = fields.Many2one('threat.comparison', 'Comparison')
    type = fields.Selection(related='compare_id.type')

    field_id = fields.Many2one('ir.model.fields', 'Field')

    description = fields.Char('Description')

    ss_code = fields.Char('Secret Sequence', copy=False)
