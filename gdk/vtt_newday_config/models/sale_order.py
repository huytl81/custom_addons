# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _compute_line_section_product_area(self):
        lines = self.mapped('order_line')
        sections = lines.filtered(lambda l: l.display_type == 'line_section')
        for s in sections:
            s_lines = lines.filtered(lambda l: l.section_id == s)
            s.vtt_product_area = sum([l.vtt_product_area for l in s_lines]) * s.display_qty


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    vtt_product_width = fields.Float('Width')
    vtt_product_height = fields.Float('Height')

    vtt_product_area = fields.Float('Area')

    vtt_product_size_price = fields.Float('Size Price')

    vtt_sub_uom = fields.Many2one('uom.uom', 'Sub-UoM')

    # For display other service at bottom of quotation
    vtt_other_service = fields.Boolean('Other Service', default=False)

    @api.onchange('product_id')
    def onchange_door_product(self):
        if self.product_id:
            self.vtt_product_width = self.product_id.vtt_product_width
            self.vtt_product_height = self.product_id.vtt_product_height
            self.vtt_product_area = self.product_id.vtt_product_area
            self.vtt_product_size_price = self.product_id.vtt_product_size_price
            self.vtt_sub_uom = self.product_id.vtt_sub_uom

    @api.onchange('vtt_product_width', 'vtt_product_height', 'display_qty')
    def onchange_line_product_size(self):
        self.vtt_product_area = self.vtt_product_width * self.vtt_product_height * self.display_qty

    @api.onchange('vtt_product_width', 'vtt_product_height', 'vtt_product_area', 'vtt_product_size_price')
    def onchange_line_product_area_price(self):
        if not self.display_type:
            if self.product_id.vtt_product_door_type == 'door':
                self.price_unit = self.vtt_product_area * self.vtt_product_size_price
            elif self.product_id.vtt_product_door_type == 'accessory':
                if not (self.vtt_product_width and self.vtt_product_height):
                    factor = self.vtt_product_width or self.vtt_product_height
                    self.price_unit = factor * self.vtt_product_size_price
                else:
                    self.price_unit = self.vtt_product_area * self.vtt_product_size_price

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'vtt_product_area' in vals and self.product_id.vtt_product_door_type == 'door':
            self.order_id._compute_line_section_product_area()

        return res

    # Other Approach
    '''
    vtt_product_width = fields.Float('Width', related='product_id.vtt_product_width', store=True)
    vtt_product_height = fields.Float('Height', related='product_id.vtt_product_height', store=True)

    vtt_product_area = fields.Float('Area', related='product_id.vtt_product_area', store=True)
    vtt_line_total_area = fields.Float('Total Area', digits='Product Size', compute='_compute_line_total_area', store=True)
    vtt_display_total_area = fields.Float('Display Area', digits='Product Size', compute='_compute_display_total_area', store=True)

    vtt_product_size_price = fields.Float('Size Price', compute='_compute_product_size_price', store=True)

    @api.depends('product_id', 'vtt_product_area', 'product_uom_qty')
    def _compute_line_total_area(self):
        for l in self:
            l.vtt_line_total_area = l.vtt_product_area * l.product_uom_qty

    @api.depends('product_id', 'vtt_product_area', 'display_qty')
    def _compute_display_total_area(self):
        for l in self:
            l.vtt_display_total_area = l.vtt_product_area * l.display_qty

    @api.depends('product_id', 'price_unit', 'vtt_product_area')
    def _compute_product_size_price(self):
        for l in self:
            l.vtt_product_size_price = l.price_unit / (l.vtt_product_area or 1.0)
    '''