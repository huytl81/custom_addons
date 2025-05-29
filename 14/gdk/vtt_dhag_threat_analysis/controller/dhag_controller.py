# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import requests, json, base64
from datetime import datetime

model_lst = [
    # ('users', 'res.users'),
    ('location', 'investigate.location', 'ss.investigate.location', 2),
    ('campaign', 'investigate.campaign', 'ss.investigate.campaign', 3),
    ('investigate', 'investigate.investigate', 'ss.investigate.investigate', 4),
    ('malware type', 'threat.malware.type', 'ss.threat.malware.type', 5),
    ('malware', 'threat.malware', 'ss.threat.malware', 6),
    ('investigate.malware', 'investigate.malware', 'ss.investigate.malware', 7),
    ('subject', 'threat.malware.subject', 'ss.threat.malware.subject', 8),
    ('activity type', 'threat.malware.activity.type', 'ss.threat.malware.activity.type', 9),
    ('activity', 'threat.malware.activity', 'ss.threat.malware.activity', 10),
    ('activity detail', 'threat.malware.activity.detail', 'ss.threat.malware.activity.detail', 11),
    ('compare template', 'threat.comparison.template', 'ss.threat.comparison.template', 12),
    ('compare template field', 'threat.comparison.template.field', 'ss.threat.comparison.template.field', 13),
    ('compare', 'threat.comparison', 'ss.threat.comparison', 14),
    ('compare field', 'threat.comparison.field', 'ss.threat.comparison.field', 15),
    ('compare report', 'threat.comparison.report', 'ss.threat.comparison.report', 16),
]


class ThreatSync(http.Controller):

    @http.route('/dhag/api/upload/', type='json', auth='user', methods=['POST'])
    def threat_upload(self, **kwargs):
        args = {
            'success': False,
            'message': 'Failed',
            'dt_submission': False,
            'results': []
        }

        # if request.jsonrequest:
            # res = request.jsonrequest
        # print(kwargs)
        # params = kwargs.get('params')
        params = kwargs
        if params:
            lst_models = [m for m in params]
            lst_models.sort(key=lambda m: params[m]['priority'])
            for m in lst_models:
                request.env[m].extract_sync_data(params[m])
            args.update({
                'success': True,
                'message': 'Success',
                'dt_submission': datetime.now(),
            })
        return args

    @http.route('/dhag/api/download/', type='json', auth='user', methods=['POST'])
    def threat_download(self, **kwargs):
        args = {
            'success': False,
            'message': 'Failed',
            'dt_submission': False,
            'results': []
        }

        params = kwargs
        if params:
            dt = params.get('dt')
            data = {
                'res.users': request.env['res.users']._prepare_push_data(),
                'investigate.department.suggest': request.env['investigate.department.suggest']._prepare_push_data()
            }
            data.update({n[1]: request.env[n[1]]._prepare_push_data(dt, False, type='pull') for n in model_lst})
            data['res.users']['priority'] = 1
            data['investigate.department.suggest']['priority'] = 1
            for n in model_lst:
                data[n[1]]['priority'] = n[3]

            args.update({
                'success': True,
                'message': 'Success',
                'dt_submission': datetime.now(),
                'results': data
            })
        return args

    @http.route('/dhag/api/get_sequence_current/', type='http', auth='user', methods=['GET'])
    def get_sequence_current(self):
        code_lst = [n[2] for n in model_lst]

        sequences = request.env['ir.sequence'].search([('code', 'in', code_lst)])

        return json.dumps({s.code: s.number_next_actual - 1 for s in sequences})

    @http.route('/dhag/api/update_sequence_current/', type='json', auth='user', methods=['POST'])
    def update_sequence_current(self, **kwargs):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        # if request.jsonrequest:
        #     data = request.jsonrequest
        params = kwargs
        if params:
            code_lst = [c for c in params]
            sequences = request.env['ir.sequence'].search([('code', 'in', code_lst)])
            for s in sequences:
                if params.get(s.code):
                    s.sudo().write({
                        'number_next_actual': params[s.code] + 1
                    })

            args.update({
                'success': True,
                'message': 'Success',
            })
        return args