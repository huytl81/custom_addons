# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from . import analysis_tools


class ThreatComparisonField(models.Model):
    _name = 'threat.comparison.field'
    _inherit = ['threat.comparison.field', 'threat.sync.mixin']
