# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AnalyticAccountLine(models.Model):
    _inherit = 'account.analytic.line'

    vtt_budget_line_id = fields.Many2one('vtt.analytic.budget.line', 'Budget Item')