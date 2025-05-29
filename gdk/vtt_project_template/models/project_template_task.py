# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTemplateTask(models.Model):
    _name = 'vtt.project.template.task'
    _description = 'Project Template Task'

    project_template_id = fields.Many2one('vtt.project.template', 'Project Template')

    name = fields.Char('Name')
    description = fields.Html('Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], default='0', string="Priority")
    sequence = fields.Integer(string='Sequence', default=10)
    tag_ids = fields.Many2many('project.tags', string='Tags')

    parent_id = fields.Many2one('vtt.project.template.task', string='Parent Task',
                                domain="['!', ('id', 'child_of', id)]")
    child_ids = fields.One2many('vtt.project.template.task', 'parent_id', string="Sub-tasks")

    def _get_task_vals(self, project_id):
        self.ensure_one()
        vals = {
            'name': self.name,
            'description': self.description,
            'priority': self.priority,
            'sequence': self.sequence,
            'tag_ids': self.tag_ids.ids,
            'project_id': project_id,
        }
        if self.child_ids:
            vals['child_ids'] = [c._get_task_vals(project_id) for c in self.child_ids]
        return [0, 0, vals]