# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttCustomRating(models.Model):
    _inherit = 'vtt.custom.rating'

    employee_id = fields.Many2one('hr.employee', 'Employee')
    department_id = fields.Many2one('hr.department', 'Department')

    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            if self.user_id.employee_id:
                self.employee_id = self.user_id.employee_id
            else:
                self.employee_id = False

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            if self.employee_id.user_id:
                self.user_id = self.employee_id.user_id
            else:
                self.user_id = False

            if self.employee_id.department_id:
                self.department_id = self.employee_id.department_id