# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttConstructItem(models.Model):
    _name = 'vtt.construct.item'
    _description = 'Construct Item'

    name = fields.Char('Name')

    construct_id = fields.Many2one('vtt.construct', 'Construction')

    description = fields.Text('Description')

    dt_plan = fields.Datetime('Plan Time')
    dt_done = fields.Datetime('Done Time')

    state = fields.Selection([
        ('plan', 'Plan'),
        ('progress', 'Progress'),
        ('done', 'Done')
    ], 'State', default='plan')