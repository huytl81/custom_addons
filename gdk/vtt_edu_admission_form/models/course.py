# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Course(models.Model):
    _inherit = 'op.course'

    category_id = fields.Many2one('op.category', 'Category')