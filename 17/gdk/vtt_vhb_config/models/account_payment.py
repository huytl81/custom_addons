# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    vtt_reconciled_sale_ids = fields.Many2many('sale.order',
                                               compute='_compute_vtt_sale_info',
                                               string='Sale Order',
                                               store=True,)
    vtt_reconciled_inv_user_ids = fields.Many2many('res.users',
                                                   compute='_compute_vtt_sale_info',
                                                   string='Invoice User',
                                                   store=True,)

    vtt_reconciled_residual_info = fields.Monetary('Residual Info', currency_field='currency_id', compute='compute_sales_amount_info')
    vtt_reconciled_taxes_info = fields.Monetary('Tax Info', currency_field='currency_id', compute='compute_sales_amount_info')
    vtt_sales_amount_info = fields.Monetary('Sales Amount', currency_field='currency_id', compute='compute_sales_amount_info')

    def action_custom_sales_report(self):
        default_date_from = fields.Date.today().replace(day=1)
        default_date_to = (default_date_from + relativedelta(months=1)).replace(day=1)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Custom Sales Report Wizard'),
            'view_mode': 'form',
            'res_model': 'vtt.vhb.custom.sales.report.wz',
            'context': {
                'default_date_from': default_date_from,
                'default_date_to': default_date_to,
            },
            'target': 'new',
        }

    @api.depends_context('sales_date_from', 'sales_date_to')
    @api.depends('reconciled_invoice_ids')
    def compute_sales_amount_info(self):
        date_from = self.env.context.get('sales_date_from', False)
        date_to = self.env.context.get('sales_date_to', False)
        if not (date_from and date_to):
            for pay in self:
                pay.vtt_reconciled_residual_info = sum([move.amount_residual for move in pay.reconciled_invoice_ids])
            self.vtt_reconciled_taxes_info = 0.0
            self.vtt_sales_amount_info = 0.0
        else:
            moves = self.mapped('reconciled_invoice_ids')
            move_residual_data = {
                move.id: {
                    'residual': move.amount_residual + move.get_invoice_partials_at_date(date_to),
                    'amount_tax': move.amount_tax,
                    'amount_tax_ref': move.amount_tax,
                    'tax_factor': move.amount_tax >= (move.amount_residual + move.get_invoice_partials_at_date(date_to)),
                    'taxed': False,
                } for move in moves
            }
            for pay in reversed(self.sorted('date')):
                pay.vtt_reconciled_residual_info = sum([move_residual_data[m.id]['residual'] for m in pay.reconciled_invoice_ids])
                pay_tax_factor = any([move_residual_data[m.id]['tax_factor'] for m in pay.reconciled_invoice_ids if not move_residual_data[m.id]['taxed']])
                if pay_tax_factor:
                    pay_taxes_info = sum([move_residual_data[m.id]['amount_tax'] for m in pay.reconciled_invoice_ids])
                    pay.vtt_reconciled_taxes_info = pay_taxes_info
                    # pay.vtt_sales_amount_info = pay.amount - pay_taxes_info
                    pay.vtt_sales_amount_info = pay.amount_signed - pay_taxes_info
                    for m in pay.reconciled_invoice_ids:
                        move_residual_data[m.id]['taxed'] = True
                else:
                    pay.vtt_reconciled_taxes_info = 0.0
                    # pay.vtt_sales_amount_info = pay.amount
                    pay.vtt_sales_amount_info = pay.amount_signed

    @api.depends('reconciled_invoice_ids', 'reconciled_invoice_ids.line_ids',
                 'reconciled_invoice_ids.invoice_user_id',
                 'reconciled_invoice_ids.state')
    def _compute_vtt_sale_info(self):
        for move in self:
            if move.reconciled_invoice_ids:
                move.vtt_reconciled_sale_ids = move.reconciled_invoice_ids.line_ids.sale_line_ids.order_id
                move.vtt_reconciled_inv_user_ids = move.reconciled_invoice_ids.invoice_user_id
            else:
                move.vtt_reconciled_sale_ids = False
                move.vtt_reconciled_inv_user_ids = False

