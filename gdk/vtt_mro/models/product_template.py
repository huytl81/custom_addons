# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    repair_order_ok = fields.Boolean('Repair Provision', default=True)