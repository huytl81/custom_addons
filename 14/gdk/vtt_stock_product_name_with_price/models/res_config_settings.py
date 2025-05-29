# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vtt_product_name_with_price = fields.Boolean('Product Name with Price', help='Display Product name with Price.',
                                                 config_parameter='vtt_stock_product_name_with_price.vtt_product_name_with_price',
                                                 default=False)
    vtt_product_name_price_type = fields.Selection([
        ('list_price', 'List Price'),
        ('standard_price', 'Cost')
    ], 'Price type')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        # res['vtt_product_name_with_price'] = self.env['ir.config_parameter'].sudo().get_param('vtt_stock_product_name_with_price.vtt_product_name_with_price', default=False)
        res['vtt_product_name_price_type'] = self.env['ir.config_parameter'].sudo().get_param('vtt_stock_product_name_with_price.vtt_product_name_price_type', default='list_price')

        return res

    @api.model
    def set_values(self):
        # self.env['ir.config_parameter'].sudo().set_param('vtt_stock_product_name_with_price.vtt_product_name_with_price', self.vtt_product_name_with_price)
        self.env['ir.config_parameter'].sudo().set_param('vtt_stock_product_name_with_price.vtt_product_name_price_type', self.vtt_product_name_price_type)
        super(ResConfigSettings, self).set_values()