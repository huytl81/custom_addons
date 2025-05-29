# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ViewCustom(models.Model):
    _inherit = 'ir.ui.view.custom'

    vtt_department_id = fields.Many2one('hr.department', 'Department')