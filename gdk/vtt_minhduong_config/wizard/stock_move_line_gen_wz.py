# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMoveLineGenWizard(models.TransientModel):
    _name = 'vtt.stock.move.line.gen.wz'
    _description = 'Stock Move Line Generate Wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    line_ids = fields.One2many('vtt.stock.move.line.gen.wz.line', 'wz_id', 'Details')

    lot_count_set = fields.Integer('Lot Count Set')

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        if self.picking_id:
            moves = self.picking_id.mapped('move_lines')
            moves.filtered(lambda m: m.product_id.tracking == 'lot' and m.product_uom_qty > 0.0)
            lines = [(0, 0, {
                'move_id': m.id,
                'lot_count': 1,
            }) for m in moves]
            self.line_ids = lines

    def action_clear_all_count(self):
        self.line_ids.lot_count = 0
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Move Line Generate Wizard'),
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            # 'breadcrumb': _('Stock Move Line Generate Wizard'),
        }

    def action_set_all_count(self):
        self.line_ids.lot_count = self.lot_count_set
        return {
            'type': 'ir.actions.act_window',
            'name': _('Stock Move Line Generate Wizard'),
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'target': 'new',
            # 'breadcrumb': _('Stock Move Line Generate Wizard'),
        }

    def gen_picking_move_line(self):
        # new_move_lines = []
        for line in self.line_ids:
            new_move_lines = []
            product = line.move_id.product_id
            if line.lot_count:
                for i_index in range(line.lot_count):
                    new_move_lines.append((0, 0, {
                        'move_id': line.move_id.id,
                        'sequence': line.move_id.sequence,
                        'product_id': product.id,
                        # 'qty_done': 1.0,
                        'picking_id': self.picking_id.id,
                        'product_uom_id': line.move_id.product_uom.id,
                        'location_id': line.move_id.location_id.id,
                        'location_dest_id': line.move_id.location_dest_id.id,
                    }))
                if new_move_lines:
                    line.move_id.write({'move_line_ids': new_move_lines})


class StockMoveLineGenWizardLine(models.TransientModel):
    _name = 'vtt.stock.move.line.gen.wz.line'

    wz_id = fields.Many2one('vtt.stock.move.line.gen.wz', 'Wizard')
    move_id = fields.Many2one('stock.move', 'Move')
    product_id = fields.Many2one(related='move_id.product_id', string='Product')
    product_default_code = fields.Char(related='move_id.product_id.default_code', string='Default Code')

    lot_count = fields.Integer('Lot To Generate')