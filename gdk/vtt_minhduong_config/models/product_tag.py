# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import random


class ProductTag(models.Model):
    _name = 'vtt.product.tag'
    _description = 'Product Tag'

    def _get_default_color(self):
        return random.randint(1, 11)

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=lambda self: self._get_default_color())
