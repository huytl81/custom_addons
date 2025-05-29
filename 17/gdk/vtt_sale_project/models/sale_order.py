# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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