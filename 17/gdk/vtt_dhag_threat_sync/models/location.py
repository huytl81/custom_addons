# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression
# from . import analysis_tools


class InvestigateLocation(models.Model):
    _name = 'investigate.location'
    _inherit = ['investigate.location', 'threat.sync.mixin']