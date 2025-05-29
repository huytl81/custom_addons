# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from . import analysis_tools


class ThreatComparisonTemplate(models.Model):
    _name = 'threat.comparison.template'
    _inherit = ['threat.comparison.template', 'threat.sync.mixin']


class ThreatComparisonTemplateField(models.Model):
    _name = 'threat.comparison.template.field'
    _inherit = ['threat.comparison.template.field', 'threat.sync.mixin']
