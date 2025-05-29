# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    vtt_amount_to_invoice = fields.Monetary('Amount To Invoice', store=True, readonly=True, compute='_compute_amount_to_invoice')

    @api.depends('state', 'qty_to_invoice', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount_to_invoice(self):
        for line in self:
            if line.state not in ['purchase', 'done']:
                amount_2_invoice = 0.0
            else:
                base_lines = self.env['account.tax']._convert_to_tax_base_line_dict(
                    line,
                    partner=line.order_id.partner_id,
                    currency=line.order_id.currency_id,
                    product=line.product_id,
                    taxes=line.taxes_id,
                    price_unit=line.price_unit,
                    quantity=line.qty_to_invoice,
                    discount=line.discount,
                    price_subtotal=line.price_subtotal,
                )
                tax_results = self.env['account.tax']._compute_taxes([base_lines])
                totals = next(iter(tax_results['totals'].values()))
                amount_untaxed = totals['amount_untaxed']
                amount_tax = totals['amount_tax']

                amount_2_invoice = amount_untaxed + amount_tax

            line.update({
                'vtt_amount_to_invoice': amount_2_invoice,
            })