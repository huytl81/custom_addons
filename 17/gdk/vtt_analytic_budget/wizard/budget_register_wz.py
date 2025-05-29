# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BudgetRegisterWizard(models.TransientModel):
    _name = 'vtt.budget.register.wz'
    _description = 'Budget Register Wizard'

    analytic_line_ids = fields.Many2many('account.analytic.line',
                                         'analytic_line_budget_register_wz_rel',
                                         string='Analytic Line')
    analytic_next_ids = fields.Many2many('account.analytic.line',
                                         'analytic_line_budget_register_wz_next_rel',
                                         string='Register Lines',
                                         default=lambda self: self.env.context.get('active_ids', []))
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    budget_available_ids = fields.Many2many('vtt.analytic.budget.line', string='Budget Category', compute='_compute_available_budget')
    budget_line_id = fields.Many2one('vtt.analytic.budget.line', 'Budget Category')

    budget_warn = fields.Boolean(compute='_compute_budget_warn')

    @api.depends('analytic_line_ids')
    def _compute_budget_warn(self):
        for wz in self:
            if wz.analytic_line_ids.mapped('vtt_budget_line_id'):
                wz.budget_warn = True
            else:
                wz.budget_warn = False

    @api.onchange('analytic_next_ids')
    def onchange_analytic_next_ids(self):
        # Account
        analytic_account = self.analytic_next_ids.mapped('account_id')
        self.account_analytic_id = analytic_account.id
        # Product
        products = self.analytic_next_ids.mapped('product_id')
        product = products[0]
        lines = self.analytic_next_ids.filtered(lambda l: l.product_id == product)
        self.analytic_line_ids = lines.ids

    @api.depends('analytic_line_ids')
    def _compute_available_budget(self):
        for wz in self:
            account = wz.account_analytic_id
            products = wz.analytic_line_ids.mapped('product_id')
            # products = wz.analytic_line_id.product_id
            budget_all = account.vtt_budget_line_ids
            budget_product_lines = budget_all.filtered(lambda b: b.product_id in products)
            budget_available_lines = wz.env['vtt.analytic.budget.line']
            for b in budget_product_lines:
                b_available = budget_all.filtered(lambda bb: bb.full_path in b.full_path)
                budget_available_lines |= b_available
            wz.budget_available_ids = budget_available_lines.ids

    def apply_budget_register(self):
        target_categ = self.budget_line_id
        if self.budget_line_id.type == 'item':
            target_categ = self.budget_line_id.parent_id
        product = self.analytic_line_ids.mapped('product_id')
        if product == self.budget_line_id.product_id and self.budget_line_id.type == 'item':
            self.analytic_line_ids.vtt_budget_line_id = self.budget_line_id.id
        elif product != self.budget_line_id.product_id:
            valid_lines = target_categ.child_ids.filtered(lambda l: l.product_id == product)
            if valid_lines:
                self.analytic_line_ids.vtt_budget_line_id = valid_lines[0].id
            else:
                vals = {
                    'account_analytic_id': self.account_analytic_id.id,
                    'name': product.name,
                    'sequence': target_categ.child_ids and target_categ.child_ids[0].sequence or target_categ.sequence,
                    'parent_id': target_categ.id,
                    'type': 'item',
                    'product_id': product.id,
                    # 'product_uom': self.analytic_line_ids.mapped('product_uom_id')[0]id,
                    'product_uom': product.uom_id.id,
                    # 'price_unit': self.analytic_line_id.amount / (self.analytic_line_id.unit_amount or 1.0),
                    'price_unit': 0.0,
                    'product_uom_qty': 0.0,
                    'is_incurred': True,
                }
                new_budget = self.env['vtt.analytic.budget.line'].create(vals)
                self.analytic_line_ids.vtt_budget_line_id = new_budget.id

        nexts = self.analytic_next_ids - self.analytic_line_ids
        if nexts:
            action = self.env['ir.actions.act_window']._for_xml_id('vtt_analytic_budget.vtt_act_window_budget_register_wz')
            action['context'] = {'active_ids': nexts.ids}
            return action
        else:
            return {'type': 'ir.actions.act_window_close'}