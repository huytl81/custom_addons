# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    project_template_id = fields.Many2one('vtt.project.template', 'Project Template')