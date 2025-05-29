# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTaskRating(models.Model):
    _name = 'vtt.project.task.rating'
    _description = 'Task Rating'
    _order = 'date desc,user_id'

    task_id = fields.Many2one('project.task', 'Task')
    user_id = fields.Many2one('res.users', 'User')
    department_id = fields.Many2one('hr.department', related='user_id.department_id', store=True)

    rating = fields.Selection([
        ('0', 'None'),
        ('1', 'Poor'),
        ('2', 'Average'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent'),
    ], 'Rating', default='3')

    rating_score = fields.Float('Rating Score', compute='_compute_rating_score', group_operator="avg", store=True)

    state = fields.Selection([
        ('new', 'New'),
        ('approve', 'Approved')
    ], 'State', default='new')

    date = fields.Date('Date', default=fields.Date.today())

    @api.depends('rating')
    def _compute_rating_score(self):
        for ptr in self:
            ptr.rating_score = float(ptr.rating)

    def action_approve(self):
        return self.write({
            'state': 'approve',
            'date': fields.Date.today()
        })

    def action_open(self):
        return self.write({
            'state': 'new',
            'date': False
        })