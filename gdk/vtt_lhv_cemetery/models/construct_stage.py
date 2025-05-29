# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttConstructStage(models.Model):
    _name = 'vtt.construct.stage'
    _description = 'Construction Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', translate=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=1)

    fold = fields.Boolean(string='Folded in Kanban')
    is_closed = fields.Boolean('Closing Stage')

    stage_type = fields.Selection([
        ('design', 'Designing'),
        ('construct', 'Construction')
    ], 'Stage Type', default='design', required=True)