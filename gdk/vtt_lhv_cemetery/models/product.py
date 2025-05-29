# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_land = fields.Boolean('Is Land')
    
    is_care_service = fields.Boolean('Is Care Service')

    # for mobile
    price_text = fields.Text('Price show on mobile')