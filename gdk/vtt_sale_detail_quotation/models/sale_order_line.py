# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def default_section_domain(self):
        context = self._context
        order_id = context.get('current_order_id', False)
        return json.dumps([('display_type', '=', 'line_section'), ('order_id', '=', order_id)])

    specical_product = fields.Boolean('Special Product?', default=False)
    section_id = fields.Many2one('sale.order.line', 'Section',
                                 domain=[('display_type', '=', 'line_section'), ('order_id', '=', lambda l:l.order_id.id)])

    # section_line_ids = fields.One2many('sale.order.line', 'section_id', 'Section Lines')

    display_qty = fields.Float(string='Display Quantity', digits='Product Unit of Measure', default=1.0)
    section_display_qty = fields.Float('Section Display Quantity', related='section_id.display_qty', store=True)

    display_price_subtotal = fields.Monetary(string='Display Subtotal', readonly=True, store=True, compute='_compute_display_amount')
    display_price_tax = fields.Float(string='Display Total Tax', readonly=True, store=True, compute='_compute_display_amount')
    display_price_total = fields.Monetary(string='Display Total', readonly=True, store=True, compute='_compute_display_amount')

    display_price_unit = fields.Float('Display Unit Price', digits='Product Price', compute='_compute_display_price_unit', store=True)

    # section_type = fields.Selection([
    #     ('top', 'Top'),
    #     ('bottom', 'Bottom')
    # ], 'Section Type')

    section_line_display = fields.Boolean('As Section?', default=False)

    section_domain = fields.Char('Section Domain', compute='_compute_section_domain', default=default_section_domain)

    @api.depends('order_id')
    def _compute_section_domain(self):
        for line in self:
            domain = [('display_type', '=', 'line_section'), ('order_id', '=', line.order_id._origin.id)]
            line.section_domain = json.dumps(domain)

    @api.depends('section_id.display_qty')
    @api.onchange('display_qty')
    def onchange_display_qty(self):
        if not self.display_type:
            if self.section_id:
                self.product_uom_qty = self.display_qty * self.section_id.display_qty
            else:
                self.product_uom_qty = self.display_qty

    @api.depends('price_subtotal', 'price_tax', 'price_total', 'display_qty', 'section_id.display_qty',
                 'order_id.order_line.price_subtotal', 'order_id.order_line.price_tax')
    def _compute_display_amount(self):
        for line in self:
            if line.display_type == 'line_section':
                ls = self.order_id.order_line.filtered(lambda l: l.section_id == line)
                line.display_price_subtotal = sum([l.price_subtotal for l in ls])
                line.display_price_tax = sum([l.price_tax for l in ls])
                line.display_price_total = sum([l.price_total for l in ls])
            elif line.section_id:
                line.display_price_subtotal = line.price_subtotal / (line.section_display_qty or 1.0)
                line.display_price_tax = line.price_tax / (line.section_display_qty or 1.0)
                line.display_price_total = line.price_total / (line.section_display_qty or 1.0)
            else:
                line.display_price_subtotal = line.price_subtotal
                line.display_price_tax = line.price_tax
                line.display_price_total = line.price_total

    @api.depends('order_id.order_line', 'order_id.order_line.display_price_subtotal')
    def _compute_display_price_unit(self):
        for line in self:
            if line.display_type == 'line_section':
                ls = self.order_id.order_line.filtered(lambda l: l.section_id == line)
                line.display_price_unit = sum([l.display_price_subtotal for l in ls])
            else:
                line.display_price_unit = line.price_unit

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        if 'display_qty' in vals and self.display_type == 'line_section':
            self.order_id.update_price_by_display_qty()

        return res
