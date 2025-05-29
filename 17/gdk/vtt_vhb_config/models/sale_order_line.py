# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def get_py3o_report_data(self):
        data = super(SaleOrderLine, self).get_py3o_report_data()
        vals = {
            'product_name': self.product_id and self.product_id.name or '',
            'product_code': self.product_id and self.product_id.default_code or '',
            'product_uom': self.product_uom and self.product_uom.name or '',
            'tax_id': self.tax_id and ', '.join([t.name for t in self.tax_id]) or '',
            'product_type': self.product_id and self.product_id.detailed_type or '',
            'product_description': self.product_id.description_sale or ''
        }
        data.update(vals)

        return data