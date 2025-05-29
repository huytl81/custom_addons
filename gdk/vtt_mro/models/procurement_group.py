# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    repair_order_id = fields.Many2one('vtt.repair.order', 'Repair Order')