# -*- coding: utf-8 -*-

from odoo import models, fields, api


class UserAppDevice(models.Model):
    _name = 'vtt.user.app.device'
    _description = 'Firebase device id (token) for User'

    name = fields.Char('Name')
    user_id = fields.Many2one('res.users', 'User')
    fcm_token = fields.Char('Firebase messaging token')