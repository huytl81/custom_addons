# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    checklist_id = fields.Many2one('vtt.task.checklist', 'Type of Task')
    checklist_line_ids = fields.One2many('vtt.task.checklist.line', 'task_id', 'Checklist')

    @api.onchange('checklist_id')
    def onchange_checklist(self):
        if self.checklist_id:
            if self.checklist_id.line_ids:
                lines = [(5, 0, 0)]
                for l in self.checklist_id.line_ids:
                    lines.append((0, 0, {
                        'name': l.name,
                        'sequence': l.sequence,
                        'task_id': self.id,
                    }))
                self.update({
                    'checklist_line_ids': lines
                })

    def save_checklist(self):
        if self.checklist_line_ids:
            if self.checklist_id:
                lines = [(5, 0, 0)]
                for l in self.checklist_line_ids:
                    lines.append((0, 0, {
                        'name': l.name,
                        'sequence': l.sequence,
                        'description': l.description,
                        'checklist_id': self.checklist_id.id,
                    }))
                self.checklist_id.write({
                    'line_ids': lines
                })
            else:
                checklist = self.env['vtt.task.checklist'].create({
                    'name': self.name,
                })
                self.write({
                    'checklist_id': checklist.id
                })
                lines = []
                for l in self.checklist_line_ids:
                    lines.append((0, 0, {
                        'name': l.name,
                        'sequence': l.sequence,
                        'description': l.description,
                        'checklist_id': checklist.id,
                    }))
                checklist.write({
                    'line_ids': lines
                })


class VttProjectTaskChecklistLine(models.Model):
    _name = 'vtt.task.checklist.line'
    _description = 'Project Task Checklist Line'
    _order = 'sequence, id desc'

    name = fields.Char('Name', required=True)
    task_id = fields.Many2one('project.task', 'Checklist')

    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)

    is_done = fields.Boolean('Done?', default=False)

    def set_done(self):

        self.task_id._message_log(body=_('<b>Set done:</b> %s') % self.name)

        return self.write({
            'is_done': True
        })

    def set_open(self):

        self.task_id._message_log(body=_('<b>Set open:</b> %s') % self.name)

        return self.write({
            'is_done': False
        })