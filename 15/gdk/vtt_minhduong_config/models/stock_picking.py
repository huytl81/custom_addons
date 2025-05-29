# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = "priority desc, scheduled_date desc, id desc"

    vtt_block_expired = fields.Boolean('Block Expired Lot', default=True)
    # need_note = fields.Boolean('Need Note?', compute='_compute_need_note', store=True)

    vtt_fleet_vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    vtt_fleet_driver_id = fields.Many2one('res.partner', 'Driver')
    vehicle_license_plate = fields.Char('License Plate', related='vtt_fleet_vehicle_id.license_plate')

    vtt_amount_total = fields.Float('Amount Total', compute='_compute_vtt_amount', store=True)
    vtt_amount_confirm = fields.Float('Amount Confirm', compute='_compute_vtt_amount', store=True)
    vtt_amount_demand = fields.Float('Amount Demand', compute='_compute_vtt_amount', store=True)

    origin = fields.Char(states={'cancel': [('readonly', True)]}, tracking=True)
    date_done = fields.Datetime(readonly=False, tracking=True)

    vtt_amount_pack_qty = fields.Float('Amount of Packages', compute='_compute_amount_pack')
    vtt_amount_surplus_qty = fields.Float('Amount of Surplus', compute='_compute_amount_pack')
    vtt_done_pack_qty = fields.Float('Done of Packages', compute='_compute_amount_pack')
    vtt_done_surplus_qty = fields.Float('Done of Surplus', compute='_compute_amount_pack')

    def _compute_amount_pack(self):
        field_name = 'move_ids_without_package'
        for picking in self:
            moves = picking.mapped(field_name).filtered(lambda m: m.state not in ['cancel'])
            pack_qty = sum(moves.mapped('vtt_pack_qty'))
            surplus_qty = sum(moves.mapped('vtt_surplus_qty'))
            picking.vtt_amount_pack_qty = pack_qty
            picking.vtt_amount_surplus_qty = surplus_qty

            # pack_qty_done = 0.0
            # surplus_qty_done = 0.0
            # for move in moves:
            #     packing_specification = move.product_id.packing_specification
            #     pack_qty_done += move.quantity_done // packing_specification
            #     surplus_qty_done += move.quantity_done % packing_specification
            pack_qty_done = sum([move.quantity_done // move.product_id.packing_specification and move.product_id.packing_specification or 1.0 for move in moves])
            surplus_qty_done = sum([move.quantity_done % move.product_id.packing_specification and move.product_id.packing_specification or 1.0 for move in moves])
            picking.vtt_done_pack_qty = pack_qty_done
            picking.vtt_done_surplus_qty = surplus_qty_done

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if res and vals.get('date_done') and vals.get('state', False) is False:
            dt = vals.get('date_done')
            moves = self.mapped('move_lines')
            moves.write({'date': dt})

            move_lines = self.mapped('move_line_ids')
            move_lines.write({'date': dt})

        return res

    @api.depends('move_lines', 'move_lines.vtt_amount_total', 'move_lines.vtt_amount_confirm',
                 'move_lines.vtt_amount_demand', 'move_lines.state')
    def _compute_vtt_amount(self):
        for picking in self:
            # moves = picking.move_lines.filtered(lambda m: m.state != 'cancel')
            moves = picking.move_lines
            amount_total = 0.0
            amount_confirm = 0.0
            amount_demand = 0.0
            for m in moves:
                amount_total += m.vtt_amount_total
                amount_confirm += m.vtt_amount_confirm
                amount_demand += m.vtt_amount_demand
            picking.vtt_amount_total = amount_total
            picking.vtt_amount_confirm = amount_confirm
            picking.vtt_amount_demand = amount_demand

    @api.onchange('vtt_fleet_vehicle_id')
    def onchange_vtt_fleet_vehicle_id(self):
        if self.vtt_fleet_vehicle_id:
            self.vtt_fleet_driver_id = self.vtt_fleet_vehicle_id.driver_id

    def expiration_time_percentage_update(self):
        self.mapped('move_line_ids')._compute_expiration_time_percentage()
        return

    def button_validate(self):
        date = datetime.now()
        picking_type_check_str = self.env['ir.config_parameter'].sudo().get_param(
            'vtt_minhduong_config.picking_type_expiration_warn_note',
            ''
        )

        lst_picking_type_check = picking_type_check_str.split(',')
        pickings = self.filtered(lambda picking: picking.picking_type_code in lst_picking_type_check)
        move_lines = self.env['stock.move.line']
        for p in pickings:
            if p.picking_type_code == 'incoming':
                move_lines |= pickings.mapped('move_line_nosuggest_ids')
            elif p.picking_type_code in ('outgoing', 'internal'):
                move_lines |= pickings.mapped('move_line_ids_without_package')
        need_note = False
        if move_lines:
            for move_line in move_lines:
                if move_line.product_id and move_line.product_id.use_expiration_date and not move_line.note:
                    if move_line.expiration_date and move_line.vtt_production_date:
                        if not move_line.product_id.vtt_use_production_date:
                            product_expiration_time = move_line.product_id.expiration_time
                        else:
                            production_date = fields.Datetime.to_datetime(move_line.vtt_production_date)
                            product_expiration_time = (move_line.expiration_date - production_date).days

                        date_diff = (move_line.expiration_date - date).days
                        if move_line.product_id.vtt_show_expiration_percentage:
                            if date_diff and product_expiration_time:
                                if date_diff / product_expiration_time * 100 < move_line.product_id.vtt_use_time_percentage:
                                    need_note = True
                                    break
                        else:
                            if date_diff < move_line.product_id.use_time:
                                need_note = True
                                break
        if need_note:
            raise ValidationError(_('Some of your details line need to note the reason before proceed.'))
        else:
            res = super(StockPicking, self).button_validate()
            if res:
                picking_2_make_alter = self.filtered(lambda p: p.state == 'done')
                picking_2_make_alter.action_create_alter_internal_picking()
            return res

    def action_create_alter_internal_picking(self):
        picking_type_id = self.env.ref('stock.picking_type_internal')
        field_name_internal = 'move_line_ids_without_package'
        picking_val_list = []
        for picking in self:
            field_name = 'move_line_ids'
            if picking.picking_type_code == 'incoming':
                field_name = 'move_line_nosuggest_ids'
            elif picking.picking_type_code in ('outgoing', 'internal'):
                field_name = 'move_line_ids_without_package'

            picking_vals = {
                'user_id': self.env.user.id,
                'picking_type_id': picking_type_id.id,
                'date': fields.Datetime.now(),
                'company_id': picking_type_id.company_id.id,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id,
            }

            moves = picking.mapped(field_name).filtered(lambda m: m.vtt_location_alter_id and m.qty_done > 0.0)
            lot_groups = {}
            for m in moves:
                if (m.lot_id, m.location_id) not in lot_groups:
                    quants = m.lot_id.quant_ids.filtered(lambda q: q.location_id == m.location_id)
                    # Fixed quantity
                    # total_qty = sum(quants.mapped('quantity'))
                    # Reserved quantity
                    total_qty = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
                    move_qty = total_qty - m.qty_done
                    if move_qty > 0:
                        lot_groups[(m.lot_id, m.location_id)] = {
                            'product_id': m.product_id.id,
                            'lot_id': m.lot_id.id,
                            'product_uom_id': m.product_uom_id.id,
                            'location_id': m.location_id.id,
                            'location_dest_id': m.vtt_location_alter_id.id,
                            'qty_done': move_qty,
                            'sequence': m.sequence,
                        }
            if lot_groups:
                move_vals = [(0, 0, lot_groups[k]) for k in lot_groups]
                picking_vals[field_name_internal] = move_vals
                picking_val_list.append(picking_vals)
        if picking_val_list:
            picking_ids = self.create(picking_val_list)
            picking_ids.action_confirm()

    def action_move_line_gen_wz(self):
        # return {
        #     'warning': {
        #         'title': _('Warning'),
        #         'message': _('Existing Serial numbers. Please correct the serial numbers encoded:'),
        #     }
        # }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Move Line Generate Wizard'),
            'view_mode': 'form',
            'res_model': 'vtt.stock.move.line.gen.wz',
            'context': {
                'picking_id': self.id,
                'default_picking_id': self.id,
                'default_lot_count_set': 1,
            },
            # 'domain': [('employee_id', '=', self.id)],
            'target': 'new',
        }

    def action_open_label_layout(self):
        res = super().action_open_label_layout()
        res['context']['default_picking_quantity'] = 'custom'
        res['context']['default_print_format'] = '3x1'
        # Remove product w/o lot in print
        # move_line_ids = self.move_line_ids.filtered(lambda l: l.lot_name).ids
        # res['context']['default_move_line_ids'] = move_line_ids
        # Get move by type
        if self.picking_type_code == 'incoming':
            moves = self.move_line_nosuggest_ids
        elif self.picking_type_code in ('outgoing', 'internal'):
            moves = self.move_line_ids_without_package
        lot_names = []
        move_2_print_ids = []
        for m in moves:
            m_lot_name = m.lot_id and m.lot_id.name or m.lot_name
            if m_lot_name not in lot_names:
                lot_names.append(m_lot_name)
                move_2_print_ids.append(m.id)
        # move_2_print_ids = set(move_2_print_ids)
        # move_2_prints = moves.filtered(lambda m: m.id in move_2_print_ids)
        res['context']['default_move_line_ids'] = move_2_print_ids
        return res

    def action_move_import_wz(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Picking Move Import Wizard'),
            'view_mode': 'form',
            'res_model': 'vtt.stock.picking.move.import.wz',
            'context': {
                'picking_id': self.id,
                'default_picking_id': self.id,
            },
            'target': 'new',
        }

    def action_clear_move_line_ids(self):
        self.ensure_one()
        if self.state not in ['done']:
            moves = self.mapped('move_line_ids')
            moves.unlink()

    def _create_backorder(self):
        for picking in self:
            moves_to_backorder = picking.move_lines.filtered(lambda x: x.state not in ('done', 'cancel'))
            moves_to_backorder.move_line_ids.unlink()
        return super(StockPicking, self)._create_backorder()

    def action_open_barcode_scan_wz(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Barcode Scan Wizard'),
            'view_mode': 'form',
            'res_model': 'vtt.barcode.scan.wz',
            'context': {
                'picking_id': self.id,
                'default_picking_id': self.id,
            },
            'target': 'new',
        }

    def generate_missing_lot_name(self):
        self.ensure_one()
        field_name = 'move_line_ids'
        if self.picking_type_code == 'incoming':
            field_name = 'move_line_nosuggest_ids'
        elif self.picking_type_code in ('outgoing', 'internal'):
            field_name = 'move_line_ids_without_package'
        moves = self.mapped(field_name).filtered(lambda m: m.product_id.tracking == 'lot')
        for m in moves:
            dt_str = m.expiration_date.strftime('%d%m%y')
            lot_name = f'{dt_str}-{m.product_id.default_code}'
            m.lot_name = lot_name

    def action_view_picking_lots(self):
        action = self.env['ir.actions.act_window']._for_xml_id('stock.action_production_lot_form')
        field_name = 'move_line_ids'
        if self.picking_type_code == 'incoming':
            field_name = 'move_line_nosuggest_ids'
        elif self.picking_type_code in ('outgoing', 'internal'):
            field_name = 'move_line_ids_without_package'
        moves = self.mapped(field_name).filtered(lambda m: m.state in ['done'])
        lots = moves.mapped('lot_id')
        action['domain'] = [('id', 'in', lots.ids)]
        return action

    def action_clear_empty_lines(self):
        self.ensure_one()
        move_lines = self.mapped('move_line_ids')
        empty_lines = move_lines.filtered(lambda m: m.qty_done <= 0.0)
        empty_lines.unlink()