# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from . import analysis_tools


class ThreatComparisonReport(models.Model):
    _name = 'threat.comparison.report'
    _description = 'Comparison Report'
    _inherit = ['threat.sync.mixin']

    compare_id = fields.Many2one('threat.comparison', 'Comparison')
    user_id = fields.Many2one(related='compare_id.user_id')
    compare_correct_id = fields.Many2one(related='compare_id.correct_id')
    compare_investigate_correct_id = fields.Many2one(related='compare_id.investigate_correct_id')
    type = fields.Selection(related='compare_id.type')

    malware_id = fields.Many2one('threat.malware', 'Malware')
    investigate_id = fields.Many2one('investigate.investigate', 'Investigate')

    score = fields.Float('Similar Percentage', digits='Compare Score')

    state = fields.Selection([
        ('consider', 'Consider'),
        ('correct', 'Correct'),
    ], 'State', default='consider', required=True)

    compare_detail = fields.Text('Compare Detail')

    ss_code = fields.Char('Secret Sequence', copy=False)

    def do_correct(self):
        reports = self.compare_id.mapped('compare_report_ids').filtered(lambda r: r.id != self.id)
        reports.do_consider()
        if self.type == 'threat.malware':
            self.compare_id.correct_id = self.malware_id.id
        else:
            self.compare_id.investigate_correct_id = self.investigate_id.id
        self.write({
            'state': 'correct'
        })

    def do_consider(self):
        if self.compare_id.type == 'threat.malware':
            if self.compare_id.correct_id in self.malware_id:
                self.compare_id.correct_id = False
        else:
            if self.compare_id.investigate_correct_id in self.investigate_id:
                self.compare_id.investigate_correct_id = False

        return self.write({
            'state': 'consider'
        })
