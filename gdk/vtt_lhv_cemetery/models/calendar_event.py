# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    vtt_department_ids = fields.Many2many('hr.department', 'vtt_calendar_event_department_rel', string='Department')

    #for mobile
    vtt_is_scheduled = fields.Boolean('Scheduled status', default=False)