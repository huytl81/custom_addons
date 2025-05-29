# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportProjectTaskUser(models.Model):
    _inherit = 'report.project.task.user'

    missed_date = fields.Selection([
        ('01_inplan', 'In Plan'),
        ('02_missed', 'Missed Deadline'),
    ], 'Missed Date', readonly=True)

    # @api.depends('date_end', 'date_deadline')
    # def _compute_report_date_state(self):
    #     date = fields.Datetime.now()
    #     for t in self:
    #         de = t.date_end and t.date_end or date
    #         dd = t.date_deadline
    #         if dd:
    #             if de <= dd:
    #                 t.missed_date = '01_inplan'
    #             else:
    #                 t.missed_date = '02_missed'
    #         else:
    #             t.missed_date = '01_inplan'

    def _select(self):
        res = super(ReportProjectTaskUser, self)._select()
        res += """,
            CASE
             WHEN t.date_deadline IS NOT NULL AND t.date_end IS NULL AND t.date_deadline < NOW() THEN '02_missed' 
             WHEN t.date_deadline IS NOT NULL AND t.date_end IS NOT NULL AND t.date_deadline < t.date_end THEN '02_missed'
             ELSE '01_inplan'
            END as missed_date
        """
        return res

    def _group_by(self):
        return super()._group_by() + """,
                missed_date
        """