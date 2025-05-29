# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import xlrd
import base64


class VttModelCustomImport(models.Model):
    _name = 'vtt.model.custom.import'
    _description = 'Model Custom Import'

    name = fields.Char('Name')
    datas = fields.Binary('Datas')
    res_model = fields.Char('Destination Model', required=True)
    res_field_name = fields.Char('Field Name', required=True)
    ids_column = fields.Integer('IDs Column', required=True, default=0)
    data_column = fields.Integer('Data Column', required=True, default=1)
    null_overwrite = fields.Boolean('Null Overwrite', default=True)

    def do_import_custom_field(self):
        MODEL = self.env[self.res_model]
        data_col = self.data_column
        ids_col = self.ids_column
        null_overwrite = self.null_overwrite
        if self.res_field_name in MODEL._fields:
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.datas))
            sheet = wb.sheets()[0]
            for row in range(sheet.nrows):
                if row > 0:
                    rec = MODEL.browse(int(sheet.cell(row, ids_col).value))
                    vals = {}
                    if sheet.cell(row, data_col).value or null_overwrite:
                        vals.update({self.res_field_name: sheet.cell(row, data_col).value})
                    if vals:
                        rec.write(vals)
