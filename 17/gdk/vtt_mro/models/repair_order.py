# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import html_keep_url, is_html_empty, float_is_zero
from odoo.exceptions import AccessError, UserError
from odoo.fields import Command
from itertools import groupby
import logging

_logger = logging.getLogger(__name__)


class RepairOrder(models.Model):
    _name = 'vtt.repair.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Repair Order'
    _order = 'dt_order desc, id desc'

    name = fields.Char('Name', default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', 'Customer', tracking=1)
    partner_invoice_id = fields.Many2one(
        comodel_name='res.partner',
        string="Invoice Address",
        compute='_compute_partner_invoice_id',
        store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    phone = fields.Char('Phone', related='partner_id.phone')
    email = fields.Char('Email', related='partner_id.email')

    dt_order = fields.Datetime('Order Time', default=fields.Datetime.now)
    dt_diagnosis = fields.Datetime('Diagnosis Time')
    dt_confirm = fields.Datetime('Confirmed Time')
    dt_deadline = fields.Datetime('Deadline')

    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment', tracking=2)
    equipment_model_name = fields.Char('Model', related='equipment_id.model_name')
    equipment_manufacture = fields.Char('Manufacture', related='equipment_id.manufacture')
    equipment_manufacture_year = fields.Char('Year', related='equipment_id.manufacture_year')
    equipment_serial_number = fields.Char('Serial Number', related='equipment_id.serial_number')
    equipment_date_warranty = fields.Date('Warranty')
    is_under_warranty = fields.Boolean('Under Warranty', default=False)

    description = fields.Text('Description')

    priority = fields.Selection([
        ('0', 'Very Low'),
        ('1', 'Low'),
        ('2', 'Normal'),
        ('3', 'High')
    ], string='Priority', tracking=20)
    state = fields.Selection([
        ('new', 'Quotation'),
        ('confirm', 'Confirmed'),
        ('under_repair', 'Repairing'),
        ('repaired', 'Repaired'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], 'Status', default='new', tracking=3)

    recipient_id = fields.Many2one('res.users', 'Recipient', default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', 'User', tracking=4)
    user_ids = fields.Many2many('res.users', string='Users')

    dt_start_repair = fields.Datetime('Start Repair')
    dt_end_repair = fields.Datetime('End Repair')

    duration_repair = fields.Float('Repair Duration', default=0.0, compute='_compute_duration_repair', store=True)
    duration_order = fields.Float('Order Duration', default=0.0, compute='_compute_duration_order', store=True)

    dt_done = fields.Datetime('Done Time')

    diagnosis_ids = fields.One2many('vtt.repair.diagnosis', 'repair_order_id', 'Diagnosis')
    diagnosis_count = fields.Integer('Diagnosis Count', compute='_compute_diagnosis_count')

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    company_id = fields.Many2one('res.company', "Company", required=True, readonly=True, default=lambda self: self.env.company)

    line_ids = fields.One2many('vtt.repair.order.line', 'repair_order_id', 'Details')

    # Amount
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=6)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')
    amount_total = fields.Monetary(string="Total", store=True, compute='_compute_amounts', tracking=5)

    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)
    amount_undiscounted = fields.Float(
        string="Amount Before Discount",
        compute='_compute_amount_undiscounted', digits=0)

    note = fields.Html(
        string="Terms and conditions",
        compute='_compute_note',
        store=True, readonly=False, precompute=True)

    locked = fields.Boolean(default=False, copy=False, help="Locked orders cannot be modified.")
    modify_available = fields.Boolean('Modify Available', compute='_compute_modify_available')

    # Delivery
    picking_ids = fields.One2many('stock.picking', 'repair_order_id', string='Transfers')
    picking_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_count')
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', required=True,
        compute='_compute_warehouse_id', store=True, readonly=False, precompute=True,
        check_company=True)
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)
    need_picking = fields.Boolean('Need Delivery', compute='_compute_need_picking')

    # Invoicing
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
             "The default value comes from the customer.",
        domain="[('company_id', '=', company_id)]")

    journal_id = fields.Many2one(
        'account.journal', string="Invoicing Journal",
        compute="_compute_journal_id", store=True, readonly=False, precompute=True,
        domain=[('type', '=', 'sale')], check_company=True,
        help="If set, the SO will invoice in this journal; "
             "otherwise the sales journal with the lowest sequence is used.")

    invoice_count = fields.Integer(string="Invoice Count", compute='_get_invoiced')
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Invoices",
        compute='_get_invoiced',
        search='_search_invoice_ids',
        copy=False)

    transaction_ids = fields.Many2many(
        comodel_name='payment.transaction',
        relation='repair_order_transaction_rel', column1='repair_order_id', column2='transaction_id',
        string="Transactions",
        copy=False, readonly=True)
    authorized_transaction_ids = fields.Many2many(
        comodel_name='payment.transaction',
        string="Authorized Transactions",
        compute='_compute_authorized_transaction_ids',
        copy=False,
        compute_sudo=True)
    amount_paid = fields.Float(compute='_compute_amount_paid', compute_sudo=True)
    amount_residual = fields.Monetary(string='Amount Due', store=True, compute='_compute_amount_due')

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string="Analytic Account",
        copy=False, check_company=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    tag_ids = fields.Many2many(
        comodel_name='vtt.repair.order.tag',
        relation='repair_order_tag_rel', column1='repair_order_id', column2='tag_id',
        string="Tags")

    need_invoice = fields.Boolean('Need Invoice', compute='_compute_need_invoice')

    payment_state = fields.Selection([
        ('new', 'New'),
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancel', 'Cancel'),
    ], 'Payment Status',
        compute='_compute_payment_state',
        store=True,
    )

    # Timesheets
    timesheet_line_ids = fields.One2many('account.analytic.line', 'repair_order_id', 'Timesheets')

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        if self.equipment_id:
            self.equipment_date_warranty = self.equipment_id.date_warranty
            if self.equipment_id.date_warranty and self.equipment_id.date_warranty >= fields.Date.today():
                self.is_under_warranty = True

    def _compute_need_picking(self):
        for order in self:
            order_need_picking = order.line_ids.filtered(lambda l: l.product_id
                                                                   and l.product_id.type != 'service'
                                                                   and l.qty_delivered < l.product_uom_qty
                                                         )
            order.need_picking = order_need_picking and True or False

    def _compute_need_invoice(self):
        for order in self:
            order_need_invoice = order.line_ids.filtered(lambda l: l.product_id
                                                                   and l.qty_to_invoice > 0.0
                                                         )
            order.need_invoice = order_need_invoice and True or False

    @api.depends('state', 'invoice_ids.payment_state', 'invoice_ids')
    def _compute_payment_state(self):
        for order in self:
            if order.state == 'new':
                order.payment_state = 'new'
            elif order.state != 'cancel':
                if all(m.payment_state == 'paid' for m in order.invoice_ids):
                    order.payment_state = 'paid'
                elif all(m.payment_state == 'not_paid' for m in order.invoice_ids):
                    order.payment_state = 'not_paid'
                else:
                    order.payment_state = 'partial'

            #     amount_paid = sum(
            #         tx.amount for tx in order.transaction_ids if tx.state in ('authorized', 'done')
            #     )
            #     if order.currency_id.compare_amounts(order.amount_paid, order.amount_total) >= 0:
            #         order.payment_state = 'paid'
            #     else:
            #         if amount_paid > 0.0:
            #             order.payment_state = 'partial'
            #         else:
            #             order.payment_state = 'not_paid'
            else:
                order.payment_state = 'cancel'

    def _compute_journal_id(self):
        self.journal_id = False

    def _prepare_invoice(self):
        self.ensure_one()

        values = {
            'ref': self.name or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.currency_id.id,
            # 'campaign_id': self.campaign_id.id,
            # 'medium_id': self.medium_id.id,
            # 'source_id': self.source_id.id,
            # 'team_id': self.team_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_invoice_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id._get_fiscal_position(
                self.partner_invoice_id)).id,
            'invoice_origin': self.name,
            # 'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_user_id': self.user_id.id,
            'payment_reference': self.name,
            'transaction_ids': [Command.set(self.transaction_ids.ids)],
            'company_id': self.company_id.id,
            'invoice_line_ids': [],
            'user_id': self.user_id.id,
        }
        if self.journal_id:
            values['journal_id'] = self.journal_id.id
        return values

    def _get_invoiceable_lines(self, final=False):
        down_payment_line_ids = []
        invoiceable_line_ids = []
        pending_section = None
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for line in self.line_ids:
            if line.display_type == 'line_section':
                # Only invoice the section if one of its lines is invoiceable
                pending_section = line
                continue
            if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                continue
            if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                # if line.is_downpayment:
                #     down_payment_line_ids.append(line.id)
                #     continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = None
                invoiceable_line_ids.append(line.id)

        return self.env['vtt.repair.order.line'].browse(invoiceable_line_ids + down_payment_line_ids)

    def _get_invoice_grouping_keys(self):
        return ['company_id', 'partner_id', 'currency_id']

    def _create_invoices(self, grouped=False, final=False, date=None):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        invoice_item_sequence = 0
        for order in self:
            order = order.with_company(order.company_id).with_context(lang=order.partner_invoice_id.lang)

            invoice_vals = order._prepare_invoice()
            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            invoice_line_vals = []
            down_payment_section_added = False
            for line in invoiceable_lines:
                # if not down_payment_section_added and line.is_downpayment:
                #     invoice_line_vals.append(
                #         Command.create(
                #             order._prepare_down_payment_section_line(sequence=invoice_item_sequence)
                #         ),
                #     )
                #     down_payment_section_added = True
                #     invoice_item_sequence += 1
                invoice_line_vals.append(
                    Command.create(
                        line._prepare_invoice_line(sequence=invoice_item_sequence)
                    ),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] += invoice_line_vals
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list and self._context.get('raise_if_nothing_to_invoice', True):
            raise UserError(_(
                "Cannot create an invoice. No items are available to invoice.\n\n"
                "To resolve this issue, please ensure that:\n"
                "   \u2022 The products have been delivered before attempting to invoice them.\n"
                "   \u2022 The invoicing policy of the product is configured correctly.\n\n"
                "If you want to invoice based on ordered quantities instead:\n"
                "   \u2022 For consumable or storable products, open the product, go to the 'General Information' tab and change the 'Invoicing Policy' from 'Delivered Quantities' to 'Ordered Quantities'.\n"
                "   \u2022 For services (and other products), change the 'Invoicing Policy' to 'Prepaid/Fixed Price'.\n"
            ))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ]
            )
            for _grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        if len(invoice_vals_list) < len(self):
            RepairOrderLine = self.env['vtt.repair.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = RepairOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_move_type()
        for move in moves:
            if final:
                delta_amount = 0
                for order_line in self.line_ids:
                    # if not order_line.is_downpayment:
                    #     continue
                    inv_amt = order_amt = 0
                    for invoice_line in order_line.invoice_lines:
                        if invoice_line.move_id == move:
                            inv_amt += invoice_line.price_total
                        elif invoice_line.move_id.state != 'cancel':
                            order_amt += invoice_line.price_total
                    if inv_amt and order_amt:
                        delta_amount += (inv_amt * (1 if move.is_inbound() else -1)) + order_amt

                if not move.currency_id.is_zero(delta_amount):
                    receivable_line = move.line_ids.filtered(
                        lambda aml: aml.account_id.account_type == 'asset_receivable')[:1]
                    product_lines = move.line_ids.filtered(
                        lambda aml: aml.display_type == 'product' and aml.is_downpayment)
                    tax_lines = move.line_ids.filtered(
                        lambda aml: aml.tax_line_id.amount_type not in (False, 'fixed'))
                    if tax_lines and product_lines and receivable_line:
                        line_commands = [Command.update(receivable_line.id, {
                            'amount_currency': receivable_line.amount_currency + delta_amount,
                        })]
                        delta_sign = 1 if delta_amount > 0 else -1
                        for lines, attr, sign in (
                            (product_lines, 'price_total', -1 if move.is_inbound() else 1),
                            (tax_lines, 'amount_currency', 1),
                        ):
                            remaining = delta_amount
                            lines_len = len(lines)
                            for line in lines:
                                if move.currency_id.compare_amounts(remaining, 0) != delta_sign:
                                    break
                                amt = delta_sign * max(
                                    move.currency_id.rounding,
                                    abs(move.currency_id.round(remaining / lines_len)),
                                )
                                remaining -= amt
                                line_commands.append(Command.update(line.id, {attr: line[attr] + amt * sign}))
                        move.line_ids = line_commands

            move.message_post_with_source(
                'mail.message_origin_link',
                render_values={'self': move, 'origin': move.line_ids.repair_order_line_ids.repair_order_id},
                subtype_xmlid='mail.mt_note',
            )
        return moves

    def action_create_invoice(self):
        self._create_invoices()
        return self.action_view_invoice()

    @api.depends('transaction_ids')
    def _compute_authorized_transaction_ids(self):
        for order in self:
            order.authorized_transaction_ids = order.transaction_ids.filtered(lambda t: t.state == 'authorized')

    # @api.depends('transaction_ids')
    # def _compute_amount_paid(self):
    #     for order in self:
    #         order.amount_paid = sum(
    #             tx.amount for tx in order.transaction_ids if tx.state in ('authorized', 'done')
    #         )

    @api.depends('invoice_ids', 'invoice_ids.amount_residual', 'invoice_ids.state')
    def _compute_amount_due(self):
        for order in self:
            order.amount_residual = sum(inv.amount_residual for inv in order.invoice_ids if inv.state == 'posted')

    @api.depends('amount_total', 'amount_residual')
    def _compute_amount_paid(self):
        for order in self:
            order.amount_paid = order.amount_total - order.amount_residual

    @api.depends('line_ids.invoice_lines')
    def _get_invoiced(self):
        for order in self:
            invoices = order.line_ids.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    def _search_invoice_ids(self, operator, value):
        if operator == 'in' and value:
            self.env.cr.execute("""
                SELECT array_agg(ro.id)
                    FROM vtt_repair_order ro
                    JOIN vtt_repair_order_line rol ON rol.repair_order_id = ro.id
                    JOIN repair_order_line_invoice_rel roli_rel ON roli_rel.repair_order_line_id = rol.id
                    JOIN account_move_line aml ON aml.id = roli_rel.invoice_line_id
                    JOIN account_move am ON am.id = aml.move_id
                WHERE
                    am.move_type in ('out_invoice', 'out_refund') AND
                    am.id = ANY(%s)
            """, (list(value),))
            so_ids = self.env.cr.fetchone()[0] or []
            return [('id', 'in', so_ids)]
        elif operator == '=' and not value:
            order_ids = self._search([
                ('line_ids.invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund'))
            ])
            return [('id', 'not in', order_ids)]
        return [
            ('line_ids.invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund')),
            ('line_ids.invoice_lines.move_id', operator, value),
        ]

    @api.depends('partner_invoice_id', 'partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            key = (order.company_id.id, order.partner_id.id, order.partner_invoice_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(
                    order.company_id
                )._get_fiscal_position(order.partner_id, order.partner_invoice_id)
            order.fiscal_position_id = cache[key]

    def _prepare_analytic_account_data(self, prefix=None):
        self.ensure_one()
        name = self.name
        if prefix:
            name = prefix + ": " + self.name
        plan = self.env['account.analytic.plan'].sudo().search([], limit=1)
        if not plan:
            plan = self.env['account.analytic.plan'].sudo().create({
                'name': 'MRO',
            })
        return {
            'name': name,
            'code': self.name,
            'company_id': self.company_id.id,
            'plan_id': plan.id,
            'partner_id': self.partner_id.id,
        }

    def _create_analytic_account(self, prefix=None):
        for order in self:
            analytic = self.env['account.analytic.account'].create(order._prepare_analytic_account_data(prefix))
            order.analytic_account_id = analytic

    def action_create_delivery(self):
        self.line_ids._action_launch_stock_rule()
        return self.action_view_picking()

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for order in self:
            order.picking_count = len(order.picking_ids)

    def _init_column(self, column_name):
        if column_name != "warehouse_id":
            return super(RepairOrder, self)._init_column(column_name)
        field = self._fields[column_name]
        default = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
        value = field.convert_to_write(default, self)
        value = field.convert_to_column(value, self)
        if value is not None:
            _logger.debug("Table '%s': setting default value of new column %s to %r",
                self._table, column_name, value)
            query = f'UPDATE "{self._table}" SET "{column_name}" = %s WHERE "{column_name}" IS NULL'
            self._cr.execute(query, (value,))

    @api.depends('user_id', 'company_id')
    def _compute_warehouse_id(self):
        for order in self:
            default_warehouse_id = self.env['ir.default'].with_company(
                order.company_id.id)._get_model_defaults('vtt.repair.order').get('warehouse_id')
            if order.state in ['new', 'confirm'] or not order.ids:
                # Should expect empty
                if default_warehouse_id is not None:
                    order.warehouse_id = default_warehouse_id
                else:
                    order.warehouse_id = order.user_id.with_company(order.company_id.id)._get_default_warehouse_id()

    def _compute_modify_available(self):
        for order in self:
            order.modify_available = not order.locked

    @api.depends('diagnosis_ids')
    def _compute_diagnosis_count(self):
        for order in self:
            # diag = order.mapped('diagnosis_ids').filtered(lambda d: d.state != 'cancel')
            # order.diagnosis_count = len(diag)
            order.diagnosis_count = len(order.diagnosis_ids)

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if not start or not stop:
            return 0
        duration = (stop - start).total_seconds() / 3600
        return round(duration, 2)

    @api.depends('dt_start_repair', 'dt_end_repair')
    def _compute_duration_repair(self):
        for order in self:
            order.duration_repair = self._get_duration(order.dt_start_repair, order.dt_end_repair)

    @api.depends('dt_confirm', 'dt_done')
    def _compute_duration_order(self):
        for order in self:
            order.duration_order = self._get_duration(order.dt_confirm, order.dt_done)

    def action_confirm(self):
        for order in self:
            if not order.analytic_account_id:
                order._create_analytic_account()

        return self.write({
            'state': 'confirm',
            'dt_confirm': fields.Datetime.now(),
        })

    def action_cancel(self):
        inv = self.invoice_ids.filtered(lambda inv: inv.state == 'draft')
        inv.button_cancel()

        return self.write({
            'state': 'cancel',
            'dt_confirm': False,
        })

    def action_draft(self):

        return self.write({
            'state': 'new',
        })

    def action_start_repair(self):

        return self.write({
            'state': 'under_repair',
            'dt_start_repair': fields.Datetime.now(),
        })

    def action_end_repair(self):

        return self.write({
            'state': 'repaired',
            'dt_end_repair': fields.Datetime.now(),
        })

    def action_done(self):

        return self.write({
            'state': 'done',
            'dt_done': fields.Datetime.now(),
        })

    def _compute_amount_undiscounted(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                total += (line.price_subtotal * 100)/(100-line.discount) if line.discount != 100 else (line.price_unit * line.product_uom_qty)
            order.amount_undiscounted = total

    @api.depends_context('lang')
    @api.depends('line_ids.tax_id', 'line_ids.price_unit', 'amount_total', 'amount_untaxed', 'currency_id')
    def _compute_tax_totals(self):
        for order in self:
            line_ids = order.line_ids.filtered(lambda x: not x.display_type)
            order.tax_totals = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in line_ids],
                order.currency_id or order.company_id.currency_id,
            )

    @api.depends('partner_id')
    def _compute_note(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('vtt_mro.use_invoice_terms')
        return
        # if not use_invoice_terms:
        #     return
        # for order in self:
        #     order = order.with_company(order.company_id)
        #     if order.terms_type == 'html' and self.env.company.invoice_terms_html:
        #         baseurl = html_keep_url(order._get_note_url() + '/terms')
        #         context = {'lang': order.partner_id.lang or self.env.user.lang}
        #         order.note = _('Terms & Conditions: %s', baseurl)
        #         del context
        #     elif not is_html_empty(self.env.company.invoice_terms):
        #         order.note = order.with_context(lang=order.partner_id.lang).env.company.invoice_terms

    @api.depends('line_ids.price_subtotal', 'line_ids.price_tax', 'line_ids.price_total')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for order in self:
            lines = order.line_ids.filtered(lambda x: not x.display_type)

            amount_untaxed = sum(lines.mapped('price_subtotal'))
            amount_tax = sum(lines.mapped('price_tax'))

            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = order.amount_untaxed + order.amount_tax

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['dt_order'])
                ) if 'dt_order' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'repair.order', sequence_date=seq_date) or _("New")

        return super().create(vals_list)

    @api.depends('partner_id')
    def _compute_partner_invoice_id(self):
        for order in self:
            order.partner_invoice_id = order.partner_id.address_get(['invoice'])[
                'invoice'] if order.partner_id else False

    def action_create_diagnosis(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_mro.vtt_act_window_repair_diagnosis")
        action['view_mode'] = 'form'
        action['views'] = [[False, "form"]]
        action['target'] = 'current'

        context = dict(self.env.context)
        context['default_repair_order_id'] = self.id
        action['context'] = context
        return action

    def action_view_diagnosis(self):
        diags = self.mapped('diagnosis_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("vtt_mro.vtt_act_window_repair_diagnosis")
        context = dict(self.env.context)
        context['default_repair_order_id'] = self.id
        action['context'] = context
        if len(diags) == 1:
            action['view_mode'] = 'form'
            action['views'] = [[False, "form"]]
            action['res_id'] = diags.id
        else:
            action['domain'] = [('id', 'in', diags.ids)]

        return action

    def action_view_picking(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        pickings = self.picking_ids

        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name, default_group_id=picking_id.group_id.id)
        return action

    def action_view_invoice(self, invoices=False):
        if not invoices:
            invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id('account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_partner_shipping_id': self.partner_invoice_id.id,
                'default_invoice_payment_term_id': self.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
            })
        action['context'] = context
        return action

    def action_view_maintenance(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('vtt_mro.vtt_act_window_maintenance_plan')
        action['domain'] = [('equipment_id', '=', self.equipment_id.id)]
        context = {
            'default_partner_id': self.partner_id.id,
            'default_equipment_id': self.equipment_id.id,
        }
        action['context'] = context
        return action

    def action_view_warranty(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('vtt_mro.vtt_act_window_warranty_ticket')
        action['domain'] = [('equipment_id', '=', self.equipment_id.id)]
        context = {
            'default_partner_id': self.partner_id.id,
            'default_equipment_id': self.equipment_id.id,
        }
        action['context'] = context
        return action

    def action_update_warranty(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Warranty Update"),
            'res_model': 'vtt.warranty.update.wz',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_equipment_id': self.equipment_id.id,
            },
            'target': 'new',
        }