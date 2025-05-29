# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    department_ids = fields.Many2many('hr.department', 'project_task_hr_department_rel', string='Departments')

    vtt_approval_request_ids = fields.One2many('approval.request', 'vtt_task_id', 'Approval Requests')
    vtt_approval_request_count = fields.Integer('Approval Request Count', compute='_compute_approval_request_count')

    vtt_construct_id = fields.Many2one('vtt.construct', 'Construct')

    def _compute_approval_request_count(self):
        for pt in self:
            pt.vtt_approval_request_count = len(pt.vtt_approval_request_ids)

    vtt_approve_need = fields.Boolean('Need Approve?', compute='_compute_approve_need', store=True)

    vtt_support_user_ids = fields.Many2many('res.users', string='Supporters')

    priority = fields.Selection(selection_add=[
        ('2', 'High Important'),
        ('3', 'Most Important'),
    ], string='Priority', ondelete={
        '2': 'set 1',
        '3': 'set 1',
    })

    vtt_task_rating_ids = fields.One2many('vtt.project.task.rating', 'task_id', 'User Rating')

    @api.depends('vtt_approval_request_ids', 'vtt_approval_request_ids.request_status')
    def _compute_approve_need(self):
        for pt in self:
            check = False
            if pt.vtt_approval_request_ids:
                requests_need_approve = pt.mapped('vtt_approval_request_ids').filtered(lambda ar: ar.request_status in ['pending'])
                if requests_need_approve:
                    check = True
            pt.vtt_approve_need= check