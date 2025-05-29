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
                'STT', 'Mã Hàng', 'Tên Hàng', 'Đơn vị tính', 'Số lượng',
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
                }

                raw_datas = [
                    {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                    for row in range(sheet.nrows) if row > 0]

                # Fix null quantity
                lst_qty_keys = ['qty_done']
                for r in raw_datas:
                    for k in lst_qty_keys:
                        if k in r:
                            if not str(r[k]).replace('.', '', 1).isdigit():
                                r[k] = 0.0

                # Type check for Product Default code
                for rd in raw_datas:
                    if type(rd['default_code']) is float:
                        if rd['default_code'].is_integer():
                            # rd_tmp = int(rd['default_code'])
                            rd['default_code'] = str(int(rd['default_code']))

                # UOM
                raw_uoms = {
                    dr['uom_name']: False for dr in raw_datas if dr['uom_name']
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
                    r['uom_id'] = raw_uoms[r['uom_name']]

                # PRODUCTS
                raw_products = {
                    dr['default_code']: {
                        'default_code': dr['default_code'],
                        'name': dr['name'],
                        'uom_name': dr['uom_name'],
                    } for dr in raw_datas
                }
                for r_product in raw_products:
                    product_id = self.env['product.product'].search([('default_code', '=', r_product)], limit=1)
                    if not product_id:
                        product_vals = default_product_values.copy()
                        product_vals['name'] = raw_products[r_product]['name']
                        product_vals['default_code'] = r_product
                        if raw_products[r_product]['uom_name']:
                            product_vals['uom_id'] = raw_uoms[raw_products[r_product]['uom_name']].id
                            product_vals['uom_po_id'] = raw_uoms[raw_products[r_product]['uom_name']].id
                        product_tmpl = self.env['product.template'].create(product_vals)
                        product_id = self.env['product.product'].search(
                            [('product_tmpl_id', '=', product_tmpl.id)],
                            limit=1)
                    raw_products[r_product]['product_id'] = product_id
                for r in raw_datas:
                    r['product_id'] = raw_products[r['default_code']]['product_id']

                raw_all_products = self.env['product.product'].browse([r['product_id'].id for r in raw_datas])

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
                for dr in raw_datas:
                    if dr['product_id'] in move_existed_products:
                        dr_m = move_existed.filtered(lambda m: m.product_id == dr['product_id'])
                        dr_m.product_uom_qty = dr['qty_done']
                        # dr_m.quantity = dr['qty_done']
                    else:
                        m_vals = {
                            'picking_id': self.picking_id.id,
                            'product_id': dr['product_id'].id,
                            'name': dr['name'],
                            'product_uom': dr['uom_id'].id,
                            'product_uom_qty': dr['qty_done'],
                            'location_id': loc_id,
                            'location_dest_id': loc_dest_id,
                        }
                        moves_2_create.append(m_vals)
                if moves_2_create:
                    self.picking_id.write({
                        'move_ids_without_package': [Command.create(mv) for mv in moves_2_create]
                    })

            else:
                raise ValidationError(_('Some problem occur from your product details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))