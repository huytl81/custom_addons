# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vtt_line_note = fields.Char('Note')
    vtt_product_actual = fields.Char('Product Actual')
    vtt_product_origin = fields.Char('Product Origin')
    vtt_product_origin_id = fields.Many2one('sale.product.origin', 'Product Origin')


class SaleProductOrigin(models.Model):
    _name = 'sale.product.origin'
    _description = 'Sale Product Origin'

    name = fields.Char('Name')