# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectCreateWizard(models.TransientModel):
    _name = 'vtt.project.create.wz'
    _description = 'Project Create Wizard'

    name = fields.Char('Name')
    order_id = fields.Many2one('sale.order', 'Sale Order')
    partner_id = fields.Many2one('res.partner', 'Partner')
    project_template_id = fields.Many2one('project.project', 'Template Project')

    sale_line_id = fields.Many2one('sale.order.line', 'Tracking Line')

    @api.onchange('order_id')
    def onchange_sale_order_id(self):
        self.partner_id = self.order_id.partner_id.id
        sol = self.order_id.order_line.filtered(lambda x: x.product_id.detailed_type == 'service')
        if sol:
            self.sale_line_id = sol[0].id
            self.project_template_id = sol[0].product_id.project_template_id.id
        else:
            self.sale_line_id = False

    @api.onchange('order_id', 'project_template_id')
    def onchange_sale_project_template(self):
        name = self.order_id.name
        if self.project_template_id:
            name += f' - {self.project_template_id.name}'
        self.name = name

    def _create_sale_project_prepare_values(self):
        account = self.order_id.analytic_account_id
        if not account:
            self.order_id._create_analytic_account()
            account = self.order_id.analytic_account_id
        return {
            'name': self.name,
            'analytic_account_id': account.id,
            'partner_id': self.partner_id.id,
            'sale_order_id': self.order_id.id,
            'active': True,
            'company_id': self.order_id.company_id.id,
            'allow_billable': True,
            'user_id': False,
        }

    def create_sale_project(self):
        if self.sale_line_id and self.sale_line_id.product_id.project_template_id == self.project_template_id:
            self.order_id.order_line.sudo().with_company(self.order_id.company_id)._timesheet_service_generation()
            return
        else:
            values = self._create_sale_project_prepare_values()
            if self.project_template_id:
                project = self.project_template_id.with_context(no_create_folder=True).copy(values)
                project.tasks.write({
                    'partner_id': self.partner_id.id,
                })
                # duplicating a project doesn't set the SO on sub-tasks
                project.tasks.filtered('parent_id').write({
                    'sale_order_id': self.order_id.id,
                })
            else:
                project = self.env['project.project'].with_context(no_create_folder=True).create(values)

            # Avoid new tasks to go to 'Undefined Stage'
            if not project.type_ids:
                project.type_ids = self.env['project.task.type'].create([{
                    'name': name,
                    'fold': fold,
                    'sequence': sequence,
                } for name, fold, sequence in [
                    (_('To Do'), False, 5),
                    (_('In Progress'), False, 10),
                    (_('Done'), True, 15),
                    (_('Canceled'), True, 20),
                ]])

            return project