# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_product_multiline_description_sale(self):
        if self.description_sale:
            name = self.description_sale
        else:
            name = super(ProductProduct, self).get_product_multiline_description_sale()

        return name