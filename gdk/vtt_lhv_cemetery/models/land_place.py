# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttLandPlace(models.Model):
    _name = 'vtt.land.place'
    _description = 'Land Place'
    _order = 'sequence'

    name = fields.Char('Name')
    description = fields.Text('Description')

    sequence = fields.Integer('Sequence', default=10)