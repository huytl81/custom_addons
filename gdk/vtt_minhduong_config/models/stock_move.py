# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'
    _order = 'picking_id, sequence, id'

    note = fields.Text('Note')

    vtt_block_expired = fields.Boolean('Block Expired Lot', related='picking_id.vtt_block_expired')

    vtt_demand_qty = fields.Float('Demand Quantity', digits='Product Unit of Measure')

    vtt_pack_qty = fields.Float('Amount of Packages', digits='Product Unit of Measure', compute='_compute_pack_surplus_qty', store=True)
    vtt_surplus_qty = fields.Float('Amount of Surplus', digits='Product Unit of Measure', compute='_compute_pack_surplus_qty', store=True)

    vtt_amount_total = fields.Float('Amount Total', compute='_compute_vtt_amount', store=True)
    vtt_amount_confirm = fields.Float('Amount Confirm', compute='_compute_vtt_amount', store=True)
    vtt_amount_demand = fields.Float('Amount Demand', compute='_compute_vtt_amount', store=True)

    vtt_fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='picking_id.vtt_fleet_vehicle_id', store=True)
    vtt_fleet_driver_id = fields.Many2one('res.partner', 'Driver', related='picking_id.vtt_fleet_driver_id', store=True)

    vtt_qty_due = fields.Float('Due Quantity', compute='_compute_due_qty')
    vtt_pack_qty_due_str = fields.Char('Dues', compute='_compute_due_qty')

    product_default_code = fields.Char('Product Default Code', related='product_id.default_code')
    product_name = fields.Char('Product Name', related='product_id.name')

    @api.depends('quantity_done', 'product_uom_qty')
    def _compute_due_qty(self):
        pack_str = _('Pack')
        odd_str = _('Odd')
        for m in self:
            qty_due = 0
            # if (m.quantity_done >= m.product_uom_qty and m.product_uom_qty > 0) or m.product_uom_qty <= 0:
            #     qty_due = 0
            if 0 < m.quantity_done < m.product_uom_qty:
                qty_due = m.product_uom_qty - m.quantity_done
            if m.quantity_done <= 0 < m.product_uom_qty:
                qty_due = m.product_uom_qty
            packing_specification = m.product_id and m.product_id.packing_specification or 1
            pack_qty = qty_due // packing_specification
            odd_qty = qty_due % packing_specification
            quantity_str = f'{pack_qty}{pack_str} {odd_qty}{odd_str}'

            m.vtt_qty_due = qty_due
            m.vtt_pack_qty_due_str = quantity_str

    @api.depends('vtt_demand_qty', 'price_unit', 'product_uom_qty', 'product_uom_qty', 'quantity_done')
    def _compute_vtt_amount(self):
        for move in self:
            price = move.price_unit
            move.vtt_amount_confirm = price * move.product_uom_qty
            move.vtt_amount_demand = price * move.vtt_demand_qty
            move.vtt_amount_total = price * move.quantity_done

    @api.onchange('vtt_pack_qty', 'vtt_surplus_qty')
    def onchange_pack_surplus_qty(self):
        packing_specification = self.product_id and self.product_id.packing_specification or 1.0
        self.product_uom_qty = self.vtt_pack_qty * packing_specification + self.vtt_surplus_qty

    @api.depends('product_uom_qty', 'product_id.packing_specification')
    def _compute_pack_surplus_qty(self):
        for m in self:
            qty = m.product_uom_qty
            packing_specification = m.product_id and m.product_id.packing_specification or 1.0
            m.vtt_pack_qty = qty // packing_specification
            m.vtt_surplus_qty = qty % packing_specification

    def _get_available_quantity(self, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
        self.ensure_one()
        if self.vtt_block_expired:
            self = self.with_context(vtt_block_expired_lot=True)
        res = super(StockMove, self)._get_available_quantity(location_id, lot_id, package_id, owner_id, strict, allow_negative)
        return res

    def _action_assign(self):
        if self.picking_id.vtt_block_expired:
            self = self.with_context(vtt_block_expired_lot=True)
        super(StockMove, self)._action_assign()

    # def _quantity_done_set(self):
    #     if self.vtt_block_expired:
    #         self = self.with_context(vtt_block_expired_lot=True)
    #     super(StockMove, self)._quantity_done_set()
    
    @api.onchange('vtt_demand_qty')
    def onchange_vtt_demand_qty(self):
        if self.state in ['draft'] and self.vtt_demand_qty:
            self.product_uom_qty = self.vtt_demand_qty

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty)
        res['vtt_demand_qty'] = 0.0
        return res
