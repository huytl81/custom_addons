# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_vtt_default_task_types(self):
        xml_ids = [
            'vtt_minhduong_config.vtt_data_project_task_type_todo',
            'vtt_minhduong_config.vtt_data_project_task_type_progress',
            'vtt_minhduong_config.vtt_data_project_task_type_done',
            'vtt_minhduong_config.vtt_data_project_task_type_cancel',
        ]
        type_ids = [self.env.ref(t).id for t in xml_ids]
        return type_ids

    @api.model
    def create(self, vals):
        type_ids = vals.get('type_ids', [])
        type_ids += [(4, t_id) for t_id in self._get_vtt_default_task_types()]
        vals['type_ids'] = type_ids
        return super().create(vals)