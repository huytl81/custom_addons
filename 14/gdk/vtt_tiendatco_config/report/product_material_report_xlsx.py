# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductMaterialTemplateReportXLSX(models.AbstractModel):
    _name = 'report.vtt_tiendat_config.product_material_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, orders):
        generate_code_obj = self.env['vtt.xlsx.report.code'].get_gen_by_code('VTT_PRODUCT_MATERIAL_TEMPLATE')

        generate_code = generate_code_obj.generate_code
        for obj in orders:
            localdict = {'workbook': workbook, 'obj': obj, 'self': self, 'orders': orders}
            try:
                exec(generate_code, localdict)
            except Exception as e:
                raise Warning('Python code is not able to run ! message : %s' % e)

        # Default Code
        # for obj in orders:
        #     report_name = obj.name
        #     # One sheet by orders
        #     sheet = workbook.add_worksheet(report_name[:31])
        #
        #     default_column = workbook.add_format({
        #         'align': 'center',
        #         'valign': 'vcenter',
        #         'text_wrap': True,
        #         'font_name': 'Arial',
        #         'num_format': '#,###',
        #     })
        #
        #     # Columns define
        #     # sheet.set_column('A:A', 8, default_column)
        #     sheet.set_column('A:A', 15, default_column)
        #     sheet.set_column('B:B', 35, default_column)
        #     sheet.set_column('C:C', 15, default_column)
        #     sheet.set_column('D:D', 15, default_column)
        #     sheet.set_column('E:E', 15, default_column)
        #
        #     title = workbook.add_format({
        #         'align': 'center',
        #         'valign': 'vcenter',
        #         'bold': True,
        #         'font_size': 25,
        #         'bg_color': '#92D050',
        #         'font_name': 'Arial',
        #     })
        #
        #     table_header = workbook.add_format({
        #         'align': 'center',
        #         'valign': 'vcenter',
        #         'bold': True,
        #         'font_size': 13,
        #         # 'bg_color': '#CCC0DA',
        #         'font_name': 'Arial',
        #     })
        #
        #     # sheet.merge_range('A2:G2', _('QUOTATION DETAILS'), title)
        #     # sheet.set_row(3, 20)
        #
        #     sheet.write('A1', 'Product Code', table_header)
        #     sheet.write('B1', 'Product Name', table_header)
        #     sheet.write('C1', 'UoM', table_header)
        #     sheet.write('D1', 'UoM Code', table_header)
        #     sheet.write('E1', 'Quantity', table_header)
        #     # sheet.write('F1', 'PRICE UNIT', table_header)
        #     # sheet.write('G1', 'PRICE SUBTOTAL', table_header)
        #     # sheet.write('H1', 'NOTE', table_header)
        #
        #     sheet.freeze_panes(1, 0)
        #
        #     start_row = 1
        #     string_left_fmt = workbook.add_format({
        #         'align': 'left',
        #         'valign': 'vcenter',
        #         'font_name': 'Arial',
        #         'text_wrap': True,
        #     })
        #     number_right = workbook.add_format({
        #         'align': 'right',
        #         'valign': 'vcenter',
        #         'num_format': '#,###',
        #         'font_name': 'Arial',
        #     })
        #     lines = obj.material_product_ids
        #     for i in range(len(lines)):
        #         sheet.write(start_row + i, 0, lines[i].default_code or '', string_left_fmt)
        #         sheet.write(start_row + i, 1, lines[i].name or '', string_left_fmt)
        #         sheet.write(start_row + i, 2, lines[i].uom_id.name or '', string_left_fmt)
        #         sheet.write(start_row + i, 3, lines[i].uom_id.code or '', string_left_fmt)
        #         sheet.write(start_row + i, 4, 1.0, number_right)
        #         qty_row = f'E{start_row + i}'
        #         price_row = f'F{start_row + i}'
        #         sheet.write(start_row + i, 5, lines[i].lst_price or 0.0, number_right)
        #         subtotal_row = f'G{start_row + i}'
        #         sheet.write_formula(subtotal_row, f'={price_row}*{qty_row}')