# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    abs_price_subtotal = fields.Float('ABS Untaxed Total', readonly=True)
    abs_price_average = fields.Float('ABS Average Price', readonly=True, group_operator="avg")

    @api.model
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ''',\n
        ABS(-line.balance * currency_table.rate) AS abs_price_subtotal,
        ABS(-line.balance / NULLIF(COALESCE(uom_line.factor, 1) / COALESCE(uom_template.factor, 1), 0.0) * currency_table.rate) AS abs_price_average
        '''