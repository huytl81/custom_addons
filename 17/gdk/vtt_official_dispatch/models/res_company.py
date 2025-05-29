# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class ResCompany(models.Model):
    _inherit = "res.company"

    # vtt_company_code = fields.Char('Company Code',default='COM')
    edit_department_id = fields.Many2one('hr.department',string="Document edit department")
