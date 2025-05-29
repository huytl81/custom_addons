# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import string
from io import BytesIO
from urllib.request import urlopen


class SaleOrder(models.AbstractModel):
    _name = 'report.vtt_sale_report_xlsx.sale_order_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, orders):
        # Generate by external code
        # localdict = {'self': workbook, 'user_obj': self.env.user, 'orders': orders}
        generate_code_obj = self.env['vtt.xlsx.report.code'].get_gen_by_code('VTT_SALE_ORDER')
        # if generate_code_obj:
        #     generate_code = generate_code_obj.generate_code
        #     try:
        #         exec(generate_code, localdict)
        #     except Exception as e:
        #         raise Warning('Python code is not able to run ! message : %s' % e)

        generate_code = generate_code_obj.generate_code
        for obj in orders:
            localdict = {
                'workbook': workbook,
                'obj': obj,
                'self': self,
                'orders': orders,
                'string': string,
                'BytesIO': BytesIO,
                'urlopen': urlopen,
            }
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
        #     sheet.set_column('A:A', 8, default_column)
        #     sheet.set_column('B:B', 50, default_column)
        #     sheet.set_column('C:C', 15, default_column)
        #     sheet.set_column('D:D', 15, default_column)
        #     sheet.set_column('E:E', 23, default_column)
        #     sheet.set_column('F:F', 23, default_column)
        #     sheet.set_column('G:G', 28, default_column)
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
        #         'bg_color': '#CCC0DA',
        #         'font_name': 'Arial',
        #     })
        #
        #     sheet.merge_range('A2:G2', _('QUOTATION DETAILS'), title)
        #     sheet.set_row(3, 20)
        #
        #     sheet.write('A4', 'STT', table_header)
        #     sheet.write('B4', 'PRODUCT NAME', table_header)
        #     sheet.write('C4', 'UOM', table_header)
        #     sheet.write('D4', 'QTY', table_header)
        #     sheet.write('E4', 'PRICE UNIT', table_header)
        #     sheet.write('F4', 'PRICE SUBTOTAL', table_header)
        #     sheet.write('G4', 'NOTE', table_header)
        #
        #     sheet.freeze_panes(4, 0)
        #
        #     start_row = 4
        #     order_lines = obj.order_line
        #     section_letters = [j for j in string.ascii_uppercase]
        #     stt = 1
        #     section_letter_index = 0
        #     for i in range(len(order_lines)):
        #
        #         string_left_fmt = workbook.add_format({
        #             'align': 'left',
        #             'valign': 'vcenter',
        #             'font_name': 'Arial',
        #             'text_wrap': True,
        #         })
        #         string_center_fmt = workbook.add_format({
        #             'align': 'center',
        #             'valign': 'vcenter',
        #             'font_name': 'Arial',
        #             'text_wrap': True,
        #         })
        #         number_center = workbook.add_format({
        #             'align': 'center',
        #             'valign': 'vcenter',
        #             'num_format': '#,###',
        #             'font_name': 'Arial',
        #         })
        #         number_right = workbook.add_format({
        #             'align': 'right',
        #             'valign': 'vcenter',
        #             'num_format': '#,###',
        #             'font_name': 'Arial',
        #         })
        #
        #         if order_lines[i].display_type != 'line_note':
        #
        #             if not order_lines[i].display_type:
        #                 sheet.write(start_row + i, 0, stt)
        #                 stt += 1
        #             elif order_lines[i].display_type == 'line_section':
        #                 number_center.set_bold()
        #                 number_right.set_bold()
        #                 string_center_fmt.set_bold()
        #                 string_left_fmt.set_bold()
        #                 sheet.write(start_row + i, 0, section_letters[section_letter_index], string_left_fmt)
        #                 section_letter_index += 1
        #                 stt = 1
        #
        #             sheet.write(start_row + i, 1, order_lines[i].name or '', string_left_fmt)
        #             sheet.write(start_row + i, 2, order_lines[i].product_uom.with_context(lang=self.env.user.lang).name or '', string_center_fmt)
        #             sheet.write(start_row + i, 3, order_lines[i].product_uom_qty or 0, number_center)
        #             sheet.write(start_row + i, 4, order_lines[i].display_price_unit or 0, number_right)
        #             sheet.write(start_row + i, 5, order_lines[i].price_subtotal or 0, number_right)
        #
        #         else:
        #             string_left_fmt.set_italic()
        #             note_range = f'A{start_row + i + 1}:G{start_row + i + 1}'
        #             sheet.merge_range(note_range, order_lines[i].name or '', string_left_fmt)
        #
        #     subtotal_row = start_row + len(order_lines)
        #     summary_string_center_fmt = workbook.add_format({
        #         'align': 'center',
        #         'valign': 'vcenter',
        #         'font_name': 'Arial',
        #         'text_wrap': True,
        #         'bold': True,
        #         'bg_color': '#00B050',
        #         'border': 1
        #     })
        #     summary_number_right = workbook.add_format({
        #         'align': 'right',
        #         'valign': 'vcenter',
        #         'num_format': '#,###',
        #         'font_name': 'Arial',
        #         'bold': True,
        #         'bg_color': '#00B050',
        #         'border': 1
        #     })
        #     # Subtotal
        #     subtotal_range = f'A{subtotal_row + 1}:E{subtotal_row + 1}'
        #     sheet.merge_range(subtotal_range, 'SUBTOTAL', summary_string_center_fmt)
        #     sheet.write(f'F{subtotal_row + 1}', obj.amount_untaxed, summary_number_right)
        #     sheet.write(f'G{subtotal_row + 1}', '', summary_string_center_fmt)
        #     # Tax
        #     tax_range = f'A{subtotal_row + 2}:E{subtotal_row + 2}'
        #     sheet.merge_range(tax_range, 'VAT', summary_string_center_fmt)
        #     sheet.write(f'F{subtotal_row + 2}', obj.amount_tax, summary_number_right)
        #     sheet.write(f'G{subtotal_row + 2}', '', summary_string_center_fmt)
        #     # Total
        #     total_range = f'A{subtotal_row + 3}:E{subtotal_row + 3}'
        #     sheet.merge_range(total_range, 'TOTAL', summary_string_center_fmt)
        #     sheet.write(f'F{subtotal_row + 3}', obj.amount_total, summary_number_right)
        #     sheet.write(f'G{subtotal_row + 3}', '', summary_string_center_fmt)