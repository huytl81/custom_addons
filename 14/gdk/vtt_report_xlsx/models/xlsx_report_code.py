# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VttXlsxReportCode(models.Model):
    _name = 'vtt.xlsx.report.code'
    _description = 'XLSX Generate code'
    _order = 'priority'

    name = fields.Char('Name')
    code = fields.Char('Code', required=True)
    priority = fields.Integer('Priority', default=10)
    generate_code = fields.Text('Generate Code')

    def get_gen_by_code(self, code):
        return self.search([('code', '=', code)], limit=1)