# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from more_itertools import chunked, divide


class StockMoveLineSplitWizard(models.TransientModel):
    _name = 'vtt.stock.move.line.split.wz'
    _description = 'Stock Move Line Split Wizard'

    move_line_id = fields.Many2one('stock.move.line', 'Move')
    type = fields.Selection([
        ('number', 'Number'),
        ('quantity', 'Quantity'),
    ], 'Type', default='number')
    amount = fields.Integer('Amount', default=2)

    def split_move(self):
        val_list = []
        qty = self.move_line_id.qty_done
        picking = self.move_line_id.picking_id
        field_name = 'move_line_ids'
        if picking.picking_type_code == 'incoming':
            field_name = 'move_line_nosuggest_ids'
        elif picking.picking_type_code in ('outgoing', 'internal'):
            field_name = 'move_line_ids_without_package'

        # Chunk solution
        # if self.type == 'number':
        #     chunks = [list(d) for d in divide(self.amount, range(int(qty)))]
        # else:
        #     chunks = list(chunked(range(int(qty)), self.amount))

        # Calculate solution
        if self.type == 'number':
            chunks = [qty / self.amount] * self.amount
        else:
            chunks = [self.amount] * int((qty // self.amount)) + [qty % self.amount]

        if chunks and len(chunks) > 1:
            for i_index in range(len(chunks)):
                # Chunk solution
                # chun_qty = len(chunks[i_index])

                # Calculate solution
                chun_qty = chunks[i_index]

                if i_index > 0:
                    vals = {
                        'product_id': self.move_line_id.product_id.id,
                        'lot_name': self.move_line_id.lot_id and self.move_line_id.lot_id.name or self.move_line_id.lot_name,
                        'move_id': self.move_line_id.move_id.id,
                        # 'picking_id': self.picking_id.id,
                        'product_uom_id': self.move_line_id.product_uom_id.id,
                        'location_id': self.move_line_id.location_id.id,
                        'location_dest_id': self.move_line_id.location_dest_id.id,
                        'qty_done': chun_qty,
                        'sequence': self.move_line_id.sequence,
                        'note': self.move_line_id.note,
                        'vtt_production_date': self.move_line_id.vtt_production_date,
                        'expiration_date': self.move_line_id.expiration_date,
                    }
                    val_list.append(vals)

            # Chunk solution
            # self.move_line_id.qty_done = len(chunks[0])

            # Calculate solution
            self.move_line_id.qty_done = chunks[0]
            picking.write({
                field_name: [(0, 0, vals) for vals in val_list]
            })