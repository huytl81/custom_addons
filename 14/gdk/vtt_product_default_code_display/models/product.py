# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_product_multiline_description_sale(self):
        if self.description_sale:
            name = self.description_sale
        else:
            name = super(ProductProduct, self).get_product_multiline_description_sale()

        return name

    def name_get(self):
        display_code_context = self._context.get('display_default_code', False)
        if not display_code_context:
            self = self.with_context(display_default_code=False)
        return super(ProductProduct, self).name_get()