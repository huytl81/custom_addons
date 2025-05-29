# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vtt_return_line_ids = fields.One2many('vtt.sale.order.return.line', 'order_id', 'Returns')
    vtt_return_line_ref_ids = fields.One2many('vtt.sale.order.return.line', 'ref_order_id', 'Returns')

    ref_picking_ids = fields.One2many('stock.picking', 'ref_sale_id', 'All Pickings')
    ref_invoice_ids = fields.Many2many("account.move", string='Ref Invoices', compute="_get_invoiced", readonly=True, copy=False)

    vtt_is_returned = fields.Boolean('All Returned?', compute='_compute_vtt_returned')
    vtt_is_refunded = fields.Boolean('All Refunded?', compute='_compute_vtt_returned')

    vtt_return_amount_total = fields.Monetary('Total Return Amount', store=True, readonly=True, compute='_amount_return_all')
    vtt_return_amount_tax = fields.Monetary(string='Return Taxes', store=True, readonly=True, compute='_amount_return_all')
    vtt_return_amount_untaxed = fields.Monetary(string='Untaxed Return Amount', store=True, readonly=True, compute='_amount_return_all')

    vtt_net_amount_total = fields.Monetary('Total Net Amount', store=True, readonly=True, compute='_amount_net_all')
    vtt_net_amount_untaxed = fields.Monetary(string='Untaxed Net Amount', store=True, readonly=True, compute='_amount_net_all')

    def _compute_vtt_returned(self):
        for order in self:
            lines = order.mapped('vtt_return_line_ref_ids')
            returned = True
            refunded = True
            if lines:
                if any(not line.is_returned for line in lines):
                    returned = False
                if any(not line.is_invoiced for line in lines):
                    refunded = False
            order.vtt_is_returned = returned
            order.vtt_is_refunded = refunded

    @api.depends('order_line.invoice_lines', 'vtt_return_line_ref_ids.invoice_line_ids')
    def _get_invoiced(self):
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            ref_invoices = order.vtt_return_line_ref_ids.invoice_line_ids.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.ref_invoice_ids = ref_invoices
            order.invoice_ids = invoices
            order.invoice_count = len(invoices) + len(ref_invoices)

    @api.depends('vtt_return_amount_total', 'amount_total')
    def _amount_net_all(self):
        for order in self:
            order.vtt_net_amount_total = order.amount_total - order.vtt_return_amount_total
            order.vtt_net_amount_untaxed = order.amount_untaxed - order.vtt_return_amount_untaxed

    @api.depends('vtt_return_line_ref_ids.price_total')
    def _amount_return_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.vtt_return_line_ref_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'vtt_return_amount_untaxed': amount_untaxed,
                'vtt_return_amount_tax': amount_tax,
                'vtt_return_amount_total': amount_untaxed + amount_tax,
            })

    def return_product_other_order(self):
        self.ensure_one()
        pickings = []

        line_2_return = self.mapped('vtt_return_line_ref_ids').filtered(lambda l: not l.is_returned)

        if line_2_return:
            for line in line_2_return:
                so_pickings = line.order_id.mapped('picking_ids')
                fil_pickings = so_pickings.filtered(lambda p: line.product_id in p.move_lines.product_id and p.state == 'done')
                moves = fil_pickings.mapped('move_lines').filtered(lambda m: m.product_id == line.product_id).sorted('date', reverse=True)
                if moves:
                    if moves[0].picking_id not in [p['picking_id'] for p in pickings]:
                        pickings.append({
                            'picking_id': moves[0].picking_id,
                            'moves': []
                        })
                    for p in pickings:
                        if p['picking_id'] == moves[0].picking_id:
                            p['moves'].append((line, moves[0]))

            if pickings:
                for p in pickings:
                    pick = p['picking_id']
                    picking_type_id = pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
                    new_picking = pick.copy({
                        'move_lines': [],
                        'picking_type_id': picking_type_id,
                        'state': 'draft',
                        'origin': _("Return of %s", pick.name),
                        'location_id': pick.location_dest_id.id,
                        'location_dest_id': pick.location_id.id,
                        'ref_sale_id': self.id
                    })
                    for m in p['moves']:
                        r_line = m[0]
                        move = m[1]
                        r_qty = r_line.product_uom_qty - r_line.qty_returned
                        qty = r_line.product_uom._compute_quantity(r_qty, r_line.product_id.uom_id, rounding_method='HALF-UP')
                        vals = {
                            'product_id': r_line.product_id.id,
                            'product_uom_qty': qty,
                            'product_uom': r_line.product_id.uom_id.id,
                            'picking_id': new_picking.id,
                            'state': 'draft',
                            'date': fields.Datetime.now(),
                            'location_id': move.location_dest_id.id,
                            'location_dest_id': move.location_id.id,
                            'picking_type_id': new_picking.picking_type_id.id,
                            'warehouse_id': pick.picking_type_id.warehouse_id.id,
                            'origin_returned_move_id': move.id,
                            'procure_method': 'make_to_stock',
                            'to_refund': True,
                            'vtt_return_line_id': r_line.id
                        }
                        r = move.copy(vals)

                        vals = {}

                        move_orig_to_link = move.move_dest_ids.mapped('returned_move_ids')
                        # link to original move
                        move_orig_to_link |= move
                        # link to siblings of original move, if any
                        move_orig_to_link |= move \
                            .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel')) \
                            .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                        move_dest_to_link = move.move_orig_ids.mapped('returned_move_ids')

                        move_dest_to_link |= move.move_orig_ids.mapped('returned_move_ids') \
                            .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel')) \
                            .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                        vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                        vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                        r.write(vals)

                    new_picking.action_confirm()
                    new_picking.action_assign()

    def refund_product_other_order(self):
        self.ensure_one()
        orders = self.vtt_return_line_ref_ids.order_id
        returns = self.mapped('vtt_return_line_ref_ids').filtered(lambda l: not l.is_invoiced)
        for order in orders:
            line_returns = returns.filtered(lambda l: l.order_id == order)
            order_lines = order.mapped('order_line')
            dict_returns = {}
            for lr in line_returns:
                lines = order_lines.filtered(lambda l: l.product_id == lr.product_id and l.invoice_lines)
                if lines:
                    for line in lines:
                        invoices = line.invoice_lines.move_id.filtered(lambda r: r.move_type == 'out_invoice' and r.state == 'posted').sorted(lambda m: m.invoice_date, reverse=True)
                        if invoices:
                            invoice = invoices[0]
                            if invoice.id not in dict_returns:
                                dict_returns.update({
                                    invoice.id: {
                                        'move': invoice,
                                        'order_lines': self.env['sale.order.line'],
                                        'return_lines': self.env['vtt.sale.order.return.line'],
                                        'group_data': []
                                    }
                                })
                            dict_returns[invoice.id]['order_lines'] |= line
                            dict_returns[invoice.id]['return_lines'] |= lr
                            dict_returns[invoice.id]['group_data'].append((line, lr))

            if dict_returns:
                for dr in dict_returns:
                    default_values_list = [{
                        'ref': _('Refund product(s) from Order %s', self.name),
                        'date': fields.Date.today(),
                        'invoice_date': fields.Date.today(),
                        'journal_id': dict_returns[dr]['move'].journal_id.id,
                        'invoice_payment_term_id': None,
                        'invoice_user_id': dict_returns[dr]['move'].invoice_user_id.id,
                        'auto_post': False,
                    }]
                    new_move = dict_returns[dr]['move']._reverse_moves(default_values_list)
                    remove_invoice_lines = new_move.invoice_line_ids.filtered(lambda l: not any(so_line in l.sale_line_ids for so_line in dict_returns[dr]['order_lines']))
                    # remove_invoice_lines.unlink()
                    # Can not direct unlink and modify.
                    # Must update by Odoo model-relation update
                    update_lines = [(2, rm.id) for rm in remove_invoice_lines]

                    for data_return in dict_returns[dr]['group_data']:
                        rl = new_move.invoice_line_ids.filtered(lambda l: data_return[0] in l.sale_line_ids)
                        if rl:
                            # vals = {}
                            # if rl[0].product_uom_id != data_return[1].product_uom:
                            #     vals.update({
                            #         'product_uom_id': data_return[1].product_uom.id,
                            #         'quantity': data_return[1].product_uom._compute_quantity(data_return[1].product_uom_qty, rl[0].product_uom_id, rounding_method='HALF-UP'),
                            #         'discount': 0.0,
                            #     })
                            # else:
                            #     vals.update({
                            #         'quantity': data_return[1].product_uom_qty,
                            #         'discount': 0.0
                            #     })
                            vals = {
                                'product_uom_id': data_return[1].product_uom.id,
                                'quantity': data_return[1].product_uom_qty - data_return[1].qty_invoiced,
                                'discount': 0.0,
                                'price_unit': data_return[1].price_unit,
                                'tax_ids': data_return[1].tax_id,
                                'vtt_return_line_id': data_return[1].id
                            }
                            if vals:
                                update_lines.append((1, rl[0].id, vals))
                                # rl[0].write(vals)
                    if update_lines:
                        new_move.invoice_line_ids = update_lines

    def action_view_delivery(self):
        action = super(SaleOrder, self).action_view_delivery()
        pickings = self.mapped('picking_ids') + self.mapped('ref_picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
            action['views'] = []
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
            action['domain'] = []
        return action

    def action_view_invoice(self):
        # action = super(SaleOrder, self).action_view_invoice()
        ref_invoices = self.env['account.move']
        for order in self:
            order_ref_invoices = order.vtt_return_line_ref_ids.invoice_line_ids.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            ref_invoices |= order_ref_invoices
        invoices = self.mapped('invoice_ids')
        invoices |= ref_invoices
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
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
                'default_partner_shipping_id': self.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.payment_term_id.id or self.partner_id.property_payment_term_id.id or
                                                   self.env['account.move'].default_get(
                                                       ['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.name,
                'default_user_id': self.user_id.id,
            })
        action['context'] = context

        return action

    @api.depends('picking_ids', 'ref_picking_ids')
    def _compute_picking_ids(self):
        for order in self:
            order.delivery_count = len(order.picking_ids) + len(order.ref_picking_ids)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.return_product_other_order()
            order.refund_product_other_order()
        return res

    def view_all_pickings(self):
        return {
            'name': _('All Picking'),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            # 'res_id': new_picking_id,
            'domain': ['|', ('sale_id', '=', self.id), ('ref_sale_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            # 'context': ctx,
            'target': 'current'
        }


class VttSaleOrderReturnLine(models.Model):
    _name = 'vtt.sale.order.return.line'
    _description = 'Sale Order Return Line'

    order_id = fields.Many2one('sale.order', 'Sale Order')
    ref_order_id = fields.Many2one('sale.order', 'Ref Order')

    partner_id = fields.Many2one('res.partner', 'Partner')

    product_id = fields.Many2one('product.product', 'Product')
    product_template_id = fields.Many2one('product.template', string='Product Template', related="product_id.product_tmpl_id")
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)

    sale_order_domain = fields.Char('Order Domain', compute='_compute_order_domain')

    is_returned = fields.Boolean('All Returned?', compute='_compute_qty_delivered', store=True)
    qty_returned = fields.Float('Returned', compute='_compute_qty_delivered', store=True)
    move_ids = fields.One2many('stock.move', 'vtt_return_line_id', 'Moves')

    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

    price_subtotal = fields.Float(compute='_compute_return_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_return_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Float(compute='_compute_return_amount', string='Total', readonly=True, store=True)

    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    is_invoiced = fields.Boolean('All Invoiced?', compute='_compute_qty_invoiced', store=True)
    qty_invoiced = fields.Float('Invoiced', compute='_compute_qty_invoiced', store=True)
    invoice_line_ids = fields.One2many('account.move.line', 'vtt_return_line_id', 'Invoice Lines')

    @api.depends('invoice_line_ids', 'invoice_line_ids.parent_state', 'product_uom_qty', 'product_uom')
    def _compute_qty_invoiced(self):
        for l in self:
            qty_return = 0.0
            moves = l.mapped('invoice_line_ids').filtered(lambda m: m.parent_state != 'cancel')
            for move in moves:
                qty_return += move.product_uom_id._compute_quantity(move.quantity, l.product_uom,
                                                                 rounding_method='HALF-UP')
            l.qty_invoiced = qty_return
            if l.product_uom_qty == qty_return:
                l.is_invoiced = True
            else:
                l.is_invoiced = False

    @api.depends('move_ids', 'move_ids.state', 'product_uom_qty', 'product_uom')
    def _compute_qty_delivered(self):
        for l in self:
            qty_return = 0.0
            moves = l.mapped('move_ids').filtered(lambda m: m.state != 'cancel')
            for move in moves:
                qty_return += move.product_uom._compute_quantity(move.product_uom_qty, l.product_uom, rounding_method='HALF-UP')
            l.qty_returned = qty_return
            if l.product_uom_qty == qty_return:
                l.is_returned = True
            else:
                l.is_returned = False

    @api.onchange('order_id', 'product_id')
    def onchange_product(self):
        if self.order_id and self.product_id:
            lines = self.order_id.mapped('order_line')
            line = lines.filtered(lambda l: l.product_id == self.product_id)[0]
            # self.price_unit = line.price_unit
            self.price_unit = line.price_reduce
            self.product_uom = line.product_uom
            self.tax_id = line.tax_id

    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_return_amount(self):
        for line in self:
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('product_id', 'partner_id')
    def _compute_order_domain(self):
        for l in self:
            domain = [('partner_id', '=', l.partner_id.id), ('order_line.product_id', 'in', [l.product_id.id]), ('state', 'in', ['sale', 'done'])]
            l.sale_order_domain = json.dumps(domain)
