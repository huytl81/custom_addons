# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def get_py3o_report_data(self):
        self.ensure_one()
        return {
            'name': self.name or '',
            'product_name': self.product_id and self.product_id.name or '',
            'product_code': self.product_id and self.product_id.default_code or '',
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom and self.product_uom.name or '',
            'tax_id': self.tax_id and ', '.join([t.name for t in self.tax_id]) or '',
            'discount': self.discount,
            'price_unit': self.price_unit,
            'price_subtotal': self.price_subtotal,
            'price_total': self.price_total,
            'price_tax': self.price_tax,
            'product_type': self.product_id and self.product_id.detailed_type or '',
            'product_description': self.product_id.description_sale or ''
        }
