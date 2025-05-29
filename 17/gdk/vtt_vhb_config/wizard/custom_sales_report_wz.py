# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CustomSalesReportWizard(models.TransientModel):
    _name = 'vtt.vhb.custom.sales.report.wz'
    _description = 'Custom Sales Report Wizard'

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')

    def action_custom_sales_report(self):
        name = _('Custom Sales Report')
        name += f' {self.date_from} - {self.date_to}'
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to),
                  ('partner_type', '=', 'customer'), ('is_internal_transfer', '=', False)]
        return {
            'type': 'ir.actions.act_window',
            'name': name,
            'view_mode': 'list,form',
            'views': [[self.env.ref('vtt_vhb_config.vtt_view_tree_account_payment_custom_sales_report').id, 'list'], [False, 'form']],
            'res_model': 'account.payment',
            'domain': domain,
            'context': {
                'sales_date_from': self.date_from,
                'sales_date_to': self.date_to,
            },
            'target': 'current',
        }