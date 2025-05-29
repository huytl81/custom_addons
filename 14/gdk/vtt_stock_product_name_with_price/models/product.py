# -*- coding: utf-8 -*-

from odoo import models, tools


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):

        result = super(ProductProduct, self).name_get()
        params = self.env['ir.config_parameter'].sudo()
        name_price_param = params.get_param('vtt_stock_product_name_with_price.vtt_product_name_with_price', default=False)

        if name_price_param:
            price_type = params.get_param('vtt_stock_product_name_with_price.vtt_product_name_price_type', default='list_price')
            currency = self.env.company.currency_id
            lang = self.env.user.lang

            # price_lst = [(rd.id, tools.format_amount(self.env, rd[price_type], currency, lang)) for rd in self]
            price_dict = {
                rd.id: ' - ' + tools.format_amount(self.env, rd[price_type], currency, lang) for rd in self
            }

            result = [(r_id, r_name + price_dict[r_id]) for r_id, r_name in result]

        return result