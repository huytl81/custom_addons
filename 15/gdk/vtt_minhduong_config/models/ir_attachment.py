# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    vtt_user_document = fields.Boolean('Is User Document', default=False)