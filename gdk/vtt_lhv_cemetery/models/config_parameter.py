# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    description = fields.Char('Description', translate=True)
    show_manager = fields.Boolean('Show for Manager?', default=False)