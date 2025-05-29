# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    vtt_task_id = fields.Many2one('project.task', 'Task')

    vtt_approved_user_ids = fields.Many2many('res.users', string='Approved Users', compute='_compute_approved_users')

    def _compute_approved_users(self):
        for ar in self:
            ar.vtt_approved_user_ids = ar.approver_ids.filtered(lambda ap: ap.status == 'approved').user_id