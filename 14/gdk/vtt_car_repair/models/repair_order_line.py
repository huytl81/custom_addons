# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.exceptions import UserError, ValidationError
import json


class VttCarRepairOrderLine(models.Model):
    _name = 'vtt.car.repair.order.line'
    _description = 'Car Repair Order Line'
    _order = 'repair_id, sequence, id'

    # def _get_product_uom_domain(self):
    #     if self.product_id:
    #         return [('category_id', '=', self.product_uom_category_id)]
    #     else:
    #         return []

    @api.depends('price_unit', 'discount')
    def _get_price_reduce(self):
        for line in self:
            line.price_reduce = line.price_unit * (1.0 - line.discount / 100.0)

    @api.depends('price_total', 'product_uom_qty')
    def _get_price_reduce_tax(self):
        for line in self:
            line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.depends('price_subtotal', 'product_uom_qty')
    def _get_price_reduce_notax(self):
        for line in self:
            line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

    name = fields.Text('Description', index=True, required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    repair_id = fields.Many2one(
        'vtt.car.repair.order', 'Repair Order Reference',
        index=True, ondelete='cascade', required=True)
    company_id = fields.Many2one(
        related="repair_id.company_id", index=True, store=True)
    currency_id = fields.Many2one(
        related="repair_id.currency_id")

    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True,
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]")
    product_uom_qty = fields.Float('Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

    product_uom_domain = fields.Char('UoM Domain', compute='_compute_uom_domain')

    @api.depends('product_id')
    def _compute_uom_domain(self):
        for line in self:
            if line.product_id:
                domain = [('category_id', '=', line.product_id.uom_id.category_id.id)]
            else:
                domain = []
            line.product_uom_domain = json.dumps(domain)

    price_subtotal = fields.Float('Subtotal', compute='_compute_price_subtotal', store=True, digits='Product Price')
    price_taxes = fields.Float('Tax Amount', compute='_compute_price_subtotal', store=True, digits='Product Price')
    price_total = fields.Float('Total', compute='_compute_price_subtotal', store=True, digits='Product Price')
    # Discount
    amount_reduced = fields.Float('Reduced Amount', compute='_compute_price_subtotal', store=True, digits='Product Price')
    price_reduce = fields.Float('Price Reduced', readonly=True, digits='Product Price', default=0.0, compute='_get_price_reduce')
    price_reduce_taxinc = fields.Monetary(compute='_get_price_reduce_tax', string='Price Reduce Tax inc', readonly=True, store=True)
    price_reduce_taxexcl = fields.Monetary(compute='_get_price_reduce_notax', string='Price Reduce Tax excl', readonly=True, store=True)

    tax_id = fields.Many2many(
        'account.tax', 'vtt_car_repair_line_tax', string='Taxes',
        domain="[('type_tax_use','=','sale'), ('company_id', '=', company_id)]", check_company=True)
    invoice_line_id = fields.Many2one('account.move.line', 'Invoice Line', copy=False, readonly=True,
                                      check_company=True)
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)
    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    technical_user_id = fields.Many2one(related='repair_id.technical_user_id')

    repair_state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], 'Repair Status', default='draft',
        copy=False, readonly=True,
        help='The repair status of a repair line is set automatically to the one of the linked repair order.')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], 'Status', default='draft',
        copy=False, readonly=True, required=True,
        help='The status of a repair line is set automatically to the one of the linked repair order.')

    vtt_car_service_id = fields.Many2one('fleet.service.type', 'Service')

    # Display note and section
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], 'Display Type', default=False)

    in_delivery_qty = fields.Float('In Delivery Quantity', compute='_compute_in_delivery_qty', store=True)

    @api.depends('repair_id.picking_ids.state')
    def _compute_in_delivery_qty(self):
        for line in self:
            pickings = line.repair_id.mapped('picking_ids').filtered(lambda p: p.state != 'cancel')
            moves = pickings.mapped('move_ids_without_package').filtered(lambda m: m.car_repair_line_id == line)
            line.in_delivery_qty = sum([m.product_uom_qty for m in moves])

    @api.depends('price_unit', 'repair_id', 'product_uom_qty', 'product_id', 'discount', 'price_reduce')
    def _compute_price_subtotal(self):
        for line in self:
            # price = line.price_unit - line.price_unit * ((line.discount or 0.0) / 100.0)
            price = line.price_reduce
            taxes = line.tax_id.compute_all(price, line.repair_id.pricelist_id.currency_id,
                                            line.product_uom_qty, line.product_id, line.repair_id.partner_id)
            line.price_subtotal = taxes['total_excluded']
            line.price_total = taxes['total_included']
            line.price_taxes = taxes['total_included'] - taxes['total_excluded']
            line.amount_reduced = line.repair_id.pricelist_id.currency_id.round((line.price_unit - price))

    @api.onchange('repair_id', 'product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        self = self.with_company(self.company_id)
        partner = self.repair_id.partner_id
        if partner and self.product_id:
            fpos = self.env['account.fiscal.position'].get_fiscal_position(partner.id, delivery_id=partner.id)
            self.tax_id = fpos.map_tax(self.product_id.taxes_id, self.product_id, partner).ids
        if partner:
            self = self.with_context(lang=partner.lang)
        product = self.product_id
        # Addition condition for name changing
        if not self.name:
            # self.name = product.display_name
            # Replace for simply use-case
            self.name = product.name
            if product.description_sale:
                if partner:
                    # self.name += '\n' + self.product_id.with_context(lang=partner.lang).description_sale
                    # Show description sale only
                    self.name = self.product_id.with_context(lang=partner.lang).description_sale
                else:
                    # self.name += '\n' + self.product_id.description_sale
                    self.name = self.product_id.description_sale
        self.product_uom = product.uom_id.id
        if self._origin.product_id:
            self.update_price()

    @api.onchange('product_uom')
    def _onchange_product_uom(self):
        if self._origin.product_id:
            self.update_price()
            # partner = self.repair_id.partner_id
            # pricelist = self.repair_id.pricelist_id
            # if pricelist and self.product_id:
            #     price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner,
            #                                         uom_id=self.product_uom.id)
            #     if price is False:
            #         warning = {
            #             'title': _('No valid pricelist line found.'),
            #             'message':
            #                 _(
            #                     "Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
            #         return {'warning': warning}
            #     else:
            #         self.price_unit = price

    def update_price(self):
        partner = self.repair_id.partner_id
        pricelist = self.repair_id.pricelist_id
        if pricelist and self.product_id:
            price = pricelist.get_product_price(self.product_id, self.product_uom_qty, partner,
                                                uom_id=self.product_uom.id)
            if price is False:
                warning = {
                    'title': _('No valid pricelist line found.'),
                    'message':
                        _(
                            "Couldn't find a pricelist line matching this product and quantity.\nYou have to change either the product, the quantity or the pricelist.")}
                return {'warning': warning}
            else:
                self.price_unit = price

    def unlink(self):
        if self.repair_id.state not in ['done', 'cancel']:
            if self.repair_id.invoice_id and self.repair_id.invoice_id.state == 'draft':
                self.invoice_line_id.unlink()
        return super().unlink()

    def get_invoice_line_values(self, group=False):
        self.ensure_one()
        currency = self.repair_id.pricelist_id.currency_id
        company = self.env.company

        if group:
            name = self.repair_id.name + '-' + self.name
        else:
            name = self.name

        invoice_line_vals = {
            'display_type': self.display_type,
            'name': name,
            # 'account_id': not self.display_type and account.id or False,
            'quantity': self.product_uom_qty,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'product_uom_id': self.product_uom.id,
            'price_unit': self.price_unit,
            'product_id': self.product_id.id,
            'car_repair_line_ids': [(4, self.id)],
            'discount': self.discount,
        }

        if not self.display_type:
            account = self.product_id.product_tmpl_id._get_product_accounts()['income']
            if not account:
                raise UserError(_('No account defined for product "%s".', self.product_id.name))
            invoice_line_vals['account_id'] = account.id
        else:
            invoice_line_vals['account_id'] = False

        price = self.price_unit - self.price_unit * ((self.discount or 0.0) / 100.0)
        if currency == company.currency_id:
            balance = -(self.product_uom_qty * price)
            invoice_line_vals.update({
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
            })
        else:
            amount_currency = - (self.product_uom_qty * price)
            balance = self._convert(amount_currency, self.currency_id, company, fields.Date.today())
            invoice_line_vals.update({
                'amount_currency': amount_currency,
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'currency_id': currency.id,
            })

        return invoice_line_vals