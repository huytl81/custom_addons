# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTemplate(models.Model):
    _name = 'vtt.project.template'
    _description = 'Project Template'

    def _get_default_task_types(self):
        task_type_default_id = [
            'vtt_project_template.vtt_data_project_task_type_new',
            'vtt_project_template.vtt_data_project_task_type_progress',
            'vtt_project_template.vtt_data_project_task_type_done',
            'vtt_project_template.vtt_data_project_task_type_cancel',
        ]
        task_types = self.env['project.task.type']
        if self.env.ref(task_type_default_id[0], raise_if_not_found=False):
            for t in task_type_default_id:
                t_type = self.env.ref(t, raise_if_not_found=False)
                if t_type:
                    task_types |= t_type
        return task_types.ids

    name = fields.Char('Name')
    description = fields.Html('Description')

    privacy_visibility = fields.Selection([
        ('followers', 'Invited internal users (private)'),
        ('employees', 'All internal users'),
        ('portal', 'Invited portal users and all internal users (public)'),
    ],
        string='Visibility', required=True,
        default='portal',)

    tag_ids = fields.Many2many('project.tags', string='Tags')

    type_ids = fields.Many2many('project.task.type', string='Tasks Stages', default=_get_default_task_types)

    task_ids = fields.One2many('vtt.project.template.task', 'project_template_id', 'Tasks')

    def _get_project_vals(self, partner_id=False, sale_id=False):
        self.ensure_one()
        vals = {
            'name': self.name,
            'description': self.description,
            'privacy_visibility': self.privacy_visibility,
            'tag_ids': self.tag_ids.ids
        }
        if partner_id:
            vals['partner_id'] = partner_id.id
        if sale_id:
            vals['name'] = _('Project') + f' {sale_id.name}'

        return vals

    def _get_task_vals(self, project_id):
        self.ensure_one()
        tasks = self.task_ids.filtered(lambda t: not t.parent_id)
        vals = [t._get_task_vals(project_id) for t in tasks]
        return vals

    def get_project(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("project.open_view_project_all")
        project_vals = self._get_project_vals()
        context = {
            'default_name': project_vals['name'],
            'default_description': project_vals['description'],
            'default_privacy_visibility': project_vals['privacy_visibility'],
            'default_tag_ids': project_vals['tag_ids'],
            'project_template_id': self.id,
        }
        action['context'] = context
        action['res_id'] = False
        action['view_mode'] = 'form'
        action['views'] = [[False, 'form']]

        return action

    def project_from_template(self, partner_id=False, sale_id=False):
        self.ensure_one()
        project_vals = self._get_project_vals(partner_id, sale_id)
        new_project = self.env['project.project'].with_context(project_template_id=self.id).create(project_vals)
        return new_project