# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'threat.sync.mixin']
    # _inherit = 'res.partner'
    #
    # s_id = fields.Integer('Server ID')