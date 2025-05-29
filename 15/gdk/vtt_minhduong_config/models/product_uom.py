# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class UoM(models.Model):
    _inherit = 'uom.uom'

    vtt_uom_code = fields.Char('UoM Code')

    _sql_constraints = [
        ('unique_uom_code', 'UNIQUE(vtt_uom_code)', 'One UoM should only have one UoM Code.')
    ]