# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vtt_product_door_type = fields.Selection([
        ('door', 'Door'),
        ('accessory', 'Accessory')
    ], 'Door Type', default=False)

    @api.onchange('type')
    def onchange_type_2_door(self):
        if self.type == 'service':
            self.vtt_product_door_type = False

    vtt_product_width = fields.Float('Width', digits='Product Size')
    vtt_product_height = fields.Float('Height', digits='Product Size')

    vtt_product_area = fields.Float('Area', digits='Product Size')
    vtt_product_size_price = fields.Float('Size Price')

    # Display sub-uom
    vtt_sub_uom = fields.Many2one('uom.uom', 'Sub-UoM')

    @api.onchange('vtt_product_width', 'vtt_product_height')
    def onchange_product_size(self):
        self.vtt_product_area = self.vtt_product_width * self.vtt_product_height

    @api.onchange('vtt_product_area', 'vtt_product_size_price')
    def onchange_product_area_price(self):
        if self.vtt_product_door_type == 'door':
            self.list_price = self.vtt_product_area * self.vtt_product_size_price
        elif self.vtt_product_door_type == 'accessory':
            if not (self.vtt_product_width and self.vtt_product_height):
                factor = self.vtt_product_width or self.vtt_product_height
                self.list_price = factor * self.vtt_product_size_price
            else:
                self.list_price = self.vtt_product_area * self.vtt_product_size_price

    # Other Approach
    '''
    vtt_product_w_size = fields.Boolean('Product with Size', default=False)

    vtt_product_width = fields.Float('Width', digits='Product Size')
    vtt_product_height = fields.Float('Height', digits='Product Size')

    vtt_product_area = fields.Float('Area', digits='Product Size')

    vtt_product_size_price = fields.Float('Size Price', compute='_compute_product_size_price', store=True)

    @api.onchange('vtt_product_width', 'vtt_product_height')
    def onchange_product_size(self):
        self.vtt_product_area = self.vtt_product_width * self.vtt_product_height

    @api.depends('vtt_product_area', 'list_price')
    def _compute_product_size_price(self):
        for p in self:
            p.vtt_product_size_price = p.list_price / (p.vtt_product_area or 1.0)
    '''