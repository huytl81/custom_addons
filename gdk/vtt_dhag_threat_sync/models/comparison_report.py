# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from . import analysis_tools


class ThreatComparisonReport(models.Model):
    _name = 'threat.comparison.report'
    _inherit = ['threat.comparison.report', 'threat.sync.mixin']

