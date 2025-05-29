# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from more_itertools import chunked, divide


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    _order = "sequence, result_package_id desc, location_id asc, location_dest_id asc, picking_id, id"

    note = fields.Text('Note')
    need_note = fields.Boolean('Need Note?', compute='_compute_need_note')

    vtt_pack_qty = fields.Float('Amount of Packages', digits='Product Unit of Measure', compute='_compute_pack_surplus_qty', store=True)
    vtt_surplus_qty = fields.Float('Amount of Surplus', digits='Product Unit of Measure', compute='_compute_pack_surplus_qty', store=True)

    sequence = fields.Integer('Sequence', default=1)

    vtt_fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='picking_id.vtt_fleet_vehicle_id', store=True)
    vtt_fleet_driver_id = fields.Many2one('res.partner', 'Driver', related='picking_id.vtt_fleet_driver_id', store=True)

    vtt_location_alter_id = fields.Many2one('stock.location', 'Alter Location')

    product_default_code = fields.Char('Product Default Code', related='product_id.default_code')
    product_name = fields.Char('Product Name', related='product_id.name')

    def make_empty_copy(self):
        self.ensure_one()
        product = self.product_id
        vals = {
            'product_id': self.product_id.id,
            # 'lot_name': lot_name,
            'move_id': self.move_id.id,
            'picking_id': self.picking_id.id,
            'product_uom_id': self.product_uom_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'sequence': self.sequence,
            'note': self.note,
        }
        # self.picking_id.update({
        #     'move_line_ids': [(0, 0, vals)]
        # })
        field_name = 'move_line_ids'
        if self.picking_id.picking_type_code == 'incoming':
            field_name = 'move_line_nosuggest_ids'
        elif self.picking_id.picking_type_code in ('outgoing', 'internal'):
            field_name = 'move_line_ids_without_package'
        self.picking_id.update({
            field_name: [(0, 0, vals)]
        })

    def make_2_split(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Move Line Split Wizard'),
            'view_mode': 'form',
            'res_model': 'vtt.stock.move.line.split.wz',
            'context': {
                'move_line_id': self.id,
                'default_move_line_id': self.id,
            },
            # 'domain': [('employee_id', '=', self.id)],
            'target': 'new',
        }

    def action_internal_transfer(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Internal Transfer Wizard'),
            'view_mode': 'form',
            'res_model': 'vtt.stock.internal.transfer.wz',
            'context': {
                'move_line_id': self.id,
                'picking_id': self.picking_id.id,
                'default_move_line_id': self.id,
                'default_picking_id': self.picking_id.id,
            },
            'target': 'new',
        }

    def get_all_from_loc(self):
        for move in self:
            if move.product_id and move.location_id:
                quant = self.env['stock.quant'].search([
                    ('product_id', '=', move.product_id.id),
                    ('location_id', '=', move.location_id.id)
                ])
                if quant and quant.quantity > 0.0 and quant.reserved_quantity == 0.0:
                    move.qty_done = quant.quantity

    @api.depends('qty_done', 'product_id.packing_specification')
    def _compute_pack_surplus_qty(self):
        for m in self:
            qty = m.qty_done
            packing_specification = m.product_id and m.product_id.packing_specification or 1.0
            m.vtt_pack_qty = qty // packing_specification
            m.vtt_surplus_qty = qty % packing_specification

    @api.onchange('vtt_pack_qty', 'vtt_surplus_qty')
    def onchange_pack_surplus_qty(self):
        packing_specification = self.product_id and self.product_id.packing_specification or 1.0
        self.qty_done = self.vtt_pack_qty * packing_specification + self.vtt_surplus_qty

    @api.onchange('expiration_date')
    def onchange_line_expiration_date(self):
        if self.expiration_date:
            product_expiration_time = self.product_id.expiration_time
            self.vtt_production_date = self.expiration_date - timedelta(days=product_expiration_time)

    def _compute_need_note(self):
        for move_line in self:
            date = datetime.now()
            picking_type_check_str = self.env['ir.config_parameter'].sudo().get_param(
                'vtt_minhduong_config.picking_type_expiration_warn_note',
                ''
            )
            lst_picking_type_check = picking_type_check_str.split(',')
            need_note = False
            if move_line.picking_id.picking_type_code in lst_picking_type_check:
                if move_line.product_id and move_line.product_id.use_expiration_date and not move_line.note:
                    if move_line.expiration_date and move_line.vtt_production_date:
                        if move_line.product_id.vtt_show_expiration_percentage:
                            if move_line.vtt_expiration_percentage < move_line.product_id.vtt_use_time_percentage:
                                need_note = True
                        else:
                            production_date = fields.Datetime.to_datetime(move_line.vtt_production_date)
                            product_expiration_time = (move_line.expiration_date - production_date).days
                            if product_expiration_time:
                                product_use_time_percentage = move_line.product_id.use_time / product_expiration_time * 100
                            else:
                                product_use_time_percentage = 0
                            if move_line.vtt_expiration_percentage < product_use_time_percentage:
                                need_note = True

            move_line.need_note = need_note