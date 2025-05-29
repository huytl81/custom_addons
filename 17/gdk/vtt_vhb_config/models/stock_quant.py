# -*- coding:utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_tag_ids = fields.Many2many(related='product_id.product_tag_ids')