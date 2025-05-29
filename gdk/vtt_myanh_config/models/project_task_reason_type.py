# -*- coding: utf-8 -*-

from odoo import models, fields
from random import randint


class ProjectTaskReasonType(models.Model):
    _name = 'vtt.project.task.reason.type'
    _description = 'Task Reason Type'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name')
    color = fields.Integer('Color', default=_get_default_color)
    detail_need = fields.Boolean('Detail Needed?', default=False)