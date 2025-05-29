# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    vtt_anniversary_user_id = fields.Many2one('res.users', 'Default User')