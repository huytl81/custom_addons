# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command, _
from odoo.exceptions import ValidationError
import magic
import base64
import xlrd


def _get_item_import_data(item, data):
    item_val = {
        'name': item['name'],
        'sequence': item['sequence'],
        'level': item['level'],
        'product_uom_qty': item['product_uom_qty'],
        'analytic_template_id': item['analytic_template_id'],
    }
    if item['children']:
        item_childs = [n for n in data if n['group'] in item['children']]
        childs = [_get_item_import_data(i, data) for i in item_childs]
    else:
        childs = []

    item_val['child_ids'] = childs

    if item.get('product_id', False) and not childs:
        item_val['type'] = 'item'
        item_val['product_id'] = item['product_id'].id
        if item.get('product_uom'):
            item_val['product_uom'] = item['product_uom'].id
    else:
        item_val['type'] = 'group'
        item_val['product_uom_qty'] = 0.0

    return Command.create(item_val)


class BudgetCustomImportWizard(models.TransientModel):
    _name = 'vtt.budget.custom.import.wz'
    _description = 'Budget Custom Import Wizard'

    budget_template_id = fields.Many2one('vtt.analytic.budget.template', 'Budget Template')

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    def budget_custom_import(self):
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
                'STT', 'Level', 'Tên hạng mục', 'Tên vật tư', 'Mã vật tư', 'Đơn vị tính', 'Số lượng',
            ], False)
            for col in range(sheet.ncols):
                for k in kw_dict:
                    if sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        kw_dict[k] = col

            # Check all Valid column
            if all(kw_dict[k] is not False for k in kw_dict) and sheet.nrows > 1:
                base_uom = self.env.ref('uom.product_uom_unit')
                base_uom_categ = self.env.ref('uom.product_uom_categ_unit')

                # Default values
                default_product_values = {
                    'detailed_type': 'product',
                    # 'detailed_type': 'consu',
                    'uom_id': base_uom.id,
                    'uom_po_id': base_uom.id,
                }

                # RAW Data
                raw_data_key_map = {
                    'sequence': 'STT',
                    'level': 'Level',
                    'name': 'Tên hạng mục',
                    'product_name': 'Tên vật tư',
                    'default_code': 'Mã vật tư',
                    'uom_name': 'Đơn vị tính',
                    'product_uom_qty': 'Số lượng',
                }
                raw_datas = [
                    {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                    for row in range(sheet.nrows) if row > 0]

                # Fix null quantity
                lst_qty_keys = ['product_uom_qty', ]
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

                # PRODUCTS
                raw_products = {
                    dr['default_code']: {
                        'default_code': dr['default_code'],
                        'name': dr['product_name'],
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
                        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl.id)],
                                                                        limit=1)
                    raw_products[r_product]['product_id'] = product_id

                # Raw data add relation fields
                for r in raw_datas:
                    r['analytic_template_id'] = self.budget_template_id.id
                    if r['default_code']:
                        r['product_id'] = raw_products[r['default_code']]['product_id']
                    if r['uom_name']:
                        r['product_uom'] = raw_uoms[r['uom_name']]

                # Add Grouping sequence
                raw_datas.sort(key=lambda x: (x['sequence'], x['level']))
                gr_count = 0
                for r in raw_datas:
                    r['group'] = gr_count
                    r['children'] = []
                    gr_count += 1
                # Append raw children
                for i_index in range(len(raw_datas)):
                    for r in raw_datas[i_index + 1:]:
                        if r['level'] == raw_datas[i_index]['level'] + 1:
                            raw_datas[i_index]['children'].append(r['group'])
                        elif r['level'] == raw_datas[i_index]['level']:
                            break

                # Prepare import data
                lvl_min = min([r['level'] for r in raw_datas])
                item_top_lvl = [r for r in raw_datas if r['level'] == lvl_min]
                datas_import = [_get_item_import_data(r, raw_datas) for r in item_top_lvl]

                if datas_import:
                    self.budget_template_id.write({'line_ids': datas_import})
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))

