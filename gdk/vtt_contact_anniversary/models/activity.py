# -*- coding: utf-8 -*-

from odoo import models, fields


class MailActivity(models.Model):
    _inherit = "mail.activity"

    anniversary_id = fields.Many2one('vtt.contact.anniversary', string="Anniversary", ondelete='cascade')
