# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from . import analysis_tools


class InvestigateInvestigate(models.Model):
    _name = 'investigate.investigate'
    _inherit = ['investigate.investigate', 'threat.sync.mixin']


class InvestigateDepartmentSuggest(models.Model):
    _name = 'investigate.department.suggest'
    _inherit = ['investigate.department.suggest', 'threat.sync.mixin']