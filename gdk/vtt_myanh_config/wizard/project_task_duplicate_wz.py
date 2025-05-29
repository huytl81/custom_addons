# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectTaskDuplicateWizard(models.TransientModel):
    _name = 'vtt.project.task.duplicate.wz'
    _description = 'Task Duplicate Wizard'

    task_ids = fields.Many2many('project.task', string='Tasks')
    project_ids = fields.Many2many('project.project', 'Projects')

    keep_assign = fields.Boolean('Keep Assign?')

    def dup_task_2_project(self):
        if self.task_ids and self.project_ids:
            task_vals = []
            for t in self.task_ids:
                t_vals = {
                    'name': t.name,
                    'tag_ids': t.tag_ids.ids
                }
                if self.keep_assign:
                    t_vals['user_ids'] = t.user_ids.ids
                else:
                    t_vals['user_ids'] = []
                task_vals.append(t_vals)

            task_all_vals = []
            for task in task_vals:
                for project in self.project_ids:
                    task_cop = task.copy()
                    task_cop['project_id'] = project.id
                    task_all_vals.append(task_cop)

            self.env['project.task'].create(task_all_vals)