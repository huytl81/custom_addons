# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    vtt_budget_template_id = fields.Many2one('vtt.analytic.budget.template', 'Budget Plan')

    vtt_budget_line_ids = fields.One2many('vtt.analytic.budget.line', 'account_analytic_id', 'Budget Items')

    vtt_planned_amount_available = fields.Monetary('Planned Available Amount',
                                                   compute='_compute_planned_amount', store=True)
    vtt_planned_amount_payable = fields.Monetary('Planned Payable Amount',
                                                 compute='_compute_planned_amount', store=True)
    vtt_planned_amount_payable_display = fields.Monetary(compute='_compute_display_amount')

    vtt_practical_amount_available = fields.Monetary('Practical Available Amount',
                                                     compute='_compute_practical_amount', store=True)
    vtt_practical_amount_payable = fields.Monetary('Practical Payable Amount',
                                                   compute='_compute_practical_amount', store=True)
    vtt_practical_amount_payable_display = fields.Monetary(compute='_compute_display_amount')

    vtt_amount_available_percentage = fields.Float('Available Achievement', compute='_compute_available_percentage')
    vtt_amount_payable_percentage = fields.Float('Payable Achievement', compute='_compute_payable_percentage')

    def re_arrange_lines(self):
        self.ensure_one()
        lines = self.vtt_budget_line_ids
        line_ids = []
        counter = 0
        main_section = lines.filtered(lambda l: not l.parent_id).sorted('sequence')
        for s in main_section:
            s_lines = lines.filtered(lambda l: s.full_path in l.full_path).sorted('full_sequence')
            for sl in s_lines:
                line_ids.append([sl.id, counter])
                counter += 1
        if line_ids:
            self.write({'vtt_budget_line_ids': [(Command.update(sl[0], {'sequence': sl[1]})) for sl in line_ids]})

    def get_budget_template_items(self):
        if self.vtt_budget_template_id:
            # self.vtt_budget_line_ids.unlink()
            budget_vals = self.vtt_budget_template_id.prepare_budget_data(self.id)
            if budget_vals:
                self.write({'vtt_budget_line_ids': [(5, 0, 0)] + budget_vals})
                self.line_ids.vtt_budget_line_id = False

    def update_budget_items_from_template(self):
        if self.vtt_budget_template_id:

            budget_lines = self.vtt_budget_line_ids
            budget_paths = budget_lines.mapped('full_path')
            template_lines = self.vtt_budget_template_id.line_ids
            template_paths = template_lines.mapped('full_path')

            line_2_create = []
            for t in template_paths:
                if t not in budget_paths:
                    line_2_create.append(t)

            if line_2_create:
                created_lines = {}
                for t in line_2_create:
                    t_bud = template_lines.get_by_full_path(t)
                    t_vals = {
                        'name': t_bud.name,
                        'type': t_bud.type,
                        'sequence': t_bud.sequence,
                        'product_id': t_bud.product_id.id,
                        'product_uom': t_bud.product_uom.id,
                        'product_uom_qty': t_bud.product_uom_qty,
                        'account_analytic_id': self.id,
                    }
                    if t_bud.parent_id:
                        t_bud_parent_path = t_bud.parent_id.full_path
                        t_line_parent = budget_lines.get_by_full_path(t_bud_parent_path)
                        if not t_line_parent:
                            t_line_parent = created_lines[t_bud_parent_path]
                        t_vals['parent_id'] = t_line_parent.id

                    new_line = self.env['vtt.analytic.budget.line'].create(t_vals)
                    created_lines[t] = new_line

    def _compute_display_amount(self):
        for acc in self:
            acc.vtt_planned_amount_payable_display = abs(acc.vtt_planned_amount_payable)
            acc.vtt_practical_amount_payable_display = abs(acc.vtt_practical_amount_payable)

    @api.depends('vtt_planned_amount_available', 'vtt_practical_amount_available')
    def _compute_available_percentage(self):
        for acc in self:
            if acc.vtt_planned_amount_available != 0.0:
                acc.vtt_amount_available_percentage = float((acc.vtt_practical_amount_available or 0.0) / acc.vtt_planned_amount_available)
            else:
                acc.vtt_amount_available_percentage = 0.0

    @api.depends('vtt_planned_amount_payable', 'vtt_practical_amount_payable')
    def _compute_payable_percentage(self):
        for acc in self:
            if acc.vtt_planned_amount_payable != 0.0:
                acc.vtt_amount_payable_percentage = float(
                    (acc.vtt_practical_amount_payable or 0.0) / acc.vtt_planned_amount_payable)
            else:
                acc.vtt_amount_payable_percentage = 0.0

    @api.depends('vtt_budget_line_ids', 'vtt_budget_line_ids.planned_amount')
    def _compute_planned_amount(self):
        for account in self:
            budgets = account.vtt_budget_line_ids.filtered(lambda l: l.product_id and l.type == 'item')
            budgets_available = budgets.filtered(lambda l: l.price_unit > 0)
            budgets_payable = budgets - budgets_available

            available = sum(budgets_available.mapped('planned_amount'))
            payable = sum(budgets_payable.mapped('planned_amount'))

            account.vtt_planned_amount_available = available
            account.vtt_planned_amount_payable = payable

    @api.depends('vtt_budget_line_ids', 'vtt_budget_line_ids.practical_amount')
    def _compute_practical_amount(self):
        for account in self:
            budgets = account.vtt_budget_line_ids.filtered(lambda l: l.product_id and l.type == 'item')
            budgets_available = budgets.filtered(lambda l: l.price_unit > 0)
            budgets_payable = budgets - budgets_available

            available = sum(budgets_available.mapped('practical_amount'))
            payable = sum(budgets_payable.mapped('practical_amount'))

            account.vtt_practical_amount_available = available
            account.vtt_practical_amount_payable = payable