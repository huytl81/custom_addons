# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# from datetime import timedelta
from dateutil.relativedelta import relativedelta


class MaintenancePlanType(models.Model):
    _name = 'vtt.maintenance.plan.type'
    _description = 'Maintenance Plan Type'

    name = fields.Char('Name', translate=True, required=True)
    period_type = fields.Selection([
        ('day', 'Days'),
        ('month', 'Months'),
        ('year', 'Years')
    ], 'Period Type', default='month')
    period_value = fields.Integer('Period Value', default=1)

    active = fields.Boolean('Active', default=True)

    def get_next_by_period(self, dt):
        if self.period_type == 'year':
            dt_delta = relativedelta(years=self.period_value)
        elif self.period_type == 'month':
            dt_delta = relativedelta(months=self.period_value)
        else:
            dt_delta = relativedelta(days=self.period_value)
        return dt + dt_delta