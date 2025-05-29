# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    vtt_mobile_image = fields.Binary('Image')
    vtt_show_on_mobile = fields.Boolean('Show on mobile', default=False)
    vtt_mobile_order = fields.Integer('Order category for mobile')