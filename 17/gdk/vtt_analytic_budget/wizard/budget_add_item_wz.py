# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command


class BudgetAddItemWizard(models.TransientModel):
    _name = 'vtt.budget.add.item.wz'
    _description = 'Add Budget Item Wizard'

    budget_template_line_id = fields.Many2one('vtt.analytic.budget.template.line', 'Category')
    budget_analytic_line_id = fields.Many2one('vtt.analytic.budget.line', 'Category')

    type = fields.Selection([
        ('group', 'Group'),
        ('item', 'Item')
    ], 'Type', default='group', required=True)

    item_ids = fields.One2many('vtt.budget.add.item.wz.line', 'wz_id', 'Item')

    def apply_new_item(self):
        if self.item_ids and (self.budget_template_line_id or self.budget_analytic_line_id):
            item_vals = []
            item_type = self.type
            if self.budget_template_line_id:
                budget_id = self.budget_template_line_id.analytic_template_id
                parent_id = self.budget_template_line_id
            else:
                budget_id = self.budget_analytic_line_id.account_analytic_id
                parent_id = self.budget_analytic_line_id
            if parent_id.child_ids:
                item_sequence = max(parent_id.child_ids.mapped('sequence'))
            else:
                item_sequence = parent_id.sequence
            for i in self.item_ids:
                vals = {
                    'name': i.name,
                    'product_id': i.product_id.id,
                    'product_uom': i.product_uom.id,
                    'product_uom_qty': i.product_uom_qty,
                    'type': item_type,
                    'parent_id': parent_id.id,
                    'sequence': item_sequence,
                }

                if self.budget_template_line_id:
                    vals['analytic_template_id'] = budget_id.id
                else:
                    vals['account_analytic_id'] = budget_id.id
                    vals['price_unit'] = i.price_unit

                item_vals.append(Command.create(vals))

            if item_vals:
                if self.budget_template_line_id:
                    budget_id.write({'line_ids': item_vals})
                else:
                    budget_id.write({'vtt_budget_line_ids': item_vals})

            """if self.budget_template_line_id:
                budget_id = self.budget_template_line_id.analytic_template_id
                if self.budget_template_line_id.child_ids:
                    item_sequence = max(self.budget_template_line_id.child_ids.mapped('sequence'))
                else:
                    item_sequence = self.budget_template_line_id.sequence

                vals = [(0, 0, {
                    'name': i.name,
                    'product_id': i.product_id.id,
                    'product_uom': i.product_uom.id,
                    'product_uom_qty': i.product_uom_qty,
                    'type': item_type,
                    'analytic_template_id': budget_id.id,
                    'parent_id': self.budget_template_line_id.id,
                    'sequence': item_sequence
                }) for i in self.item_ids]
            else:
                budget_id = self.budget_analytic_line_id.account_analytic_id
                if self.budget_analytic_line_id.child_ids:
                    item_sequence = max(self.budget_analytic_line_id.child_ids.mapped('sequence'))
                else:
                    item_sequence = self.budget_analytic_line_id.sequence

                vals = [(0, 0, {
                    'name': i.name,
                    'product_id': i.product_id.id,
                    'product_uom': i.product_uom.id,
                    'product_uom_qty': i.product_uom_qty,
                    'price_unit': i.price_unit,
                    'type': item_type,
                    'account_analytic_id': budget_id.id,
                    'parent_id': self.budget_analytic_line_id.id,
                    'sequence': item_sequence
                }) for i in self.item_ids]

            budget_id.write({'line_ids': vals})"""


class BudgetAddItemWizardLine(models.TransientModel):
    _name = 'vtt.budget.add.item.wz.line'
    _description = 'Add Budget Item Wizard Line'

    wz_id = fields.Many2one('vtt.budget.add.item.wz', 'Wizard')

    name = fields.Char('Name')

    product_id = fields.Many2one('product.product', 'Product')
    product_uom = fields.Many2one(
        'uom.uom', "UoM", domain="[('category_id', '=', product_uom_category_id)]",
        compute="_compute_product_uom", store=True, readonly=False, precompute=True,
    )
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_qty = fields.Float(
        'Quantity',
        digits='Product Unit of Measure',
        default=0.0)

    price_unit = fields.Float('Price Unit', compute='_compute_price_unit', store=True, readonly=False, precompute=True)
    amount = fields.Float('Amount', compute='_compute_amount')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.name = self.product_id.name

    @api.depends('product_id', 'product_uom')
    def _compute_price_unit(self):
        currency = self.env.company.currency_id
        pricelist_item = self.env['product.pricelist.item']
        for line in self:
            if line.product_id and line.product_uom:
                price = pricelist_item._compute_price(
                    product=line.product_id,
                    quantity=line.product_uom_qty,
                    uom=line.product_uom,
                    date=fields.Datetime.now(),
                    currency=currency,
                )
            else:
                price = 0.0
            line.price_unit = price

    @api.depends('price_unit', 'product_uom_qty')
    def _compute_amount(self):
        for line in self:
            line.amount = line.price_unit * line.product_uom_qty

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            line.product_uom = line.product_id.uom_id.id