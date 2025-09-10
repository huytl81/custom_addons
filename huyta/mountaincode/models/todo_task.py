from odoo import models, fields, api, _
from random import randint

class TodoTask(models.Model):
    _name = 'todo.task'
    _description = 'Todo Task'
    _order = 'priority desc, name'

    name = fields.Char(string='Task Name', required=True)
    priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], string='Priority', default='low')
    is_done = fields.Boolean(string='Done', default=False)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    deadline = fields.Date(string='Deadline')
    color = fields.Char(string='Color', default=lambda self: self._get_default_color(), aggregator=False)

    @api.model
    def _get_default_color(self):
        return randint(1, 11)
