# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command


class AnalyticBudgetTemplate(models.Model):
    _name = 'vtt.analytic.budget.template'
    _description = 'Analytic Budget Template'

    name = fields.Char('Name')
    line_ids = fields.One2many('vtt.analytic.budget.template.line',
                               'analytic_template_id',
                               'Budget Categories')

    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def copy(self, default=None):
        default = dict(default or {})
        if not default.get('name'):
            default['name'] = _("%s (copy)", self.name)
        res = super().copy(default)
        if res:
            lines = self.prepare_budget_data(budget_template_id=res.id)
            res.write({'line_ids': lines})
        return res

    def budget_custom_import(self):
        self.ensure_one()
        self.re_arrange_lines()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vtt.budget.custom.import.wz',
            'name': _("Import Budget Items Wizard"),
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'budget_template_id': self.id,
                'default_budget_template_id': self.id,
            }
        }

    def prepare_budget_data(self, account_analytic_id=False, budget_template_id=False):
        self.ensure_one()
        lines = self.line_ids.filtered(lambda l: not l.parent_id)
        vals = [l.prepare_budget_data(account_analytic_id, budget_template_id) for l in lines]
        return vals

    def re_arrange_lines(self):
        self.ensure_one()
        lines = self.line_ids
        line_ids = []
        counter = 0
        main_section = lines.filtered(lambda l: not l.parent_id).sorted('sequence')
        for s in main_section:
            s_lines = lines.filtered(lambda l: s.full_path in l.full_path).sorted('full_sequence')
            for sl in s_lines:
                line_ids.append([sl.id, counter])
                counter += 1
        if line_ids:
            self.write({'line_ids': [(Command.update(sl[0], {'sequence': sl[1]})) for sl in line_ids]})


class AnalyticBudgetTemplateLine(models.Model):
    _name = 'vtt.analytic.budget.template.line'
    _description = 'Analytic Budget Template Line'
    _order = 'sequence, full_path, level, id'

    def get_default_sequence(self):
        lines = self.analytic_template_id.mapped('line_ids')
        if lines:
            return max(lines.mapped('sequence')) + 1
        else:
            return 10

    name = fields.Char('Name')
    analytic_template_id = fields.Many2one('vtt.analytic.budget.template', 'Budget Template', ondelete='cascade')

    sequence = fields.Integer('Sequence', default=get_default_sequence)

    parent_id = fields.Many2one('vtt.analytic.budget.template.line', 'Parent Category',
                                index=True, domain="['!', ('id', 'child_of', id)]",
                                ondelete='cascade')
    child_ids = fields.One2many('vtt.analytic.budget.template.line', 'parent_id', "Items")

    type = fields.Selection([
        ('group', 'Group'),
        ('item', 'Item')
    ], 'Type', default='item')
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note')
    ], 'Display Type', default=False)

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

    level = fields.Integer('Level', compute='_compute_level', store=True)
    full_path = fields.Char('Full Path', compute='_compute_full_path', store=True,
                            precompute=True, index=True)

    full_sequence = fields.Char('Full Sequence', compute='_compute_full_sequence', store=True, precompute=True)

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
            line.product_uom = line.product_id.uom_id.id

    def get_by_full_path(self, path):
        return self.filtered(lambda line: line.full_path == path)

    def prepare_budget_data(self, account_analytic_id, budget_template_id):
        vals = {
            'name': self.name,
            'type': self.type,
            'sequence': self.sequence,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_uom_qty,
            # 'account_analytic_id': account_analytic_id,
        }
        if account_analytic_id:
            vals['account_analytic_id'] = account_analytic_id
        if budget_template_id:
            vals['analytic_template_id'] = budget_template_id
        if self.child_ids:
            vals['child_ids'] = [c.prepare_budget_data(account_analytic_id, budget_template_id) for c in self.child_ids]
        return [0, 0, vals]

    def action_add_item_wz(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vtt.budget.add.item.wz',
            'name': _("Add Budget Item Wizard"),
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'budget_template_line_id': self.id,
                'default_budget_template_line_id': self.id,
            }
        }
