# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from . import analysis_tools


class ThreatComparisonTemplate(models.Model):
    _name = 'threat.comparison.template'
    _description = 'Comparison Template'
    _inherit = ['threat.sync.mixin']

    name = fields.Char('Name', required=True)
    type = fields.Selection([
        ('threat.malware', 'Malware'),
        ('investigate.investigate', 'Investigate'),
    ], 'Type', default='threat.malware', required=True)
    compare_field_ids = fields.One2many('threat.comparison.template.field', 'compare_template_id', 'Fields')

    ss_code = fields.Char('Secret Sequence', copy=False)


class ThreatComparisonTemplateField(models.Model):
    _name = 'threat.comparison.template.field'
    _description = 'Comparison Template Field'
    _inherit = ['threat.sync.mixin']

    field_id = fields.Many2one('ir.model.fields', 'Field')

    compare_template_id = fields.Many2one('threat.comparison.template', 'Template')
    type = fields.Selection(related='compare_template_id.type')

    description = fields.Char('Description')

    ss_code = fields.Char('Secret Sequence', copy=False)
