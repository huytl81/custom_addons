# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from fuzzywuzzy import fuzz, process
import json
import itertools
from . import analysis_tools
from operator import itemgetter


class ThreatComparison(models.Model):
    _name = 'threat.comparison'
    _description = 'Threat Comparison'
    _inherit = ['threat.sync.mixin']

    malware_id = fields.Many2one('threat.malware', 'Source to Compare')
    investigate_id = fields.Many2one('investigate.investigate', 'Investigate to Compare')
    type = fields.Selection([
        ('threat.malware', 'Malware'),
        ('investigate.investigate', 'Investigate'),
    ], 'Type', default='threat.malware', required=True)

    user_id = fields.Many2one('res.users', 'Reporter', default=lambda self: self.env.user.id)

    dt = fields.Datetime('Date', default=fields.Datetime.now)

    compare_template_id = fields.Many2one('threat.comparison.template', 'Template')

    compare_field_ids = fields.One2many('threat.comparison.field', 'compare_id', 'Fields to Compare')

    compare_report_ids = fields.One2many('threat.comparison.report', 'compare_id', 'Reports')
    correct_id = fields.Many2one('threat.malware', 'Correct Similar')
    investigate_correct_id = fields.Many2one('investigate.investigate', 'Similar Investigate')

    report_count = fields.Integer('Report Count', compute='_compute_report_count')

    def _compute_report_count(self):
        for compare in self:
            compare.report_count = len(compare.compare_report_ids)

    ss_code = fields.Char('Secret Sequence', copy=False)

    @api.depends('dt')
    def name_get(self):
        result = []
        for c in self:
            name = f'{c.dt.date()}'
            if c.compare_template_id:
                name = c.compare_template_id.name + ' ' + name
            result.append((c.id, name))
        return result

    @api.onchange('compare_template_id')
    def onchange_compare_template(self):
        if self.compare_template_id and self.compare_template_id.compare_field_ids:
            lines = [(5, 0, 0)]
            lines += [(0, 0, {
                'compare_id': self.id,
                'field_id': f.field_id.id,
                'description': f.description
            }) for f in self.compare_template_id.compare_field_ids]
            self.update({
                'compare_field_ids': lines
            })

    @api.onchange('type')
    def onchange_type(self):
        if self.type != self.compare_template_id.type:
            self.compare_template_id = False

        lines = self.compare_field_ids.filtered(lambda f: f.field_id.model_id.model != self.type)
        data_lines = [(3, l.id) for l in lines]
        self.compare_field_ids = data_lines

    def get_similar(self):
        self.compare_report_ids = [(5, 0, 0)]
        self.correct_id = False
        results = self._calculate_similar()
        results.sort(key=lambda r: r['avg_compare_score'], reverse=True)
        count = 6 if len(results) >= 6 else len(results)
        h_results = results[:count]
        if self.type == 'threat.malware':
            vals_lst = [{
                'compare_id': self.id,
                'malware_id': res['id'],
                'score': res['avg_compare_score'],
                'compare_detail': json.dumps([{'field': n, 'score': res[n]} for n in res if n not in ['id', 'avg_compare_score']], indent=2)
            } for res in h_results]
        else:
            vals_lst = [{
                'compare_id': self.id,
                'investigate_id': res['id'],
                'score': res['avg_compare_score'],
                'compare_detail': json.dumps(
                    [{'field': n, 'score': res[n]} for n in res if n not in ['id', 'avg_compare_score']], indent=2)
            } for res in h_results]
        if vals_lst:
            self.env['threat.comparison.report'].create(vals_lst)

    def _calculate_similar(self):
        lst_fields = [f.field_id.name for f in self.compare_field_ids]
        MODELS = self.env[self.type]
        if self.type == 'threat.malware':
            domain = [('id', '!=', self.malware_id.id)]
            src_rd = self.malware_id
        else:
            domain = [('id', '!=', self.investigate_id.id)]
            src_rd = self.investigate_id
        compare_rds = MODELS.search(domain)
        compare_rds.sorted('id')
        lst_results = [{'id': r.id} for r in compare_rds]

        count = len(lst_results)
        avg_factor = len(lst_fields)

        for n in lst_fields:
            if self.type == 'threat.malware' and n == 'malware_activity_detail':
                qts_lst = [(n.activity_id.name, n.name) for n in src_rd.malware_activity_detail]
                qts_lst.sort(key=lambda q: q[0])
                qt = str([(key, list(map(itemgetter(1), group))) for key, group in itertools.groupby(qts_lst, lambda x: x[0])])
                lst_choices = []
                for r in compare_rds:
                    r_asw_lst = [(n.activity_id.name, n.name) for n in r.malware_activity_detail]
                    r_asw_lst.sort(key=lambda q: q[0])
                    r_asw = [(key, list(map(itemgetter(1), group))) for key, group in itertools.groupby(r_asw_lst, lambda x: x[0])]
                    lst_choices.append(str(r_asw))
            elif self.type == 'investigate.investigate' and n == 'threat_activity_ids':
                qts_lst = [(n.activity_id.name, n.name) for n in src_rd.threat_activity_ids]
                qts_lst.sort(key=lambda q: q[0])
                qt = str([(key, list(map(itemgetter(1), group))) for key, group in
                      itertools.groupby(qts_lst, lambda x: x[0])])
                lst_choices = []
                for r in compare_rds:
                    r_asw_lst = [(n.activity_id.name, n.name) for n in r.threat_activity_ids]
                    r_asw_lst.sort(key=lambda q: q[0])
                    r_asw = [(key, list(map(itemgetter(1), group))) for key, group in
                             itertools.groupby(r_asw_lst, lambda x: x[0])]
                    lst_choices.append(str(r_asw))
            else:
                if self.type == 'threat.malware' and n == 'malware_type_id':
                    qt = src_rd[n].id
                    lst_choices = [r[n].id for r in compare_rds]
                else:
                    qt = src_rd[n] or ''
                    lst_choices = [r[n] or '' for r in compare_rds]

            if self.type == 'threat.malware' and n == 'malware_type_id':
                check_lst = list(map(lambda x: x == qt, lst_choices))
                scores = list(map(lambda x: x * 100, check_lst))
                n_answer = [{n: i} for i in scores]
            else:
                scores = list(process.extractWithoutOrder(qt, lst_choices))
                n_answer = [{n: i[1]} for i in scores]
            lst_results = [{**lst_results[i], **n_answer[i]} for i in range(count)]

        for i in range(count):
            total_score = sum([lst_results[i][f] for f in lst_results[i] if f != 'id'])
            avg_score = float(total_score) / float(avg_factor)
            lst_results[i].update({'avg_compare_score': avg_score})

        return lst_results
