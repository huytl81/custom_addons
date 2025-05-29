# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SupplyRequestLine(models.Model):
    _name = 'vtt.supply.request.line'
    _description = 'Supply Request Line'

    request_id = fields.Many2one('vtt.supply.request', 'Request')
    company_id = fields.Many2one(related="request_id.company_id", index=True, store=True)

    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', 'Product')
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure',
                             compute='_compute_product_uom',
                             store=True, readonly=False, precompute=True, ondelete='restrict', )
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', depends=['product_id'])
    product_uom_qty = fields.Float('Quantity', default=1.0)

    sequence = fields.Integer(string='Sequence', default=10)

    state = fields.Selection(
        related='request_id.state',
        string="Request Status",
        copy=False, store=True, precompute=True)

    qty_delivered = fields.Float(
        string="Delivery Quantity",
        compute='_compute_qty_delivered',
        digits='Product Unit of Measure',
        store=True, readonly=False, copy=False)
    qty_picking = fields.Float(
        string="Picking Quantity",
        compute='_compute_qty_delivered',
        digits='Product Unit of Measure',
        store=True)

    @api.depends('product_id')
    def _compute_product_uom(self):
        for line in self:
            if not line.product_id:
                continue
            else:
                if not line.uom_id or (line.product_id.uom_id.id != line.uom_id.id):
                    line.uom_id = line.product_id.uom_id

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id and not self.name:
            self.name = self.product_id.name

    @api.depends('request_id.picking_ids.move_ids.state', 'request_id.picking_ids.move_ids.scrapped', 'request_id.picking_ids.move_ids.quantity', 'request_id.picking_ids.move_ids.product_uom')
    def _compute_qty_delivered(self):
        for line in self:
            if line.product_id:
                if line.product_id.type == 'service':
                    if line.state in ('confirm', 'done'):
                        line.qty_delivered = line.product_uom_qty
                        line.qty_picking = line.product_uom_qty
                    else:
                        line.qty_delivered = 0.0
                        line.qty_picking = 0.0
                else:
                    qty = 0.0
                    outgoing_moves, incoming_moves = line._get_outgoing_incoming_moves()

                    incoming_moves_filtered = incoming_moves.filtered(lambda m: m.state != 'draft')
                    qty_picking_in = sum([m.product_uom._compute_quantity(m.product_uom_qty, line.uom_id, rounding_method='HALF-UP') for m in incoming_moves_filtered])
                    qty_picking_out = sum([m.product_uom._compute_quantity(m.product_uom_qty, line.uom_id, rounding_method='HALF-UP') for m in outgoing_moves])
                    qty_picking = qty_picking_out - qty_picking_in

                    for move in outgoing_moves:
                        if move.state != 'done':
                            continue
                        qty += move.product_uom._compute_quantity(move.quantity, line.uom_id, rounding_method='HALF-UP')
                    for move in incoming_moves:
                        if move.state != 'done':
                            continue
                        qty -= move.product_uom._compute_quantity(move.quantity, line.uom_id, rounding_method='HALF-UP')
                    line.qty_delivered = qty
                    line.qty_picking = qty_picking if qty_picking >= 0.0 else 0.0

    def _prepare_delivery_amount(self):
        self.ensure_one()
        picking_type_id = self.request_id.warehouse_id.int_type_id
        qty = self.product_uom_qty - self.qty_picking
        qty_available = 0.0
        if qty > 0.0:
            qty_available = qty
        amount = {
            'product_id': self.product_id.id,
            'name': self.name,
            'product_uom': self.uom_id.id,
            'product_uom_qty': qty_available,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': self.request_id.location_dest_id.id,
        }
        return amount

    def _get_lang(self):
        return self.request_id.request_user_id.partner_id.lang or self.env.user.lang

    def _get_outgoing_incoming_moves(self):
        outgoing_moves = self.env['stock.move']
        incoming_moves = self.env['stock.move']

        moves = self.request_id.picking_ids.mapped('move_ids').filtered(lambda r: r.state != 'cancel' and not r.scrapped and self.product_id == r.product_id)

        for move in moves:
            if move.location_dest_id == self.request_id.location_dest_id:
                if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                    outgoing_moves |= move
            elif move.location_dest_id != self.request_id.location_dest_id and move.to_refund:
                incoming_moves |= move

        return outgoing_moves, incoming_moves
