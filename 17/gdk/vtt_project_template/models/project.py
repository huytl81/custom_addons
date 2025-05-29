# -*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo import Command


class Project(models.Model):
    _inherit = 'project.project'

    @api.model_create_multi
    def create(self, vals_list):
        context = self._context.copy()
        projects = super().create(vals_list)

        # if context.get('project_template_id', False):
        #     project_template = self.env['vtt.project.template'].browse(context.get('project_template_id', False))

        project_template = self.env['vtt.project.template'].browse(context.get('project_template_id', False))
        if project_template:
            # Task Types
            task_types = project_template.mapped('type_ids')
            for t in task_types:
                t.write({'project_ids': [Command.link(p.id) for p in projects]})

            for p in projects:
                task_vals = project_template._get_task_vals(p.id)
                p.write({'tasks': task_vals})

        return projects