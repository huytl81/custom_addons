# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ResUser(models.Model):
    _inherit = 'res.users'

    device_ids = fields.One2many('vtt.user.app.device', 'user_id', 'Devices')