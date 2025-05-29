# -*- coding: utf-8 -*-

from odoo import models, fields, api
from random import randint


class RepairOrderTag(models.Model):
    _name = 'vtt.repair.order.tag'
    _description = 'Repair Order Tag'

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color', default=_get_default_color)

    _sql_constraints = [('name_uniq', 'unique (name)', "Tag name already exists!")]