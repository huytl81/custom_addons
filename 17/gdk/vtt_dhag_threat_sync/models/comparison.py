# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ThreatComparison(models.Model):
    _name = 'threat.comparison'
    _inherit = ['threat.comparison', 'threat.sync.mixin']
