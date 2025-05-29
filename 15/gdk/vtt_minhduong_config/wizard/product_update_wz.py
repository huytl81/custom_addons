# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import magic
import base64
import xlrd
from odoo.exceptions import ValidationError


class ProductUpdateWizard(models.TransientModel):
    _name = 'vtt.product.update.wz'
    _description = 'Product Update Wizard'

    date = fields.Datetime('Date', default=fields.Datetime.now)

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    def submit_product_update_wz(self):
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
                'Mã SP', 'Tên SP', 'Quy cách thùng', 'Nhóm vật tư',
                'Trọng Lượng (kg)', 'Dài (cm)', 'Rộng (cm)', 'Cao (cm)',
                'Hạn Sử Dụng (ngày)', 'Giá bán', 'Giá mua', 'Đơn vị tính',
                'Mã vạch', 'Mã vạch thùng',
            ], False)
            for col in range(sheet.ncols):
                for k in kw_dict:
                    if sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        kw_dict[k] = col

            # Check all Valid column
            if all(kw_dict[k] is not False for k in kw_dict) and sheet.nrows > 1:
                # BASE Data
                base_uom = self.env.ref('uom.product_uom_unit')
                base_uom_categ = self.env.ref('uom.product_uom_categ_unit')
                base_product_categ = self.env.ref('product.product_category_all')
                base_package_type = self.env.ref('vtt_minhduong_config.vtt_data_stock_package_type_box')
                base_product_removal = self.env.ref('product_expiry.removal_fefo')

                # Default values
                default_product_values = {
                    'detailed_type': 'product',
                    'uom_id': base_uom.id,
                    'uom_po_id': base_uom.id,
                    'tracking': 'lot',
                    'use_expiration_date': True,
                    'vtt_show_expiration_percentage': True,
                    # 'vtt_use_production_date': True,
                    'categ_id': base_product_categ.id,
                }

                # RAW Data
                raw_data_key_map = {
                    'default_code': 'Mã SP',
                    'name': 'Tên SP',
                    'package_size': 'Quy cách thùng',
                    # 'category_name': 'Ngành hàng',
                    # 'categ2_name': 'Nhóm vật tư',
                    # 'categ3_name': 'Loại',
                    'category_name': 'Nhóm vật tư',
                    'weight': 'Trọng Lượng (kg)',
                    'vtt_length': 'Dài (cm)',
                    'vtt_width': 'Rộng (cm)',
                    'vtt_height': 'Cao (cm)',
                    'expiration_time': 'Hạn Sử Dụng (ngày)',
                    'list_price': 'Giá bán',
                    'standard_price': 'Giá mua',
                    'uom_name': 'Đơn vị tính',
                    'product_barcode': 'Mã vạch',
                    'pack_barcode': 'Mã vạch thùng',
                }

                raw_datas = [
                    {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                    for row in range(sheet.nrows) if row > 0]

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
                    uom_name = uom.strip()
                    uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
                    if not uom_id:
                        uom_id = self.env['uom.uom'].create({
                            'category_id': base_uom_categ.id,
                            'name': uom_name,
                            'uom_type': 'smaller',
                        })
                    raw_uoms[uom] = uom_id

                # CATEGORY
                raw_product_categs = {}
                for dr in raw_datas:
                    if dr['category_name']:
                        categ = ' / '.join(c.strip() for c in dr['category_name'].split('/'))
                        raw_product_categs[categ] = False
                # New Resolve
                for dr_name in raw_product_categs:
                    dr_name_split = dr_name.split('/')
                    if len(dr_name_split) == 1:
                        categ = dr_name_split[0].strip()
                        categ_id = self.env['product.category'].search([('complete_name', '=', categ)], limit=1)
                        if not categ_id:
                            categ_id = self.env['product.category'].create({
                                'name': categ,
                                'removal_strategy_id': base_product_removal.id,
                                # 'parent_id': base_product_categ.id,
                            })
                        raw_product_categs[categ] = categ_id
                    else:
                        for i_index in range(len(dr_name_split)):
                            dr_name_range = dr_name_split[:i_index+1]
                            categ = ' / '.join([c.strip() for c in dr_name_range])
                            if raw_product_categs.get(categ, False):
                                categ_id = raw_product_categs[categ]
                            else:
                                categ_id = self.env['product.category'].search([('complete_name', '=', categ)], limit=1)
                                if not categ_id:
                                    categ_vals = {
                                        'name': dr_name_split[i_index].strip(),
                                        'removal_strategy_id': base_product_removal.id,
                                    }
                                    if i_index > 0:
                                        parent_categ = ' / '.join([pc.strip() for pc in dr_name_range[:i_index]])
                                        categ_vals['parent_id'] = raw_product_categs[parent_categ].id
                                    categ_id = self.env['product.category'].create(categ_vals)
                            raw_product_categs[categ] = categ_id

                # for categ in raw_product_categs:
                #     categ_id = self.env['product.category'].search([('complete_name', '=', categ)], limit=1)
                #     if not categ_id:
                #         categ_id = self.env['product.category'].create({
                #             'name': categ,
                #             'removal_strategy_id': base_product_removal.id,
                #             # 'parent_id': base_product_categ.id
                #         })
                #     raw_product_categs[categ] = categ_id
                #
                # raw_product_categs2 = {
                #     (dr['category_name'], dr['categ2_name']): False
                #     for dr in raw_datas if dr['category_name'] and dr['categ2_name']
                # }
                # for categ in raw_product_categs2:
                #     categ_parent_id = raw_product_categs[categ[0]]
                #     categ_id = self.env['product.category'].search([
                #         ('name', '=', categ),
                #         ('parent_id', '=', categ_parent_id.id)
                #     ], limit=1)
                #     if not categ_id:
                #         categ_id = self.env['product.category'].create({
                #             'name': categ,
                #             'removal_strategy_id': base_product_removal.id,
                #             'parent_id': categ_parent_id.id
                #         })
                #     raw_product_categs[categ] = categ_id
                #
                # raw_product_categs3 = {
                #     (dr['category_name'], dr['categ2_name'], dr['categ3_name']): False
                #     for dr in raw_datas if dr['category_name'] and dr['categ2_name'] and dr['categ3_name']
                # }
                # for categ in raw_product_categs3:
                #     categ_parent_id = raw_product_categs2[(categ[0], categ[1])]
                #     categ_id = self.env['product.category'].search([
                #         ('name', '=', categ),
                #         ('parent_id', '=', categ_parent_id.id)
                #     ], limit=1)
                #     if not categ_id:
                #         categ_id = self.env['product.category'].create({
                #             'name': categ,
                #             'removal_strategy_id': base_product_removal.id,
                #             'parent_id': categ_parent_id.id
                #         })
                #     raw_product_categs[categ] = categ_id

                # Loop Product Data
                for r_data in raw_datas:
                    if r_data['default_code']:
                        product_id = self.env['product.product'].search([('default_code', '=', r_data['default_code'])], limit=1)
                        if not product_id and r_data['name']:
                            product_vals = default_product_values.copy()
                            product_vals.update({
                                'name': r_data['name'],
                                'default_code': r_data['default_code'],
                                'list_price': r_data['list_price'],
                                'standard_price': r_data['standard_price'],
                                'expiration_time': r_data['expiration_time'],
                                'weight': r_data['weight'],
                                'vtt_length': r_data['vtt_length'],
                                'vtt_width': r_data['vtt_width'],
                                'vtt_height': r_data['vtt_height'],
                                'product_barcode': r_data['product_barcode'],
                                'pack_barcode': r_data['pack_barcode'],
                            })

                            if r_data['uom_name']:
                                product_vals['uom_id'] = raw_uoms[r_data['uom_name']].id
                                product_vals['uom_po_id'] = raw_uoms[r_data['uom_name']].id

                            # if r_data['category_name'] and r_data['categ2_name'] and r_data['categ3_name']:
                            #     product_id.categ_id = raw_product_categs3[
                            #         (r_data['category_name'], r_data['categ2_name'], r_data['categ3_name'])].id
                            # elif r_data['category_name'] and r_data['categ2_name']:
                            #     product_id.categ_id = raw_product_categs2[
                            #         (r_data['category_name'], r_data['categ2_name'])].id
                            # elif r_data['category_name']:
                            #     product_id.categ_id = raw_product_categs[r_data['category_name']].id

                            # New Product Category Resolve
                            if r_data['category_name']:
                                categ = ' / '.join(c.strip() for c in r_data['category_name'].split('/'))
                                product_id.categ_id = raw_product_categs[categ].id

                            if r_data['package_size']:
                                product_vals['packaging_ids'] = [(0, 0, {
                                    'name': 'Thùng',
                                    'package_type_id': base_package_type.id,
                                    'qty': r_data['package_size'],
                                })]
                                product_vals['packing_specification'] = r_data['package_size']
                            product_tmpl = self.env['product.template'].create(product_vals)
                            product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl.id)],
                                                                            limit=1)
                        elif product_id:
                            product_id.list_price = r_data['list_price']
                            product_id.standard_price = r_data['standard_price']
                            product_id.expiration_time = r_data['expiration_time']
                            product_id.weight = r_data['weight']
                            product_id.vtt_length = r_data['vtt_length']
                            product_id.vtt_width = r_data['vtt_width']
                            product_id.vtt_height = r_data['vtt_height']
                            # Add barcode
                            product_id.product_barcode = r_data['product_barcode']
                            product_id.pack_barcode = r_data['pack_barcode']

                            # if r_data['category_name'] and r_data['categ2_name'] and r_data['categ3_name']:
                            #     product_id.categ_id = raw_product_categs3[(r_data['category_name'], r_data['categ2_name'], r_data['categ3_name'])].id
                            # elif r_data['category_name'] and r_data['categ2_name']:
                            #     product_id.categ_id = raw_product_categs2[(r_data['category_name'], r_data['categ2_name'])].id
                            # elif r_data['category_name']:
                            #     product_id.categ_id = raw_product_categs[r_data['category_name']].id

                            # New Product Category Resolve
                            if r_data['category_name']:
                                categ = ' / '.join(c.strip() for c in r_data['category_name'].split('/'))
                                product_id.categ_id = raw_product_categs[categ].id

                            if r_data['package_size']:
                                product_id.packing_specification = r_data['package_size']
                                product_package = product_id.packaging_ids.filtered(lambda pp: pp.qty == r_data['package_size'])
                                if not product_package:
                                    product_id.packaging_ids = [(0, 0, {
                                        'name': 'Thùng',
                                        'package_type_id': base_package_type.id,
                                        'qty': r_data['package_size'],
                                    })]
            else:
                raise ValidationError(_('Some problem occur from your product details.'
                                        'Please checkout of it.'))
        else:
            raise ValidationError(_('Your Excel template does not meet the valid template.'))