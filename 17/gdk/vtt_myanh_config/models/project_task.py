# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['project.task', 'hierarchy.mixin']

    reason_type_id = fields.Many2one('vtt.project.task.reason.type', 'Reason Type')
    reason = fields.Char('Reason')
    reason_detail_need = fields.Boolean(related='reason_type_id.detail_need')

    hierarchy_sequence = fields.Char('Hierarchy Sequence', compute='_compute_hierarchy_sequence', precompute=True, store=True,)

    @api.depends('parent_id', 'sequence', 'hierarchy_level')
    def _compute_hierarchy_sequence(self):
        for t in self:
            seq = f'{t.hierarchy_level}_{t.sequence}_{t.id}'
            if t.parent_id:
                t.hierarchy_sequence = f'{t.parent_id.hierarchy_sequence}__{seq}'
            else:
                t.hierarchy_sequence = seq

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProjectTask, self).create(vals_list)
        res._compute_hierarchy_sequence()
        return res

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        if 'stage_id' in vals and self.child_ids:
            self.child_ids.stage_id = vals['stage_id']
        return res

    def action_dup_2_project(self):
        # ids = self._context.get('active_ids', [])
        ids = self.ids
        return {
            'name': _('Task Duplicate Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'vtt.project.task.duplicate.wz',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_ids': ids,
                'task_ids': ids,
            },
        }