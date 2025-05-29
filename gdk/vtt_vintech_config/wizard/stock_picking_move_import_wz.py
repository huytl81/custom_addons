# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
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
    _inherit = 'vtt.stock.picking.move.import.wz'

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
                'STT', 'Mã Hàng', 'Tên Hàng', 'Đơn vị tính', 'Số lượng', 'Serial',
            ], False)
            for col in range(sheet.ncols):
                for k in kw_dict:
                    if sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        kw_dict[k] = col

            # Check all Valid column
            if all(kw_dict[k] is not False for k in kw_dict) and sheet.nrows > 3:
                # BASE Data
                base_uom = self.env.ref('uom.product_uom_unit')
                base_uom_categ = self.env.ref('uom.product_uom_categ_unit')

                # Default values
                default_product_values = {
                    'detailed_type': 'product',
                    'uom_id': base_uom.id,
                    'uom_po_id': base_uom.id,
                }

                # RAW Data
                raw_data_key_map = {
                    'sequence': 'STT',
                    'default_code': 'Mã Hàng',
                    'name': 'Tên Hàng',
                    'uom_name': 'Đơn vị tính',
                    'qty_done': 'Số lượng',
                    # 'serial': 'Serial',
                }

                tmp_target_move = False
                raw_datas_by_code = {}
                for row in range(sheet.nrows):
                    if row > 0:
                        dt = {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                        dt_serial = sheet.cell(row, kw_dict['Serial']).value.strip()
                        if dt_serial and dt['default_code']:
                            tmp_target_move = dt['default_code']
                            dt['serial'] = [dt_serial]
                            raw_datas_by_code[dt['default_code']] = dt
                        elif dt_serial and not dt['default_code']:
                            raw_datas_by_code[tmp_target_move]['serial'].append(dt_serial)

                # Fix null quantity
                lst_qty_keys = ['qty_done']
                for r in raw_datas_by_code:
                    for k in lst_qty_keys:
                        if k in raw_datas_by_code[r]:
                            if not str(raw_datas_by_code[r][k]).replace('.', '', 1).isdigit():
                                raw_datas_by_code[r][k] = 0.0

                # Type check for Product Default code
                raw_datas = {}
                for r in raw_datas_by_code:
                    rd_data = raw_datas_by_code[r]
                    if 'serial' not in rd_data:
                        rd_data['serial'] = []
                    if type(raw_datas_by_code[r]['default_code']) is float:
                        if raw_datas_by_code[r]['default_code'].is_integer():
                            rd_code = str(int(raw_datas_by_code[r]['default_code']))
                            rd_data['default_code'] = rd_code
                            raw_datas[rd_code] = rd_data
                        else:
                            raw_datas[r] = rd_data
                    else:
                        raw_datas[r] = rd_data

                # UOM
                raw_uoms = {
                    raw_datas[r]['uom_name']: False for r in raw_datas if raw_datas[r]['uom_name']
                }
                for uom in raw_uoms:
                    uom_id = self.env['uom.uom'].search([('name', '=', uom)], limit=1)
                    if not uom_id:
                        uom_id = self.env['uom.uom'].create({
                            'category_id': base_uom_categ.id,
                            'name': uom,
                            'uom_type': 'smaller',
                        })
                    raw_uoms[uom] = uom_id
                for r in raw_datas:
                    raw_datas[r]['uom_id'] = raw_uoms[raw_datas[r]['uom_name']]

                # PRODUCTS
                raw_products = {
                    r: {
                        'default_code': raw_datas[r]['default_code'],
                        'name': raw_datas[r]['name'],
                        'uom_id': raw_datas[r]['uom_id'],
                    } for r in raw_datas
                }
                for r_product in raw_products:
                    product_id = self.env['product.product'].search([('default_code', '=', r_product)], limit=1)
                    if not product_id:
                        product_vals = default_product_values.copy()
                        product_vals['name'] = raw_products[r_product]['name']
                        product_vals['default_code'] = r_product
                        if raw_products[r_product]['uom_id']:
                            product_vals['uom_id'] = raw_products[r_product]['uom_id'].id
                            product_vals['uom_po_id'] = raw_products[r_product]['uom_id'].id
                        product_tmpl = self.env['product.template'].create(product_vals)
                        product_id = self.env['product.product'].search(
                            [('product_tmpl_id', '=', product_tmpl.id)],
                            limit=1)
                    raw_products[r_product]['product_id'] = product_id
                for r in raw_datas:
                    raw_datas[r]['product_id'] = raw_products[r]['product_id']

                raw_all_products = self.env['product.product'].browse([raw_datas[r]['product_id'].id for r in raw_datas])

                # PICKING LOCATION
                if self.picking_id.picking_type_id.code in ['incoming']:
                    loc_id = self.picking_id.picking_type_id.default_location_src_id and \
                             self.picking_id.picking_type_id.default_location_src_id.id or \
                             self.env.ref('stock.stock_location_suppliers').id
                    loc_dest_id = self.picking_id.location_dest_id.id
                elif self.picking_id.picking_type_id.code in ['outgoing']:
                    loc_id = self.picking_id.location_id.id
                    loc_dest_id = self.picking_id.picking_type_id.default_location_dest_id and \
                                  self.picking_id.picking_type_id.default_location_dest_id.id or \
                                  self.env.ref('stock.stock_location_customers').id

                # Importing
                moves = self.picking_id.mapped('move_ids_without_package')
                move_existed = moves.filtered(lambda m: m.product_id in raw_all_products)
                move_existed_products = move_existed.mapped('product_id')

                moves_2_create = []
                for r in raw_datas:
                    if raw_datas[r]['product_id'] in move_existed_products:
                        dr_m = move_existed.filtered(lambda m: m.product_id == raw_datas[r]['product_id'])
                        dr_m.product_uom_qty = raw_datas[r]['qty_done']
                        # dr_m.quantity = dr['qty_done']
                        if raw_datas[r]['serial']:
                            sml_vals = [Command.create({
                                'picking_id': self.picking_id.id,
                                'product_id': dr_m.product_id.id,
                                'product_uom_id': dr_m.product_uom.id,
                                'quantity': 1.0,
                                'location_id': dr_m.location_id.id,
                                'location_dest_id': dr_m.location_dest_id.id,
                                'lot_name': sml_serial
                            }) for sml_serial in raw_datas[r]['serial']]
                            dr_m.write({
                                'move_line_ids': [Command.clear()] + sml_vals
                            })
                    else:
                        m_vals = {
                            'picking_id': self.picking_id.id,
                            'product_id': raw_datas[r]['product_id'].id,
                            'name': raw_datas[r]['name'],
                            'product_uom': raw_datas[r]['uom_id'].id,
                            'product_uom_qty': raw_datas[r]['qty_done'],
                            'location_id': loc_id,
                            'location_dest_id': loc_dest_id,
                        }
                        if raw_datas[r]['serial']:
                            sml_vals = [Command.create({
                                'picking_id': self.picking_id.id,
                                'product_id': raw_datas[r]['product_id'].id,
                                'product_uom_id': raw_datas[r]['uom_id'].id,
                                'quantity': 1.0,
                                'location_id': loc_id,
                                'location_dest_id': loc_dest_id,
                                'lot_name': sml_serial
                            }) for sml_serial in raw_datas[r]['serial']]
                            m_vals['move_line_ids'] = sml_vals
                        moves_2_create.append(m_vals)
                if moves_2_create:
                    self.picking_id.write({
                        'move_ids_without_package': [Command.create(mv) for mv in moves_2_create]
                    })

                # Updating Lot data
                self.picking_id.move_ids_without_package.move_line_ids.apply_lot_name()

            else:
                raise ValidationError(_('Some problem occur from your product details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))