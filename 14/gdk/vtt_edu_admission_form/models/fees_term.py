# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _


class FeesTerm(models.Model):
    _inherit = 'op.fees.terms'

    product_id = fields.Many2one('product.product', 'Product', domain=[('type', '=', 'service')])

    value_type = fields.Selection([
        ('percent', 'Percentage'),
        ('exact', 'Exact Value')
    ], 'Value Type', default='percent')

    @api.model
    def create(self, vals):
        res = super(FeesTerm, self).create(vals)
        if not res.line_ids:
            raise exceptions.AccessError(_("Fees Terms must be Required!"))
        total = 0.0
        if res.value_type == 'percent':
            for line in res.line_ids:
                if line.value:
                    total += line.value
            if total != 100.0:
                raise exceptions.AccessError(
                    _("Fees terms must be divided as such sum up in 100%"))
        return res


class FeesTermLine(models.Model):
    _inherit = 'op.fees.terms.line'

    value_type = fields.Selection(related='fees_id.value_type')
    exact_value = fields.Float('Value', compute='_compute_exact_value', store=True)

    fees_terms = fields.Selection(related='fees_id.fees_terms')

    @api.depends('fees_element_line.exact_value')
    def _compute_exact_value(self):
        value = 0.0
        for e in self.fees_element_line:
            value += e.exact_value
        self.exact_value = value


class FeesElement(models.Model):
    _inherit = 'op.fees.element'

    value_type = fields.Selection(related='fees_terms_line_id.fees_id.value_type')
    exact_value = fields.Float('Value')

    type = fields.Selection([
        ('compulsive', 'Compulsive'),
        ('selective', 'Selective')
    ], 'Type', default='compulsive')