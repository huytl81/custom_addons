# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    product_default_code = fields.Char('Default Code', related='product_id.default_code')
    date_material_deadline = fields.Date('Component Deadline')