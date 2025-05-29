# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
from functools import partial
from odoo.tools.misc import formatLang, get_lang


class VttCarRepairOrder(models.Model):
    _name = 'vtt.car.repair.order'
    _description = 'Car Repair Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, states={'confirmed': [('readonly', True)]}, tracking=3)
    vehicle_brand_id = fields.Many2one(related='vehicle_id.brand_id', string='Brand')
    vehicle_model_id = fields.Many2one(related='vehicle_id.model_id', string='Model')
    vehicle_license_plate = fields.Char('License Plate', related='vehicle_id.license_plate')
    vehicle_color = fields.Char('Color', related='vehicle_id.color')
    vehicle_model_year = fields.Char('Model Year', related='vehicle_id.model_year')

    odometer_id = fields.Many2one('fleet.vehicle.odometer', 'Odometer',
                                  help='Odometer measure of the vehicle at the moment of this log')
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer', string='Odometer Value',
                            states={'confirmed': [('readonly', True)]},
                            help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(related='vehicle_id.odometer_unit', string="Unit", readonly=True)

    name = fields.Char(
        'Repair Reference',
        copy=False,
        states={'confirmed': [('readonly', True)]},
        default=lambda self: _('New'))
    partner_id = fields.Many2one(
        'res.partner', 'Customer', tracking=1,
        index=True, states={'confirmed': [('readonly', True)]}, check_company=True, change_default=True,
        help='Choose partner for whom the order will be invoiced and delivered. You can find a partner by its Name, TIN, Email or Internal Reference.')
    partner_phone = fields.Char('Customer Phone', related='partner_id.phone')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('confirmed', 'Confirmed'),
        ('under_repair', 'Under Repair'),
        ('repaired', 'Repaired'),
        ('done', 'Repaired'),
        ('cancel', 'Cancelled')], string='Status',
        copy=False, default='draft', readonly=True, tracking=16,
        help="* The \'Quotation\' status is used when a user is encoding a new and unconfirmed repair order.\n"
             "* The \'Confirmed\' status is used when a user confirms the repair order.\n"
             "* The \'Done\' status is set when repairing is completed.\n"
             "* The \'Cancelled\' status is used when user cancel repair order.")
    location_id = fields.Many2one(
        'stock.location', 'Location',
        index=True, readonly=True, required=True, check_company=True,
        help="This is the location where the product to repair is located.",
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', True)]})
    guarantee_limit = fields.Date('Warranty Expiration', states={'confirmed': [('readonly', True)]}, tracking=10)
    pricelist_id = fields.Many2one(
        'product.pricelist', 'Pricelist',
        default=lambda self: self.env['product.pricelist'].search([('company_id', 'in', [self.env.company.id, False])],
                                                                  limit=1).id,
        help='Pricelist of the selected partner.', check_company=True)
    currency_id = fields.Many2one(related='pricelist_id.currency_id')

    invoice_id = fields.Many2one(
        'account.move', 'Invoice',
        copy=False, readonly=True, tracking=8,
        domain=[('move_type', '=', 'out_invoice')])

    picking_ids = fields.One2many('stock.picking', 'car_repair_id', string='Transfers')
    delivery_count = fields.Integer(string='Delivery Orders', compute='_compute_picking_ids')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', required=True, check_company=True,)
    internal_notes = fields.Text('Internal Notes')
    quotation_notes = fields.Text('Quotation Notes')

    user_id = fields.Many2one('res.users', string="Responsible", default=lambda self: self.env.user, check_company=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        readonly=True, required=True, index=True,
        default=lambda self: self.env.company)
    tag_ids = fields.Many2many('vtt.car.repair.tags', 'vtt_car_repair_order_tag_rel', string="Tags")
    invoiced = fields.Boolean('Invoiced', copy=False, readonly=True)
    repaired = fields.Boolean('Repaired', copy=False, readonly=True)
    amount_untaxed = fields.Float('Untaxed Amount', compute='_amount_untaxed', store=True, tracking=4)
    amount_tax = fields.Float('Taxes', compute='_amount_tax', store=True)
    amount_total = fields.Float('Total', compute='_amount_total', store=True, tracking=5)
    amount_reduced = fields.Float('Reduced Amount', compute='_amount_reduced', store=True)
    invoice_state = fields.Selection(string='Invoice State', related='invoice_id.state')

    order_line_ids = fields.One2many('vtt.car.repair.order.line', 'repair_id', 'Details', copy=True)

    dt_receive = fields.Datetime('Receive Date', default=fields.Datetime.now)
    dt_confirmed = fields.Datetime('Confirmed Date', tracking=11)
    dt_deadline = fields.Datetime('Expected Close', tracking=12)

    dt_start_repair = fields.Datetime('Start Repair', tracking=13)
    dt_end_repair = fields.Datetime('End Repair', tracking=14)
    total_repair_time = fields.Float('Total Repair Time', compute='_get_total_repair_time', store=True)

    receive_user_id = fields.Many2one('res.users', 'Receiver', default=lambda self: self.env.user, tracking=15)
    technical_user_id = fields.Many2one('res.users', 'Technical', tracking=15)

    repair_state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], 'Repair State', default='draft', copy=False, readonly=True, tracking=16)

    vtt_car_service_ids = fields.Many2many('fleet.service.type', 'vtt_car_repair_service_type_rel', string='Services',
                                           domain=[('category', '=', 'service')])

    amount_by_group = fields.Binary(string="Tax amount by group", compute='_amount_by_group',
                                    help="type: [(name, amount, base, formated amount, formated base)]")

    img1 = fields.Image(string="Image", readonly=False, store=True)
    img2 = fields.Image(string="Image", readonly=False, store=True)
    img3 = fields.Image(string="Image", readonly=False, store=True)
    img4 = fields.Image(string="Image", readonly=False, store=True)

    amount_total_text = fields.Char('Amount Text')

    # Check rights to change data
    can_modify = fields.Boolean('Can Modify?', compute='_compute_can_modify', default=True)

    # Update inventory show
    has_update_inventory = fields.Boolean('Has Update Inventory', compute='_compute_has_update_inventory')

    def _compute_has_update_inventory(self):
        for ro in self:
            check = False
            lines = ro.order_line_ids.filtered(lambda l: l.product_id and l.product_id.type != 'service' and l.in_delivery_qty < l.product_uom_qty)
            if lines:
                check = True
            ro.has_update_inventory = check

    def _compute_can_modify(self):
        user = self.env.user
        modify_right = True
        for r in self:
            if r.id and r.state in ['done', 'cancel']:
                if r.state in ['done'] and user.has_group('vtt_car_repair.vtt_group_car_repair_manager'):
                    modify_right = True
                else:
                    modify_right = False
            r.can_modify = modify_right

    @api.onchange('amount_total')
    def onchange_amount_total(self):
        amount = self.amount_total or 0.0
        if self.partner_id:
            lang_code = self.partner_id.lang
        else:
            lang_code = self.env.user.lang
        txt = self.currency_id.with_context(lang=lang_code).amount_to_text(amount)
        amount_text = txt[:1] + txt[1:].lower()
        self.amount_total_text = amount_text

    @api.depends('state', 'repair_state', 'dt_start_repair', 'dt_end_repair')
    def _get_total_repair_time(self):
        for r in self:
            if r.state in ['under_repair', 'repaired', 'done'] and r.repair_state in ['progress', 'done'] \
                    and r.dt_start_repair:
                if r.repair_state == 'progress':
                    duration = (fields.Datetime.now() - r.dt_start_repair).total_seconds() / 3600
                elif r.repair_state == 'done' and r.dt_end_repair:
                    duration = (r.dt_end_repair - r.dt_start_repair).total_seconds() / 3600
                else:
                    duration = 0.0
            else:
                duration = 0.0
            r.update({
                'total_repair_time': round(duration, 2)
            })

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('vtt.car.repair.order')
        res = super().create(vals)
        if res and 'vtt_car_service_ids' in vals:
            res._update_car_services()
        return res

    @api.depends('order_line_ids.price_subtotal', 'pricelist_id.currency_id')
    def _amount_untaxed(self):
        for order in self:
            total = sum(operation.price_subtotal for operation in order.order_line_ids)
            order.amount_untaxed = order.pricelist_id.currency_id.round(total)

    @api.depends('order_line_ids.amount_reduced')
    def _amount_reduced(self):
        for order in self:
            total = sum(operation.amount_reduced for operation in order.order_line_ids)
            order.amount_reduced = order.pricelist_id.currency_id.round(total)

    @api.depends('order_line_ids.price_unit', 'order_line_ids.product_uom_qty', 'order_line_ids.product_id',
                 'pricelist_id.currency_id', 'partner_id', 'order_line_ids.discount')
    def _amount_tax(self):
        for order in self:
            val = 0.0
            lines = order.order_line_ids.filtered(lambda l: not l.display_type)
            for operation in lines:
                if operation.tax_id:
                    price_reduce = operation.price_unit - operation.price_unit * ((operation.discount or 0.0) / 100.0)
                    tax_calculate = operation.tax_id.compute_all(price_reduce, order.pricelist_id.currency_id,
                                                                 operation.product_uom_qty, operation.product_id,
                                                                 order.partner_id)
                    for c in tax_calculate['taxes']:
                        val += c['amount']
            order.amount_tax = val

    @api.depends('amount_untaxed', 'amount_tax')
    def _amount_total(self):
        for order in self:
            order.amount_total = order.pricelist_id.currency_id.round(order.amount_untaxed + order.amount_tax)

    def _get_odometer(self):
        self.odometer = 0
        for record in self:
            if record.odometer_id:
                record.odometer = record.odometer_id.value

    def _set_odometer(self):
        for record in self:
            if record.odometer:
                odometer = self.env['fleet.vehicle.odometer'].create({
                    'value': record.odometer,
                    'date': record.dt_receive.date() or fields.Date.context_today(record),
                    'vehicle_id': record.vehicle_id.id
                })
                self.odometer_id = odometer

    @api.onchange('vehicle_id')
    def onchange_vehicle(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.partner_id = self.vehicle_id.driver_id

    @api.onchange('partner_id')
    def onchange_partner(self):
        self = self.with_company(self.company_id)
        if not self.partner_id:
            self.pricelist_id = self.env['product.pricelist'].search([
                ('company_id', 'in', [self.env.company.id, False]),
            ], limit=1)
        else:
            self.pricelist_id = self.partner_id.property_product_pricelist.id

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
            self.location_id = warehouse.lot_stock_id
            self.picking_type_id = warehouse.out_type_id
        else:
            self.location_id = False
            self.picking_type_id = False

    def button_dummy(self):
        # TDE FIXME: this button is very interesting
        return True

    def action_repair_confirm(self):
        if self.filtered(lambda repair: repair.state != 'draft'):
            raise UserError(_("Only draft repairs can be confirmed."))

        # Check Product when confirm Repair Order
        if any(self.mapped('order_line_ids').filtered(lambda line: not line.display_type and not line.product_id)):
            raise UserError(_("All order line with type 'Product' have to referer to System Product\n"
                              "before the Order can be confirm."))

        self._check_company()
        self.order_line_ids._check_company()
        self.mapped('order_line_ids').write({'state': 'confirmed'})
        self.write({'state': 'confirmed', 'dt_confirmed': fields.Datetime.now()})
        return True

    def action_repair_cancel(self):
        invoice_to_cancel = self.filtered(lambda repair: repair.invoice_id.state == 'draft').invoice_id
        if invoice_to_cancel:
            invoice_to_cancel.button_cancel()
        self.mapped('order_line_ids').write({'state': 'cancel', 'repair_state': 'cancel'})
        self.picking_ids.filtered(lambda p: p.state != 'done').action_cancel()
        return self.write({'state': 'cancel', 'repair_state': 'cancel', 'dt_confirmed': False})

    def action_repair_cancel_draft(self):
        if self.filtered(lambda repair: repair.state != 'cancel'):
            raise UserError(_("Repair must be canceled in order to reset it to draft."))
        self.mapped('order_line_ids').write({'state': 'draft', 'repair_state': 'draft', 'invoiced': False})
        return self.write({'state': 'draft', 'repair_state': 'draft', 'invoice_id': False, 'invoiced': False})

    def action_start_repair(self):
        self.mapped('order_line_ids').write({
            'repair_state': 'progress'
        })
        self.write({
            'state': 'under_repair',
            'repair_state': 'progress',
            'dt_start_repair': fields.Datetime.now()
        })

    def action_end_repair(self):
        self.mapped('order_line_ids').write({
            'repair_state': 'done'
        })
        return self.write({
            'state': 'repaired',
            'repair_state': 'done',
            'dt_end_repair': fields.Datetime.now()
        })

    def action_done(self):
        self.mapped('order_line_ids').write({
            'repair_state': 'done'
        })
        vals = {
            'state': 'done',
            'repair_state': 'done'
        }
        if self.dt_start_repair:
            vals['dt_end_repair'] = fields.Datetime.now()
        return self.write(vals)

    def action_repair_picking_create(self):
        for r in self:
            r._create_stock_picking()

    def action_repair_invoice_create(self):
        for repair in self:
            repair._create_invoices()
        return True

    def _create_invoices(self, group=False):
        grouped_invoices_vals = {}
        repairs = self.filtered(lambda repair: repair.state not in ('draft', 'cancel') and not repair.invoice_id)
        for repair in repairs:
            repair = repair.with_company(repair.company_id)
            partner_invoice = repair.partner_id
            if not partner_invoice:
                raise UserError(_('You have to select an invoice address in the repair form.'))

            narration = repair.quotation_notes
            currency = repair.pricelist_id.currency_id
            company = repair.env.company

            journal = repair.env['account.move'].with_context(move_type='out_invoice')._get_default_journal()
            if not journal:
                raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (
                company.name, company.id))

            if (partner_invoice.id, currency.id) not in grouped_invoices_vals:
                grouped_invoices_vals[(partner_invoice.id, currency.id, company.id)] = []
            current_invoices_list = grouped_invoices_vals[(partner_invoice.id, currency.id, company.id)]

            if not group or len(current_invoices_list) == 0:
                fpos = self.env['account.fiscal.position'].get_fiscal_position(partner_invoice.id,
                                                                               delivery_id=repair.partner_id.id)
                invoice_vals = {
                    'move_type': 'out_invoice',
                    'partner_id': partner_invoice.id,
                    'partner_shipping_id': repair.partner_id.id,
                    'currency_id': currency.id,
                    'narration': narration,
                    'invoice_origin': repair.name,
                    'car_repair_id': repair.id,
                    'car_repair_ids': [(4, repair.id)],
                    'invoice_line_ids': [],
                    'fiscal_position_id': fpos.id
                }
                if partner_invoice.property_payment_term_id:
                    invoice_vals['invoice_payment_term_id'] = partner_invoice.property_payment_term_id.id
                current_invoices_list.append(invoice_vals)
            else:
                # if group == True: concatenate invoices by partner and currency
                invoice_vals = current_invoices_list[0]
                invoice_vals['invoice_origin'] += ', ' + repair.name
                invoice_vals['car_repair_ids'].append((4, repair.id))
                if not invoice_vals['narration']:
                    invoice_vals['narration'] = narration
                else:
                    invoice_vals['narration'] += '\n' + narration

            # Create invoice lines from fees.
            for fee in repair.order_line_ids:
                # if group:
                #     name = repair.name + '-' + fee.name
                # else:
                #     name = fee.name
                #
                # invoice_line_vals = {
                #     'display_type': fee.display_type,
                #     'name': name,
                #     # 'account_id': not fee.display_type and account.id or False,
                #     'quantity': fee.product_uom_qty,
                #     'tax_ids': [(6, 0, fee.tax_id.ids)],
                #     'product_uom_id': fee.product_uom.id,
                #     'price_unit': fee.price_unit,
                #     'product_id': fee.product_id.id,
                #     'car_repair_line_ids': [(4, fee.id)],
                #     'discount': fee.discount,
                # }
                #
                # if not fee.display_type:
                #     account = fee.product_id.product_tmpl_id._get_product_accounts()['income']
                #     if not account:
                #         raise UserError(_('No account defined for product "%s".', fee.product_id.name))
                #     invoice_line_vals['account_id'] = account.id
                # else:
                #     invoice_line_vals['account_id'] = False
                #
                # price = fee.price_unit - fee.price_unit * ((fee.discount or 0.0) / 100.0)
                # if currency == company.currency_id:
                #     balance = -(fee.product_uom_qty * price)
                #     invoice_line_vals.update({
                #         'debit': balance > 0.0 and balance or 0.0,
                #         'credit': balance < 0.0 and -balance or 0.0,
                #     })
                # else:
                #     amount_currency = - (fee.product_uom_qty * price)
                #     balance = currency._convert(amount_currency, company.currency_id, company,
                #                                 fields.Date.today())
                #     invoice_line_vals.update({
                #         'amount_currency': amount_currency,
                #         'debit': balance > 0.0 and balance or 0.0,
                #         'credit': balance < 0.0 and -balance or 0.0,
                #         'currency_id': currency.id,
                #     })
                invoice_line_vals = fee.get_invoice_line_values(group)
                invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))

        # Create invoices.
        invoices_vals_list_per_company = defaultdict(list)
        for (partner_invoice_id, currency_id, company_id), invoices in grouped_invoices_vals.items():
            for invoice in invoices:
                invoices_vals_list_per_company[company_id].append(invoice)

        for company_id, invoices_vals_list in invoices_vals_list_per_company.items():
            # VFE TODO remove the default_company_id ctxt key ?
            # Account fallbacks on self.env.company, which is correct with with_company
            self.env['account.move'].with_company(company_id).with_context(default_company_id=company_id,
                                                                           default_move_type='out_invoice').create(
                invoices_vals_list)

        repairs.write({'invoiced': True})
        repairs.mapped('order_line_ids').write({'invoiced': True})

        return dict((repair.id, repair.invoice_id.id) for repair in repairs)

    def action_created_invoice(self):
        self.ensure_one()
        return {
            'name': _('Invoice created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
            'res_id': self.invoice_id.id,
            }

    def _create_stock_picking(self):
        self.ensure_one()
        company = self.company_id
        lines_to_pick = self.order_line_ids.filtered(lambda line: line.product_id and line.product_id.type != 'service')
        if not lines_to_pick:
            return
            # raise UserError(_("The Repair Order doesn't has any product available to delivery.\n"
            #                   "Please note that 'Service' product would not appear in delivery order."))

        picking_vals = {
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.picking_type_id.default_location_src_id.id if self.picking_type_id.default_location_src_id else self.location_id.id,
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'scheduled_date': self.dt_deadline if self.dt_deadline else fields.Datetime.now(),
            'origin': self.name,
            'car_repair_id': self.id,
            'move_ids_without_package': []
        }
        for line in lines_to_pick:
            move_vals = {
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom,
                'name': line.name,
                'car_repair_line_id': line.id,
            }
            picking_vals['move_ids_without_package'].append((0, 0, move_vals))

        new_picking = self.env['stock.picking'].with_company(company.id).with_context(default_company_id=company.id).sudo().create(picking_vals)
        if new_picking:
            # Need to add Auto confirm new picking
            new_picking.sudo().action_confirm()
        return True

    def update_stock_picking(self):
        self.ensure_one()
        pickings = self.mapped('picking_ids').filtered(lambda p: p.state != 'cancel')
        move_lines = pickings.mapped('move_ids_without_package').filtered(lambda m: m.state not in ['done', 'cancel'])
        lines_to_pick = self.order_line_ids.filtered(lambda line: line.product_id and line.product_id.type != 'service' and line.in_delivery_qty < line.product_uom_qty)
        if lines_to_pick:
            new_pick_moves = []
            for l in lines_to_pick:
                qty_change = l.product_uom_qty - l.in_delivery_qty
                moves = move_lines.filtered(lambda m: m.car_repair_line_id == l)
                if moves:
                    moves[0].product_uom_qty += qty_change
                else:
                    new_pick_moves.append((l, qty_change))
            if new_pick_moves:
                open_pickings = pickings.filtered(lambda p: p.state != 'done')
                move_vals = [(0, 0, {
                    'product_id': l[0].product_id.id,
                    'product_uom_qty': l[1],
                    'product_uom': l[0].product_uom,
                    'name': l[0].name,
                    'car_repair_line_id': l[0].id,
                    'location_id': self.picking_type_id.default_location_src_id.id if self.picking_type_id.default_location_src_id else self.location_id.id,
                    'location_dest_id': self.partner_id.property_stock_customer.id,
                }) for l in new_pick_moves]

                if open_pickings:
                    picking = open_pickings[0]
                    picking.move_ids_without_package = move_vals
                    picking.sudo().action_confirm()
                else:
                    picking_vals = {
                        'partner_id': self.partner_id.id,
                        'picking_type_id': self.picking_type_id.id,
                        'location_id': self.picking_type_id.default_location_src_id.id if self.picking_type_id.default_location_src_id else self.location_id.id,
                        'location_dest_id': self.partner_id.property_stock_customer.id,
                        'scheduled_date': self.dt_deadline if self.dt_deadline else fields.Datetime.now(),
                        'origin': self.name,
                        'car_repair_id': self.id,
                        'move_ids_without_package': move_vals
                    }

                    new_picking = self.env['stock.picking'].with_company(self.company_id.id).with_context(
                        default_company_id=self.company_id.id).sudo().create(picking_vals)
                    if new_picking:
                        # Need to add Auto confirm new picking
                        new_picking.sudo().action_confirm()

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(order.picking_ids)

    def action_view_delivery(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        pickings = self.mapped('picking_ids')
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
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id, default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name)
        return action

    def write(self, vals):
        res = super().write(vals)
        if 'vtt_car_service_ids' in vals:
            self._update_car_services()
        return res

    def _update_car_services(self):
        repairs = self.filtered(lambda repair: repair.state not in ['done', 'cancel'])
        if repairs:
            for repair in repairs:
                services = repair.mapped('vtt_car_service_ids')
                service_order_lines = repair.mapped('order_line_ids').filtered(lambda line: line.vtt_car_service_id)
                services_2_remove = service_order_lines.filtered(lambda line: line.vtt_car_service_id not in services)
                services_2_add = services.filtered(lambda service: service not in [l.vtt_car_service_id for l in service_order_lines])

                if services_2_remove:
                    services_2_remove.unlink()
                if services_2_add:
                    s_list = []
                    for s in services_2_add:
                        vals = {
                            'vtt_car_service_id': s.id,
                        }
                        if s.product_id:
                            partner = repair.partner_id
                            pricelist = repair.pricelist_id
                            price = pricelist.get_product_price(s.product_id, 1.0, partner,
                                                                uom_id=s.product_id.uom_id.id)
                            vals['product_id'] = s.product_id.id
                            vals['name'] = s.product_id.display_name
                            vals['price_unit'] = price
                            vals['product_uom'] = s.product_id.uom_id.id
                            if s.product_id.description_sale:
                                if self.partner_id:
                                    vals['name'] += '\n' + s.product_id.with_context(lang=self.partner_id.lang).description_sale
                                else:
                                    vals['name'] += '\n' + s.product_id.description_sale
                        else:
                            vals['name'] = s.name
                            vals['price_unit'] = 0.0
                            vals['product_uom'] = s.env.ref('uom.product_uom_unit').id
                        s_list.append((0, 0, vals))
                    repair.write({
                        'order_line_ids': s_list
                    })

    def _amount_by_group(self):
        for order in self:
            currency = order.currency_id or order.company_id.currency_id
            fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
            res = {}
            for line in order.order_line_ids:
                price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
                taxes = line.tax_id.compute_all(price_reduce, quantity=line.product_uom_qty, product=line.product_id, partner=order.partner_id)['taxes']
                for tax in line.tax_id:
                    group = tax.tax_group_id
                    res.setdefault(group, {'amount': 0.0, 'base': 0.0})
                    for t in taxes:
                        if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
                            res[group]['amount'] += t['amount']
                            res[group]['base'] += t['base']
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            order.amount_by_group = [(
                l[0].name, l[1]['amount'], l[1]['base'],
                fmt(l[1]['amount']), fmt(l[1]['base']),
                len(res),
            ) for l in res]

    def action_quotation_send(self):
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('vtt_car_repair.vtt_email_template_edi_car_repair_order', raise_if_not_found=False)
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'vtt.car.repair.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            # 'mark_so_as_sent': True,
            # 'custom_layout': "mail.mail_notification_paynow",
            # 'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': _('Quotation') if self.state in ['draft'] else _('Order'),
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }