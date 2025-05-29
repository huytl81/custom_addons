# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vtt_commitment_date_str = fields.Char('Commitment Date')
    vtt_shipping_address_str = fields.Char('Shipping Address')
    vtt_quotation_due_str = fields.Char('Quotation Due Date')
    vtt_payment_policy_str = fields.Char('Payment Policy')
    vtt_price_include_str = fields.Char('Price Included')

    contact_id = fields.Many2one('res.partner', 'Contact')

    vtt_amount_reduced = fields.Float('Amount Reduced', compute='_compute_amount_reduced')

    def _compute_amount_reduced(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                total += line.price_total / (100-line.discount) * line.discount if line.discount != 100 else 0.0
            order.vtt_amount_reduced = total

    @api.onchange('partner_id')
    def onchange_partner_2_contact(self):
        if self.partner_id and self.partner_id.child_ids:
            self.contact_id = self.partner_id.child_ids.sorted(lambda c: -c.id)[0]
        else:
            self.contact_id = False

    def _compute_show_project_and_task_button(self):
        is_project_manager = self.env.user.has_group('project.group_project_manager')
        for order in self:
            order.show_project_button = order.project_count
            order.show_task_button = order.tasks_count
            order.show_create_project_button = is_project_manager and not order.project_count and order.state != 'cancel'

    def action_create_project(self):
        # New solution
        return {
            'name': _('Project Creation'),
            'view_mode': 'form',
            'res_model': 'vtt.project.create.wz',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
        }

        # Old solution
        # self.ensure_one()
        # service_line = self.order_line.filtered(lambda sol: sol.product_id.detailed_type == 'service')
        # if service_line:
        #     return super(SaleOrder, self).action_create_project()
        # else:
        #     return {
        #         'name': _('Project Creation'),
        #         'view_mode': 'form',
        #         'res_model': 'vtt.project.create.wz',
        #         'type': 'ir.actions.act_window',
        #         'target': 'new',
        #         'context': {
        #             'default_order_id': self.id,
        #             'default_partner_id': self.partner_id.id,
        #         },
        #     }

    def action_view_project_ids(self):
        self.ensure_one()
        service_line = self.order_line.filtered(lambda sol: sol.product_id.detailed_type == 'service')
        if service_line:
            return super(SaleOrder, self).action_view_project_ids()
        else:
            action = {
                'type': 'ir.actions.act_window',
                'name': _('Projects'),
                'domain': ['|', ('sale_order_id', '=', self.id),
                           ('id', 'in', self.with_context(active_test=False).project_ids.ids),
                           ('active', 'in', [True, False])],
                'res_model': 'project.project',
                'views': [(False, 'kanban'), (False, 'tree'), (False, 'form')],
                'view_mode': 'kanban,tree,form',
                'context': {
                    **self._context,
                    'default_partner_id': self.partner_id.id,
                    'default_sale_order_id': self.id,
                    'default_allow_billable': 1,
                }
            }
            if len(self.with_context(active_test=False).project_ids) == 1:
                action.update({'views': [(False, 'form')], 'res_id': self.project_ids.id})
            return action

    @api.model
    def get_py3o_report_data(self):
        data = super(SaleOrder, self).get_py3o_report_data()
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
        vals = {
            'date_order_sformat': self.date_order.strftime('%d/%m/%Y'),
            'date_order_dformat': self.date_order.strftime('ngày %d tháng %m năm %Y'),
            # 'date_order_dformat': self.date_order.strftime('ngay %d thang %m nam %Y'),
            'today_dformat': datetime.date.today().strftime('ngày %d tháng %m năm %Y'),
            # 'today_dformat': datetime.date.today().strftime('ngay %d thang %m nam %Y'),
            'partner_id': self.partner_id.get_py3o_report_data(),
            'contact_id': self.contact_id.get_py3o_report_data(),
            'partner_name': partner_name,
            'partner_contact': partner_contact,
            'partner_company': partner_company,
            'partner_address': partner_address,
            'partner_vat': partner_vat,
        }
        data.update(vals)

        return data
