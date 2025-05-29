# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one(store=True, readonly=False)
    tag_ids = fields.Many2many(tracking=True)