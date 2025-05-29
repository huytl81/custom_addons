# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AnalyticBudgetLine(models.Model):
    _name = 'vtt.analytic.budget.line'
    _description = 'Analytic Budget Line'
    _order = 'sequence, full_path, level, id'

    def get_default_sequence(self):
        lines = self.account_analytic_id.mapped('vtt_budget_line_ids')
        if lines:
            return max(lines.mapped('sequence')) + 1
        else:
            return 10

    name = fields.Char('Name')
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account')

    sequence = fields.Integer('Sequence', default=get_default_sequence)

    parent_id = fields.Many2one('vtt.analytic.budget.line', 'Budget Category',
                                index=True, domain="['!', ('id', 'child_of', id)]")
    child_ids = fields.One2many('vtt.analytic.budget.line', 'parent_id', "Items", ondelete='cascade')
    company_id = fields.Many2one(related='account_analytic_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    # amount_type = fields.Selection([
    #     ('cost', 'Cost'),
    #     ('revenue', 'Revenue')
    # ], 'Type', required=True, default='cost')
    type = fields.Selection([
        ('group', 'Group'),
        ('item', 'Item')
    ], 'Type', default='item')

    level = fields.Integer('Level', compute='_compute_level', store=True)
    full_path = fields.Char('Full Path', compute='_compute_full_path', store=True,
                            precompute=True, index=True)
    full_sequence = fields.Char('Full Sequence', compute='_compute_full_sequence', store=True, precompute=True)

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

    price_unit = fields.Float(
        string="Unit Price",
        compute='_compute_price_unit',
        digits='Product Price',
        store=True, readonly=False, precompute=True)

    analytic_line_ids = fields.One2many('account.analytic.line', 'vtt_budget_line_id', 'Practicals')

    planned_amount = fields.Monetary(
        'Planned Amount', compute='_compute_planned_amount',
        store=True, precompute=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")

    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Practical Amount',
        store=True, precompute=True,
        help="Amount really earned/spent.")

    percentage = fields.Float(
        compute='_compute_percentage', string='Achievement',
        help="Comparison between practical and planned amount. This measure tells you if you are below or over budget.")

    is_above_budget = fields.Boolean(compute='_is_above_budget')
    is_incurred = fields.Boolean('Incurred', default=False)

    def change_price_unit_side(self):
        self.price_unit = -self.price_unit

    def get_by_full_path(self, path):
        return self.filtered(lambda line: line.full_path == path)

    @api.depends('parent_id', 'parent_id.full_sequence', 'sequence')
    def _compute_full_sequence(self):
        for line in self:
            if line.parent_id:
                line.full_sequence = f'{line.parent_id.full_sequence}_{line.sequence}'
            else:
                line.full_sequence = str(line.sequence)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and not self.name:
            self.name = self.product_id.name

    @api.depends('parent_id', 'parent_id.full_path')
    def _compute_full_path(self):
        for line in self:
            if line.parent_id:
                line.full_path = f'{line.parent_id.full_path}/{line.name}'
            else:
                line.full_path = line.name or ''

    @api.depends('parent_id', 'parent_id.level')
    def _compute_level(self):
        for line in self:
            if line.parent_id:
                line.level = line.parent_id.level + 1
            else:
                line.level = 0

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            line.product_uom = line.product_id and line.product_id.uom_id.id or False

    @api.depends('product_id', 'product_uom')
    def _compute_price_unit(self):
        pricelist_item = self.env['product.pricelist.item']
        for line in self:
            if line.product_id and line.product_uom:
                price = pricelist_item._compute_price(
                    product=line.product_id,
                    quantity=line.product_uom_qty,
                    uom=line.product_uom,
                    date=fields.Datetime.now(),
                    currency=line.company_id.currency_id,
                )
            else:
                price = 0.0
            line.price_unit = price

    @api.depends('price_unit', 'product_uom_qty', 'child_ids', 'child_ids.planned_amount')
    def _compute_planned_amount(self):
        for line in self:
            if line.type == 'item':
                line.planned_amount = line.price_unit * line.product_uom_qty
            else:
                line.planned_amount = sum(line.child_ids.filtered(lambda l: l.type == 'item').mapped('planned_amount'))

    @api.depends('analytic_line_ids', 'analytic_line_ids.amount', 'child_ids', 'child_ids.practical_amount')
    def _compute_practical_amount(self):
        for line in self:
            if line.type == 'item':
                line.practical_amount = sum(line.analytic_line_ids.mapped('amount'))
            else:
                line.practical_amount = sum(line.child_ids.filtered(lambda l: l.type == 'item').mapped('practical_amount'))

    def _compute_percentage(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.planned_amount)
            else:
                line.percentage = 0.00

    def _is_above_budget(self):
        for line in self:
            if line.planned_amount >= 0:
                line.is_above_budget = line.practical_amount > line.planned_amount
            else:
                line.is_above_budget = line.practical_amount < line.planned_amount

    def action_add_item_wz(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vtt.budget.add.item.wz',
            'name': _("Add Budget Item Wizard"),
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'budget_analytic_line_id': self.id,
                'default_budget_analytic_line_id': self.id,
            }
        }