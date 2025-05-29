# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ThreatCampaign(models.Model):
    _name = 'investigate.campaign'
    _inherit = ['investigate.campaign', 'threat.sync.mixin']