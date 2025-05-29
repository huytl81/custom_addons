# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ViewCustom(models.Model):
    _inherit = 'ir.ui.view.custom'
    _order = 'vtt_is_global desc, create_date desc'

    vtt_is_global = fields.Boolean('Is Global?', default=False)