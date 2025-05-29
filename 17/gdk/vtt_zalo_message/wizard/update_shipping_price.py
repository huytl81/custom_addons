# -*- coding: utf-8 -*-
from odoo import api, fields, models

class UpdateShippingPriceWizard(models.TransientModel):
    _name = 'update.shipping.price.wizard'
    _description = 'Update Shipping Price Wizard'

    shipping_price = fields.Float(string='Shipping Price')

    def update_shipping_price(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            wards = self.env['res.ward'].browse(active_ids)
            for ward in wards:
                ward.default_shipping_method_price = self.shipping_price