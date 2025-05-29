# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class BarcodeScanWizard(models.TransientModel):
    _name = 'vtt.barcode.scan.wz'
    _description = 'Barcode Scan Wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    barcode = fields.Char('Barcode')

    qty = fields.Float('Quantity')
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial')
    product_id = fields.Many2one('product.product', 'Product')

    # move_id = fields.Many2one('stock.move', 'Move')
    # move_line_id = fields.Many2one('stock.move.line', 'Move Line')

    packing_specification = fields.Integer('Packing Specification', default=1)
    pack_qty = fields.Float('Amount of Packages', store=True, compute='_compute_pack_surplus_qty')
    surplus_qty = fields.Float('Amount of Surplus', store=True, compute='_compute_pack_surplus_qty')

    warning = fields.Boolean('Barcode Warning', compute='_compute_barcode_warning')

    # Vehicle information
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='picking_id.vtt_fleet_vehicle_id')
    driver_id = fields.Many2one('res.partner', 'Driver', related='picking_id.vtt_fleet_driver_id')
    vehicle_license_plate = fields.Char('License Plate', related='picking_id.vtt_fleet_vehicle_id.license_plate')

    location_id = fields.Many2one('stock.location', 'Location')

    lot_available_ids = fields.Many2many('stock.production.lot', string='Available Lots/ Serials')
    location_available_ids = fields.Many2many('stock.location', string='Location')

    option_pick_all = fields.Boolean('Pick All', default=False)

    @api.depends('qty')
    def _compute_pack_surplus_qty(self):
        self.pack_qty = self.qty // (self.packing_specification and self.packing_specification or 1.0)
        self.surplus_qty = self.qty % (self.packing_specification and self.packing_specification or 1.0)

    @api.onchange('pack_qty', 'surplus_qty')
    def onchange_pack_qty(self):
        self.qty = self.pack_qty * self.packing_specification + self.surplus_qty

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.packing_specification = self.product_id.packing_specification

            # lots = self.env['stock.production.lot'].search([
            #     ('product_id', '=', self.product_id.id),
            #     ('product_qty_available', '!=', False)
            # ], limit=1)
            # if lots:
            #     self.lot_id = lots[0]

            # Get Available Lot
            quants_env = self.env['stock.quant'].with_context(vtt_block_expired_lot=self.picking_id.vtt_block_expired)
            quants = quants_env._gather(self.product_id, self.picking_id.location_id).filtered(lambda q: q.quantity > 0.0)
            lot_available_ids = quants.mapped('lot_id')
            loc_available_ids = quants.mapped('location_id')
            self.lot_available_ids = lot_available_ids.ids
            self.location_available_ids = loc_available_ids
            if quants:
                self.lot_id = quants[0].lot_id.id
                self.location_id = quants[0].location_id.id

            picking_moves = self.picking_id.mapped('move_lines')
            # picking_moves = self.picking_id.mapped('move_line_ids_without_package')
            product_moves = picking_moves.filtered(lambda m: m.product_id == self.product_id)
            if product_moves:
                qty = sum(product_moves.mapped('product_uom_qty')) - sum(product_moves.mapped('quantity_done'))
                self.qty = qty if qty > 0.0 else 0.0
            else:
                self.qty = 1.0
        else:
            self.packing_specification = 1
            self.qty = 1.0
            self.lot_available_ids = []
            self.location_available_ids = []
            self.lot_id = False
            self.location_id = False

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            barcode = self.barcode.strip()
            products = self.picking_id.mapped('move_ids_without_package').mapped('product_id').filtered(
                lambda p: p.pack_barcode == barcode or p.product_barcode == barcode
            )
            if not products:
                products = self.env['product.product'].search([
                    '|', ('pack_barcode', '=', barcode),
                    ('product_barcode', '=', barcode)
                ])
            if products:
                picking_moves = self.picking_id.move_ids_without_package
                picking_moves_todo = picking_moves.filtered(lambda m: m.product_uom_qty > m.quantity_done)
                if picking_moves_todo:
                    picking_products = picking_moves_todo.mapped('product_id')
                else:
                    picking_products = picking_moves.mapped('product_id')
                product = products & picking_products
                if product:
                    product_to_add = product[0]
                else:
                    product_to_add = products[0]

                self.product_id = product_to_add

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            moves = self.picking_id.mapped('move_line_ids_without_package').\
                filtered(lambda m: m.product_id == self.product_id and m.lot_id == self.lot_id and m.product_uom_qty > 0.0).sorted(lambda m: -(m.product_uom_qty - m.qty_done))
            quants_env = self.env['stock.quant'].with_context(vtt_block_expired_lot=self.picking_id.vtt_block_expired)
            quants = quants_env._gather(self.product_id, self.picking_id.location_id, lot_id=self.lot_id).filtered(lambda q: q.quantity > 0.0)
            loc_available_ids = quants.mapped('location_id')
            if quants:
                self.location_available_ids = loc_available_ids
                if moves:
                    self.location_id = moves[0].location_id.id
                else:
                    self.location_id = quants[0].location_id.id

    def _compute_barcode_warning(self):
        for wz in self:
            if wz.barcode and not wz.lot_id:
                wz.warning = True
            else:
                wz.warning = False

    def _apply_product_qty(self):
        if self.barcode and self.picking_id and self.lot_id and self.product_id and self.qty > 0:
            moves = self.picking_id.mapped('move_ids_without_package').filtered(
                lambda m: m.product_id == self.product_id
            ).sorted(
                lambda m: -m.quantity_done
            )
            move = moves and moves[0] or False

            quants_env = self.env['stock.quant'].with_context(
                vtt_block_expired_lot=self.picking_id.vtt_block_expired)
            quants = quants_env._gather(self.product_id, self.picking_id.location_id).filtered(lambda q: q.quantity > 0.0)

            move_lines_field = 'move_line_ids_without_package'
            picking_moves = self.picking_id.mapped(move_lines_field).filtered(
                lambda m: m.product_id == self.product_id)

            moves_reserved = picking_moves.filtered(lambda m: 0.0 < m.product_uom_qty > m.qty_done)
            total_moves = self.picking_id.move_lines.filtered(lambda m: m.product_id == self.product_id)
            total_qty = sum(total_moves.mapped('product_uom_qty')) - sum(total_moves.mapped('quantity_done'))
            optional_qty = total_qty - self.qty

            # move_lines = picking_moves.filtered(
            #     lambda m: m.lot_id == self.lot_id and m.location_id == self.location_id).sorted(
            #     lambda m: m.qty_done - m.product_uom_qty)

            qty_reserve = self.qty

            move_lines = picking_moves.filtered(lambda m: m.lot_id and m.location_id)
            priority_line = move_lines.filtered(lambda m: m.lot_id == self.lot_id and m.location_id == self.location_id)
            move_lines -= priority_line

            # priority_quant = quants.filtered(lambda q: q.lot_id == priority_line.lot_id and q.location_id == q.location_id)
            priority_quant = quants_env.search([('location_id.usage','=', 'internal'),
                                                ('lot_id', '=', self.lot_id.id),
                                                ('location_id', '=', self.location_id.id)
                                                ])
            # move_add_vals = []

            if not move:
                move_vals = {
                    'name': self.product_id.name,
                    'product_id': self.product_id.id,
                    'product_uom': self.product_id.uom_id.id,
                    'location_id': self.picking_id.location_id.id,
                    'location_dest_id': self.picking_id.location_dest_id.id,
                    'product_uom_qty': self.qty,
                    'price_unit': self.product_id.list_price,
                }
                self.picking_id.write({'move_ids_without_package': [(0, 0, move_vals)]})
                move = self.picking_id.mapped('move_ids_without_package').filtered(lambda m: m.product_id == self.product_id)

            qty_need = qty_reserve
            # qty_need = move.product_uom_qty - move.reserved_availability
            # move._do_unreserve()

            # # qty_reserve = self.qty
            # if qty_reserve > qty_need:
            #     qty_need = qty_reserve

            lines_2_update = {}

            if priority_line in moves_reserved:
                m_qty = priority_line.product_uom_qty
                if m_qty > qty_reserve:
                    m_qty = qty_reserve
                lines_2_update.update({(priority_quant.location_id, priority_quant.lot_id): m_qty})
                qty_reserve -= m_qty
                moves_reserved -= priority_line
            else:
                priority_quant_qty = sum([q.quantity - q.reserved_quantity for q in priority_quant])
                if priority_quant_qty > qty_reserve:
                    priority_quant_qty = qty_reserve
                move._update_reserved_quantity(qty_reserve, priority_quant_qty, priority_quant.location_id, priority_quant.lot_id)
                lines_2_update.update({(priority_quant.location_id, priority_quant.lot_id): priority_quant_qty})
                qty_reserve -= priority_quant_qty

            if priority_quant in quants:
                quants -= priority_quant

            if qty_reserve:
                nd_moves = moves_reserved.filtered(lambda m: m.lot_id == self.lot_id)
                for nd_move in nd_moves:
                    if qty_reserve > 0.0:
                        nd_move_qty = nd_move.product_uom_qty
                        if nd_move_qty > qty_reserve:
                            nd_move_qty = qty_reserve
                        lines_2_update.update({(nd_move.location_id, nd_move.lot_id): nd_move_qty})
                        qty_reserve -= nd_move_qty

                if qty_reserve > 0.0:
                    nd_quants = quants.filtered(lambda q: q.lot_id == self.lot_id and q.quantity - q.reserved_quantity > 0.0)
                    for nd_quant in nd_quants:
                        if qty_reserve > 0.0:
                            nd_quant_qty = nd_quant.quantity - nd_quant.reserved_quantity
                            if nd_quant_qty > qty_reserve:
                                nd_quant_qty = qty_reserve

                            move._update_reserved_quantity(qty_reserve, nd_quant_qty, nd_quant.location_id, nd_quant.lot_id)
                            if (nd_quant.location_id, nd_quant.lot_id) in lines_2_update:
                                lines_2_update[(nd_quant.location_id, nd_quant.lot_id)] += nd_quant_qty
                            else:
                                lines_2_update.update({(nd_quant.location_id, nd_quant.lot_id): nd_quant_qty})
                            qty_reserve -= nd_quant_qty

            if qty_reserve or (self.option_pick_all and optional_qty):
                if self.option_pick_all:
                    qty_reserve = optional_qty
                rd_moves = moves_reserved.filtered(lambda m: m.lot_id != self.lot_id)
                for rd_move in rd_moves:
                    if qty_reserve > 0.0:
                        rd_move_qty = rd_move.product_uom_qty
                        if rd_move_qty > qty_reserve:
                            rd_move_qty = qty_reserve
                        lines_2_update.update({(rd_move.location_id, rd_move.lot_id): rd_move_qty})
                        qty_reserve -= rd_move_qty

                if qty_reserve:
                    rd_quants = quants.filtered(lambda q: q.lot_id != self.lot_id and q.quantity - q.reserved_quantity > 0.0)
                    for rd_quant in rd_quants:
                        if qty_reserve > 0.0:
                            rd_quant_qty = rd_quant.quantity - rd_quant.reserved_quantity
                            if rd_quant_qty > qty_reserve:
                                rd_quant_qty = qty_reserve

                            move._update_reserved_quantity(qty_reserve, rd_quant_qty, rd_quant.location_id, rd_quant.lot_id)
                            if (rd_quant.location_id, rd_quant.lot_id) in lines_2_update:
                                lines_2_update[(rd_quant.location_id, rd_quant.lot_id)] += rd_quant_qty
                            else:
                                lines_2_update.update({(rd_quant.location_id, rd_quant.lot_id): rd_quant_qty})
                            qty_reserve -= rd_quant_qty

            # Update qty done
            move_line_ids = move.mapped('move_line_ids')
            for c in lines_2_update:
                c_line = move_line_ids.filtered(lambda l: l.location_id == c[0] and l.lot_id == c[1])
                if c_line:
                    c_line[0].qty_done = c_line[0].qty_done + lines_2_update[c]

            move._recompute_state()

            """
            if priority_line:
                qty_need = qty_reserve
                qty_reserved = priority_line.product_uom_qty
                # quant = quants.filtered(lambda q: q.lot_id == priority_line.lot_id and q.location_id == q.location_id)
                quant_qty = sum([q.quantity - q.reserved_quantity for q in priority_quant]) + qty_reserved
                if quant_qty:
                    if quant_qty < qty_reserve:
                        qty_need = quant_qty
                        if priority_quant in quants:
                            quants -= priority_quant
                    priority_line.qty_done = priority_line.qty_done + qty_need
                    qty_reserve -= qty_need
                else:
                    if priority_quant in quants:
                        quants -= priority_quant
            else:
                if priority_quant in quants:
                    quants -= priority_quant
                quants = priority_quant | quants

            while qty_reserve > 0.0 and quants:
                quant = quants[0]
                quant_move = move_lines.filtered(
                    lambda m: m.lot_id == quant.lot_id and m.location_id == quant.location_id)
                qty_need = qty_reserve
                qty_reserved = quant_move.product_uom_qty
                quant_qty = quant.quantity - quant.reserved_quantity + qty_reserved
                if quant_qty:
                    if quant_qty <= qty_reserve:
                        qty_need = quant_qty
                        quants -= quant

                    if quant_move:
                        quant_move.qty_done = quant_move.qty_done + qty_need
                    else:
                        vals = {
                            'picking_id': self.picking_id.id,
                            'location_id': quant.location_id.id,
                            'location_dest_id': self.picking_id.location_dest_id.id,
                            'product_id': self.product_id.id,
                            'product_uom_id': self.lot_id.product_id.uom_id.id,
                            'lot_id': quant.lot_id.id,
                            'qty_done': qty_need,
                        }
                        # if self.location_id:
                        #     vals['location_id'] = self.location_id.id
                        if move:
                            vals['move_id'] = move.id

                        move_add_vals.append((0, 0, vals))
                else:
                    quants -= quant

                qty_reserve -= qty_need

            if move_add_vals:
                self.picking_id.write({
                    'move_line_ids_without_package': move_add_vals
                })

        # Assign for move
        if move:
            # move._action_assign()
            missing_reserved_uom_quantity = move.product_uom_qty - move.reserved_availability
            if missing_reserved_uom_quantity:
                missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity,
                                                                               move.product_id.uom_id,
                                                                               rounding_method='HALF-UP')
                move._update_reserved_quantity(missing_reserved_quantity, self.qty,
                                               self.location_id and self.location_id or move.location_id, strict=False)
            move._action_assign()
        # self.picking_id.mapped('move_line_ids_without_package').mapped('move_id')._action_assign()
        """

        self.barcode = ''
        self.lot_id = False
        self.product_id = False
        self.qty = 0.0
        self.packing_specification = 1
        self.pack_qty = 0.0
        self.surplus_qty = 0.0

    def apply_product_qty(self):
        self._apply_product_qty()
        return {'type': 'ir.actions.act_window_close'}

    def apply_product_qty_and_continue(self):
        self._apply_product_qty()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Barcode Scan Wizard'),
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            'context': {
                'barcode': '',
            }
        }