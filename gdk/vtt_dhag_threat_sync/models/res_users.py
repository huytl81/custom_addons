# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'threat.sync.mixin']