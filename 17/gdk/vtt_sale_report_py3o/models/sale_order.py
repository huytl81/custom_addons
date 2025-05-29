# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_py3o_report_data(self):
        self.ensure_one()
        if self.partner_id.parent_id:
            partner_contact = self.partner_id.name or ''
            partner_company = self.partner_id.parent_id.name or ''
            partner_address = self.partner_id.parent_id.street or ''
            partner_name = self.partner_id.parent_id.name or ''
            partner_vat = self.partner_id.parent_id.vat or ''
        else:
            partner_address = self.partner_id.street or ''
            partner_contact = ''
            partner_company = ''
            partner_name = self.partner_id.name or ''
            partner_vat = self.partner_id.vat or ''
        values = {
            'name': self.name or '',
            'date_order': self.date_order.strftime('%d/%m/%Y'),
            'partner_id': self.partner_id.get_py3o_report_data(),
            'user_id': self.user_id.partner_id.get_py3o_report_data(),
            'partner_name': partner_name,
            'partner_contact': partner_contact,
            'partner_company': partner_company,
            'partner_address': partner_address,
            'partner_vat': partner_vat,
            'date_order_dformat': self.date_order.strftime('ngày %d tháng %m năm %Y'),
        }
        return values
