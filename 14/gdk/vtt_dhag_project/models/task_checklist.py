# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttTaskChecklist(models.Model):
    _name = 'vtt.task.checklist'
    _description = 'Project Task Checklist'

    name = fields.Char('Name', required=True)
    line_ids = fields.One2many('vtt.checklist.line', 'checklist_id', 'Checklist')


class VttTaskChecklistLine(models.Model):
    _name = 'vtt.checklist.line'
    _description = 'Project Task Checklist Line'
    _order = 'sequence, id desc'

    name = fields.Char('Name', required=True)
    checklist_id = fields.Many2one('vtt.task.checklist', 'Checklist')

    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)