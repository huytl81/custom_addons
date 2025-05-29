# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    product_id = fields.Many2one('product.product', 'Product')
    is_show = fields.Boolean('Show in Order?', default=True)