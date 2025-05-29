# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import magic
import base64
import xlrd
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


def from_excel_ordinal(ordinal: float, _epoch0=datetime(1899, 12, 31)) -> datetime:
    if ordinal >= 60:
        ordinal -= 1  # Excel leap year bug, 1900 is not a leap year!
    return (_epoch0 + timedelta(days=ordinal)).replace(microsecond=0)


class StockPickingMoveImportWizard(models.TransientModel):
    _name = 'vtt.stock.picking.move.import.wz'
    _description = 'Stock Picking Move Import Wizard'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    # date = fields.Datetime('Date', default=fields.Datetime.now)

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    def submit_stock_picking_move_import_wz(self):
        mime = magic.from_buffer(base64.decodebytes(self.datas), mime=True)
        valid_mime = mime in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]

        if valid_mime:
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.datas))
            sheet = wb.sheets()[0]

            # DATA KEY
            kw_dict = dict.fromkeys([
                'STT', 'Mã Hàng', 'Tên Hàng', 'Số Lô', 'Hạn sử dụng',
                'SL Thùng', 'SL Lẻ', 'Tổng SL Lẻ', 'Ghi chú',
            ], False)
            for col in range(sheet.ncols):
                for k in kw_dict:
                    if sheet.cell(2, col).value.lower().strip() == k.lower().strip():
                        kw_dict[k] = col

            picking_name = sheet.cell(0, 1).value

            # Check all Valid column
            if all(kw_dict[k] is not False for k in kw_dict) and sheet.nrows > 3:
                # Check picking match
                if picking_name == self.picking_id.name:
                    # RAW Data
                    raw_data_key_map = {
                        'sequence': 'STT',
                        'product_default_code': 'Mã Hàng',
                        'product_name': 'Tên Hàng',
                        'lot_name': 'Số Lô',
                        'expiration_date': 'Hạn sử dụng',
                        'vtt_pack_qty': 'SL Thùng',
                        'vtt_surplus_qty': 'SL Lẻ',
                        'qty_done': 'Tổng SL Lẻ',
                        'note': 'Ghi chú',
                    }

                    raw_datas = [
                        {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                        for row in range(sheet.nrows) if row > 0]

                    # Check data
                    move_lines = self.picking_id.mapped('move_line_ids')
                    move_lot_names = {
                        (m.product_id.default_code, m.lot_id and m.lot_id.name or m.lot_name): m
                        for m in move_lines}
                    new_move_datas = [d for d in raw_datas if (d['product_default_code'], d['lot_name']) not in move_lot_names]
                    move_product_codes = self.picking_id.move_lines.mapped('product_id.default_code')

                    # LOOP
                    # Existed Lot
                    for dt in raw_datas:
                        if (dt['product_default_code'], dt['lot_name']) in move_lot_names:
                            ml = move_lot_names[(dt['product_default_code'], dt['lot_name'])]
                            if dt['qty_done'] <= 0 and (dt['vtt_pack_qty'] > 0 or dt['vtt_surplus_qty'] > 0):
                                dt_qty = dt['vtt_pack_qty'] * ml.product_id.packing_specification + dt['vtt_surplus_qty']
                            else:
                                dt_qty = dt['qty_done']
                            ml_vals = {
                                'sequence': dt['sequence'],
                                'qty_done': dt_qty,
                                'note': dt['note'],
                            }
                            if dt['expiration_date']:
                                if type(dt['expiration_date']) == str:
                                    r_date = datetime.strptime(dt['expiration_date'], '%d/%m/%Y')
                                elif type(dt['expiration_date']) in [int, float]:
                                    r_date = from_excel_ordinal(dt['expiration_date'])
                                else:
                                    r_date = False
                                if r_date:
                                    ml_vals['expiration_date'] = r_date
                            ml.write(ml_vals)
                    # New Lot
                    for dt in new_move_datas:
                        if dt['product_default_code'] in move_product_codes:
                            move = self.picking_id.move_lines.filtered(lambda m: m.product_id.default_code == dt['product_default_code'])
                            product_move_lines = self.env['stock.move.line'].search([('product_id', '=', move[0].product_id.id)])
                            product_lot_names = [m.lot_id and m.lot_id.name or m.lot_name for m in product_move_lines]
                            if dt['product_default_code'] not in product_lot_names:
                                if dt['qty_done'] <= 0 and (dt['vtt_pack_qty'] > 0 or dt['vtt_surplus_qty'] > 0):
                                    dt_qty = dt['vtt_pack_qty'] * move[0].product_id.packing_specification + dt[
                                        'vtt_surplus_qty']
                                else:
                                    dt_qty = dt['qty_done']
                                ml_vals = {
                                    'sequence': dt['sequence'],
                                    'move_id': move[0].id,
                                    'picking_id': self.picking_id.id,
                                    'location_id': move[0].location_id.id,
                                    'location_dest_id': move[0].location_dest_id.id,
                                    'product_id': move[0].product_id.id,
                                    'product_uom_id': move[0].product_uom.id,
                                    'lot_name': dt['lot_name'],
                                    'qty_done': dt_qty,
                                    'note': dt['note'],
                                }
                                if dt['expiration_date']:
                                    if type(dt['expiration_date']) == str:
                                        r_date = datetime.strptime(dt['expiration_date'], '%d/%m/%Y')
                                    elif type(dt['expiration_date']) in [int, float]:
                                        r_date = from_excel_ordinal(dt['expiration_date'])
                                    else:
                                        r_date = False
                                    if r_date:
                                        ml_vals['expiration_date'] = r_date
                                move[0].write({
                                    'move_line_ids': [(0, 0, ml_vals)]
                                })
                else:
                    raise ValidationError(_('Your Picking name does not match.'
                                            'Please checkout of it.'))
            else:
                raise ValidationError(_('Some problem occur from your product details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))