# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from random import randint


class VttCarRepairTags(models.Model):
    _name = "vtt.car.repair.tags"
    _description = "Repair Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Tag Name', required=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]