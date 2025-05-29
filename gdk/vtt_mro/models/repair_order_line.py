# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare
from datetime import timedelta
from odoo.tools.mail import html2plaintext, is_html_empty
from odoo.fields import Command
from collections import defaultdict


class RepairOrderLine(models.Model):
    _name = 'vtt.repair.order.line'
    _description = 'Repair Diagnosis Line'
    _inherit = 'analytic.mixin'
    _rec_names_search = ['name', 'repair_order_id.name']
    _order = 'repair_order_id, sequence, id'

    name = fields.Char('Description')
    repair_order_id = fields.Many2one('vtt.repair.order', 'Order')
    diagnosis_line_id = fields.Many2one('vtt.repair.diagnosis.line', 'Diagnosis')

    product_id = fields.Many2one('product.product', 'Product')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure',
                             compute='_compute_product_uom',
                             store=True, readonly=False, precompute=True, ondelete='restrict',)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_uom_qty = fields.Float('Quantity', default=1.0)
    # product_type = fields.Selection([
    #     ('service', 'Service'),
    #     ('product', 'Product')
    # ], 'Product Type')

    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one(related="repair_order_id.company_id", index=True, store=True)
    currency_id = fields.Many2one(related='repair_order_id.currency_id',
                                  depends=['repair_order_id.currency_id'],
                                  store=True, precompute=True)

    order_partner_id = fields.Many2one(
        related='repair_order_id.partner_id',
        string="Customer",
        store=True, index=True, precompute=True)

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ], string='Display Type', default=False)

    state = fields.Selection(
        related='repair_order_id.state',
        string="Order Status",
        copy=False, store=True, precompute=True)

    # Amount
    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        compute='_compute_tax_id',
        store=True, readonly=False,
        context={'active_test': False},
        check_company=True)

    price_unit = fields.Float(
        string="Unit Price",
        digits='Product Price',
        compute='_compute_price_unit',
        store=True, readonly=False, required=True)

    discount = fields.Float(
        string="Discount (%)",
        digits='Discount',
        store=True, readonly=False)

    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount',
        store=True)
    price_tax = fields.Float(
        string="Total Tax",
        compute='_compute_amount',
        store=True)
    price_total = fields.Monetary(
        string="Total",
        compute='_compute_amount',
        store=True)
    price_reduce_taxexcl = fields.Monetary(
        string="Price Reduce Tax excl",
        compute='_compute_price_reduce_taxexcl',
        store=True)
    price_reduce_taxinc = fields.Monetary(
        string="Price Reduce Tax incl",
        compute='_compute_price_reduce_taxinc',
        store=True)

    # Delivery
    route_id = fields.Many2one('stock.route', string='Route', domain=[('sale_selectable', '=', True)],
                               ondelete='restrict', check_company=True)
    move_ids = fields.One2many('stock.move', 'repair_line_id', string='Stock Moves')
    qty_delivered = fields.Float(
        string="Delivery Quantity",
        compute='_compute_qty_delivered',
        digits='Product Unit of Measure',
        store=True, readonly=False, copy=False)

    # Invoicing
    qty_invoiced = fields.Float(
        string="Invoiced Quantity",
        compute='_compute_qty_invoiced',
        digits='Product Unit of Measure',
        store=True)
    qty_to_invoice = fields.Float(
        string="Quantity To Invoice",
        compute='_compute_qty_to_invoice',
        digits='Product Unit of Measure',
        store=True)

    analytic_line_ids = fields.One2many(
        comodel_name='account.analytic.line', inverse_name='repair_order_line_id',
        string="Analytic lines")

    invoice_lines = fields.Many2many(
        comodel_name='account.move.line',
        relation='repair_order_line_invoice_rel', column1='repair_order_line_id', column2='invoice_line_id',
        string="Invoice Lines",
        copy=False)

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        for line in self:
            qty_invoiced = 0.0
            for invoice_line in line._get_invoice_lines():
                if invoice_line.move_id.state != 'cancel' or invoice_line.move_id.payment_state == 'invoicing_legacy':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.uom_id)
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(invoice_line.quantity,
                                                                                      line.uom_id)
            line.qty_invoiced = qty_invoiced

    def _get_invoice_lines(self):
        self.ensure_one()
        if self._context.get('accrual_entry_date'):
            return self.invoice_lines.filtered(
                lambda l: l.move_id.invoice_date and l.move_id.invoice_date <= self._context['accrual_entry_date']
            )
        else:
            return self.invoice_lines

    @api.depends('qty_invoiced', 'qty_delivered', 'product_uom_qty', 'state')
    def _compute_qty_to_invoice(self):
        for line in self:
            if line.state not in ('new', 'cancel') and not line.display_type:
                if line.product_id.invoice_policy == 'order':
                    line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
                else:
                    line.qty_to_invoice = line.qty_delivered - line.qty_invoiced
            else:
                line.qty_to_invoice = 0

    @api.depends('repair_order_id.partner_id', 'product_id')
    def _compute_analytic_distribution(self):
        for line in self:
            if not line.display_type and line.product_id:
                distribution = line.env['account.analytic.distribution.model']._get_distribution({
                    "product_id": line.product_id.id,
                    "product_categ_id": line.product_id.categ_id.id,
                    "partner_id": line.repair_order_id.partner_id.id,
                    "partner_category_id": line.repair_order_id.partner_id.category_id.ids,
                    "company_id": line.company_id.id,
                })
                line.analytic_distribution = distribution or line.analytic_distribution

    def _prepare_invoice_line(self, **optional_values):
        self.ensure_one()
        res = {
            'display_type': self.display_type or 'product',
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.uom_id.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [Command.set(self.tax_id.ids)],
            'repair_order_line_ids': [Command.link(self.id)],
            # 'is_downpayment': self.is_downpayment,
        }
        analytic_account_id = self.repair_order_id.analytic_account_id.id
        if self.analytic_distribution and not self.display_type:
            res['analytic_distribution'] = self.analytic_distribution
        if analytic_account_id and not self.display_type:
            analytic_account_id = str(analytic_account_id)
            if 'analytic_distribution' in res:
                res['analytic_distribution'][analytic_account_id] = res['analytic_distribution'].get(analytic_account_id, 0) + 100
            else:
                res['analytic_distribution'] = {analytic_account_id: 100}
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res

    def _get_invoice_line_sequence(self, new=0, old=0):
        return new or old

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['vtt.repair.order.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes, comp = None, company
                while not taxes and comp:
                    taxes = taxes_by_product_company[(line.product_id, comp)]
                    comp = comp.parent_id
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.repair_order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                cache_key += line._get_custom_compute_tax_cache_key()
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

    def _get_custom_compute_tax_cache_key(self):
        return tuple()

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_id:
                continue
            else:
                if not line.uom_id or (line.product_id.uom_id.id != line.uom_id.id):
                    line.uom_id = line.product_id.uom_id

    @api.depends('product_id', 'uom_id', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            if line.product_id and line.uom_id:
                price = line.with_company(line.company_id)._get_unit_price()
                line.price_unit = price
            else:
                if line.price_unit:
                    continue
                else:
                    line.price_unit = 0.0

    def _get_unit_price(self):
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_item = self.env['product.pricelist.item']

        price = pricelist_item._compute_price(
            product=self.product_id,
            quantity=self.product_uom_qty or 1.0,
            uom=self.uom_id,
            date=self.repair_order_id.dt_order,
            currency=self.currency_id,
        )

        return price

    def _get_lang(self):
        """Determine language to use for translated description"""
        return self.repair_order_id.partner_id.lang or self.env.user.lang

    def _get_procurement_group(self):
        return self.repair_order_id.procurement_group_id

    def _prepare_procurement_group_vals(self):
        return {
            'name': self.repair_order_id.name,
            'move_type': 'direct',
            'repair_order_id': self.repair_order_id.id,
            'partner_id': self.repair_order_id.partner_id.id,
        }

    def _create_procurement(self, product_qty, procurement_uom, values):
        self.ensure_one()
        return self.env['procurement.group'].Procurement(
            self.product_id, product_qty, procurement_uom, self.repair_order_id.partner_id.property_stock_customer,
            self.product_id.display_name, self.repair_order_id.name, self.repair_order_id.company_id, values)

    def _get_qty_procurement(self, previous_product_uom_qty=False):
        self.ensure_one()
        qty = 0.0
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty_to_compute = move.quantity if move.state == 'done' else move.product_uom_qty
            qty += move.product_uom._compute_quantity(qty_to_compute, self.uom_id, rounding_method='HALF-UP')
        for move in incoming_moves:
            qty_to_compute = move.quantity if move.state == 'done' else move.product_uom_qty
            qty -= move.product_uom._compute_quantity(qty_to_compute, self.uom_id, rounding_method='HALF-UP')
        return qty

    def _prepare_procurement_values(self, group_id=False):
        self.ensure_one()
        values = {}
        # Use the delivery date if there is else use date_order and lead time
        date_deadline = self.repair_order_id.dt_deadline or (self.repair_order_id.dt_order + timedelta(days=self.product_id.sale_delay or 0.0))
        date_planned = date_deadline - timedelta(days=self.repair_order_id.company_id.security_lead)
        product = self.product_id.with_context(lang=self._get_lang())
        # description_picking = product._get_description(self.picking_type_id)
        description_picking = html2plaintext(product.description) if not is_html_empty(product.description) else product.name
        values.update({
            'group_id': group_id,
            'repair_line_id': self.id,
            'date_planned': date_planned,
            'date_deadline': date_deadline,
            'route_ids': self.route_id,
            'warehouse_id': self.repair_order_id.warehouse_id or False,
            'partner_id': self.repair_order_id.partner_id.id,
            # 'product_description_variants': self.with_context(lang=self.repair_order_id.partner_id.lang)._get_sale_order_line_multiline_description_variants(),
            'product_description_variants': description_picking,
            'company_id': self.repair_order_id.company_id,
            # 'product_packaging_id': self.product_packaging_id,
            'sequence': self.sequence,
        })
        return values

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        if self._context.get("skip_procurement"):
            return True
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        procurements = []
        for line in self:
            line = line.with_company(line.company_id)
            if line.state not in ('confirm', 'under_repair', 'repaired') or line.repair_order_id.locked or not line.product_id or not line.product_id.type in ('consu', 'product'):
                continue
            qty = line._get_qty_procurement(previous_product_uom_qty)
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) == 0:
                continue

            group_id = line._get_procurement_group()
            if not group_id:
                group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
                line.repair_order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.repair_order_id.partner_id:
                    updated_vals.update({'partner_id': line.repair_order_id.partner_id.id})
                if group_id.move_type != 'direct':
                    updated_vals.update({'move_type': 'direct'})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            product_qty = line.product_uom_qty - qty

            line_uom = line.uom_id
            quant_uom = line.product_id.uom_id
            product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
            procurements.append(line._create_procurement(product_qty, procurement_uom, values))
        if procurements:
            self.env['procurement.group'].run(procurements)

        # This next block is currently needed only because the scheduler trigger is done by picking confirmation rather than stock.move confirmation
        orders = self.mapped('repair_order_id')
        for order in orders:
            pickings_to_confirm = order.picking_ids.filtered(lambda p: p.state not in ['cancel', 'done'])
            if pickings_to_confirm:
                # Trigger the Scheduler for Pickings
                pickings_to_confirm.action_confirm()
        return True

    @api.depends('move_ids.state', 'move_ids.scrapped', 'move_ids.quantity', 'move_ids.product_uom')
    def _compute_qty_delivered(self):
        for line in self:
            if line.product_id:
                if line.product_id.type == 'service':
                    if line.state in ('under_repair', 'repaired', 'done'):
                        line.qty_delivered = line.product_uom_qty
                    else:
                        line.qty_delivered = 0.0
                else:
                    qty = 0.0
                    outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()
                    for move in outgoing_moves:
                        if move.state != 'done':
                            continue
                        qty += move.product_uom._compute_quantity(move.quantity, line.uom_id, rounding_method='HALF-UP')
                    for move in incoming_moves:
                        if move.state != 'done':
                            continue
                        qty -= move.product_uom._compute_quantity(move.quantity, line.uom_id, rounding_method='HALF-UP')
                    line.qty_delivered = qty

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env['stock.move']
        incoming_moves = self.env['stock.move']

        moves = self.move_ids.filtered(lambda r: r.state != 'cancel' and not r.scrapped and self.product_id == r.product_id)
        # if self._context.get('accrual_entry_date'):
        #     moves = moves.filtered(lambda r: fields.Date.context_today(r, r.date) <= self._context['accrual_entry_date'])

        for move in moves:
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                    outgoing_moves |= move
            elif move.location_dest_id.usage != "customer" and move.to_refund:
                incoming_moves |= move

        return outgoing_moves, incoming_moves

    def _convert_to_tax_base_line_dict(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.repair_order_id.partner_id,
            currency=self.repair_order_id.currency_id,
            product=self.product_id,
            taxes=self.tax_id,
            price_unit=self.price_unit,
            quantity=self.product_uom_qty,
            discount=self.discount,
            price_subtotal=self.price_subtotal,
            **kwargs,
        )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the RO line.
        """
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes([
                line._convert_to_tax_base_line_dict()
            ])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']

            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })

    @api.depends('price_subtotal', 'product_uom_qty')
    def _compute_price_reduce_taxexcl(self):
        for line in self:
            line.price_reduce_taxexcl = line.price_subtotal / line.product_uom_qty if line.product_uom_qty else 0.0

    @api.depends('price_total', 'product_uom_qty')
    def _compute_price_reduce_taxinc(self):
        for line in self:
            line.price_reduce_taxinc = line.price_total / line.product_uom_qty if line.product_uom_qty else 0.0

    def write(self, values):
        lines = self.env['vtt.repair.order.line']
        if 'product_uom_qty' in values or 'product_id' in values:
            lines = self.filtered(lambda r: r.state in ('confirm', 'under_repair', 'repaired'))

        previous_product_uom_qty = {line.id: line.product_uom_qty for line in lines}
        res = super(RepairOrderLine, self).write(values)
        if lines:
            lines._action_launch_stock_rule(previous_product_uom_qty)
        return res
