# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VttCarRepairOrderLine(models.Model):
    _inherit = 'vtt.car.repair.order.line'

    discount_fixed = fields.Float(
        string="Discount (Fixed)",
        digits="Product Price",
        default=0.00
    )

    @api.depends('price_unit', 'discount', 'discount_fixed')
    def _get_price_reduce(self):
        for line in self:
            if line.discount_fixed:
                line.price_reduce = line.price_unit - line.discount_fixed
            else:
                line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    @api.onchange('discount_fixed')
    def onchange_discount_fixed(self):
        if self.discount_fixed:
            self.discount = 0.0

    @api.onchange('discount')
    def onchange_discount(self):
        if self.discount:
            self.discount_fixed = 0.0

    def get_invoice_line_values(self, group=False):
        res = super(VttCarRepairOrderLine, self).get_invoice_line_values(group)
        res.update({
            'discount_fixed': self.discount_fixed
        })
        return res