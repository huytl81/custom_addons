# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import requests
import json
from odoo.exceptions import UserError
import base64

model_lst = [
    # ('users', 'res.users'),
    ('location', 'investigate.location', 'ss.investigate.location', 2),
    ('campaign', 'investigate.campaign', 'ss.investigate.campaign', 3),
    ('investigate', 'investigate.investigate', 'ss.investigate.investigate', 4),
    ('malware type', 'threat.malware.type', 'ss.threat.malware.type', 5),
    ('malware', 'threat.malware', 'ss.threat.malware', 6),
    ('subject', 'threat.malware.subject', 'ss.threat.malware.subject', 7),
    ('malware', 'investigate.malware', 'ss.investigate.malware', 8),
    ('activity type', 'threat.malware.activity.type', 'ss.threat.malware.activity.type', 9),
    ('activity', 'threat.malware.activity', 'ss.threat.malware.activity', 10),
    ('activity detail', 'threat.malware.activity.detail', 'ss.threat.malware.activity.detail', 11),
    ('compare template', 'threat.comparison.template', 'ss.threat.comparison.template', 12),
    ('compare template field', 'threat.comparison.template.field', 'ss.threat.comparison.template.field', 13),
    ('compare', 'threat.comparison', 'ss.threat.comparison', 14),
    ('compare field', 'threat.comparison.field', 'ss.threat.comparison.field', 15),
    ('compare report', 'threat.comparison.report', 'ss.threat.comparison.report', 16),
]


class ThreatSyncConfig(models.Model):
    _name = 'threat.sync.config'
    _description = 'Threat Synchronize Configuration'

    name = fields.Char('Server Name')
    host = fields.Char('Host')
    username = fields.Char('Username')
    pwd = fields.Char('Password')
    db = fields.Char('Database')

    ssid = fields.Char('Session ID')
    dt = fields.Datetime('Last Sync')

    request_ids = fields.One2many('threat.sync.request', 'sync_config_id', 'Requests')

    # ---------------Download
    def download_datas(self):
        sess_authen = self.get_session_info()
        if sess_authen:
            header = {
                'Content-Type': 'application/json',
                'X-Openerp-Session-Id': self.ssid
            }
            data = {
                "jsonrpc": "2.0",
                'params': {'dt': self.dt}
            }

            # Download data
            url_pull_data = 'http://' + '/'.join(s.strip('/') for s in (self.host, '/dhag/api/download/'))
            res = requests.post(url_pull_data, data=json.dumps(data, default=str), headers=header)
            if res and res.status_code == 200 and res.json().get('result'):
                if res.json()['result']['success']:
                    results = res.json()['result']['results']
                    lst_models = [m for m in results]
                    lst_models.sort(key=lambda m: results[m]['priority'])
                    models = self.env['ir.model'].search([('model', 'in', lst_models)])
                    count_data = []
                    lst_count_models = [n[1] for n in model_lst]
                    for m in lst_models:
                        self.env[m].extract_sync_data(results[m], type='pull')
                        model = models.filtered(lambda md: md.model == m)
                        if m in lst_count_models and model and len(results[m]['writes']) > 0:
                            count_data.append({
                                'model': model.name,
                                'value': len(results[m]['writes']),
                            })
                    return {
                        'success': True,
                        'results': count_data
                    }
                else:
                    return {
                        'success': False,
                        'message': _('Download data Failed.')
                    }
            else:
                return {
                        'success': True,
                        'message': _('Synchronize failed.')
                    }
        else:
            return {
                'success': False,
                'message': _('Authenticate failure!\nThe Synchronize configuration seem need to update.')
            }

    # ---------------Upload
    def _prepare_upload_data(self, sequences):
        USERS = self.env['res.users']
        DEPARTMENT_SUGGEST = self.env['investigate.department.suggest']

        data = {
            'res.users': USERS._prepare_push_data(),
            'investigate.department.suggest': DEPARTMENT_SUGGEST._prepare_push_data()
        }
        data.update({n[1]: self.env[n[1]]._prepare_push_data(self.dt, sequences.get(n[2], 1)) for n in model_lst})

        # Priority
        data['res.users']['priority'] = 1
        data['investigate.department.suggest']['priority'] = 1
        for n in model_lst:
            data[n[1]]['priority'] = n[3]

        # New sequences
        for n in model_lst:
            data[n[1]]['new_seq'] = sequences.get(n[2]) + len(data[n[1]].get('creates', 0)) + 1

        return data

    def upload_datas(self):
        sess_authen = self.get_session_info()
        if sess_authen:
            header = {
                # 'Content-Type': 'application/json',
                'X-Openerp-Session-Id': self.ssid
            }
            data = {
                "jsonrpc": "2.0"
            }

            # Get current sequence
            url_get_sequences = 'http://' + '/'.join(
                s.strip('/') for s in (self.host, '/dhag/api/get_sequence_current/'))
            sequence_data = requests.get(url_get_sequences, headers=header).json()

            push_data = self._prepare_upload_data(sequence_data)

            # Update base sequence
            url_update_sequences = 'http://' + '/'.join(
                s.strip('/') for s in (self.host, '/dhag/api/update_sequence_current/'))
            header.update({
                'Content-Type': 'application/json'
            })
            data.update({'params': {n[2]: push_data[n[1]].get('new_seq') for n in model_lst}})

            requests.post(url_update_sequences, data=json.dumps(data), headers=header)

            # Pull data
            vals = {'sync_config_id': self.id, 'state': 'failed'}
            pull = self.download_datas()
            if pull and pull['success']:
                # Push data
                url_push_data = 'http://' + '/'.join(s.strip('/') for s in (self.host, '/dhag/api/upload/'))
                data.update({
                    'params': push_data
                })

                lst_models = [n[1] for n in model_lst]
                models = self.env['ir.model'].search([('model', 'in', lst_models)])
                counts = []
                for n in lst_models:
                    model = models.filtered(lambda md: md.model == n)
                    if model:
                        counts.append({
                            'model': model.name,
                            'value': len(push_data[n]['creates']) + len(push_data[n]['writes']),
                        })
                count_data = [i for i in counts if i.get('value') > 0]
                res = requests.post(url_push_data, data=json.dumps(data, default=str), headers=header)
                if res and res.status_code == 200 and res.json().get('result'):
                    if res.json()['result']['success']:
                        vals.update({
                            'state': 'success',
                            'upload_content': json.dumps(count_data, default=str),
                            'download_content': json.dumps(pull.get('results'), default=str),
                            'total_upload': sum([i.get('value', 0) for i in count_data]),
                            'total_download': sum([i.get('value', 0) for i in pull['results']])
                        })
                    else:
                        vals.update({
                            'fail_content': _('Upload data Failed.'),
                        })
                    self.dt = fields.Datetime.now()
                else:
                    vals.update({
                        'fail_content': _('Synchronize failed.'),
                    })
            else:
                vals.update({
                    'fail_content': pull.get('message'),
                })

            vals.update({'dt': fields.Datetime.now()})
            self.env['threat.sync.request'].create(vals)

    # ---------------Authenticate
    def test_call(self):
        session = self.get_session_info()
        if session:
            self.ssid = session
            raise UserError(_('Connection successful.'))
        else:
            raise UserError(_('Could not connect to Server.\n Please check-out the Server config.'))

    def _get_session(self):
        header = {
            'Content-Type': 'application/json'
        }
        data = {
            "jsonrpc": "2.0",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.pwd
            }
        }
        url = 'http://' + '/'.join(s.strip('/') for s in (self.host, '/web/session/authenticate'))
        res = requests.post(url, data=json.dumps(data), headers=header)
        if res and res.status_code == 200 and res.json().get('result'):
            ss_id = res.headers['Set-Cookie'].split(';')[0][11:]
            return ss_id
        else:
            return False

    def get_session_info(self):
        check = False
        if self.ssid:
            header = {
                'Content-Type': 'application/json',
                'X-Openerp-Session-Id': self.ssid
            }
            data = {
                "jsonrpc": "2.0"
            }
            url_session_info = 'http://' + '/'.join(s.strip('/') for s in (self.host, '/web/session/get_session_info'))
            res = requests.post(url_session_info, data=json.dumps(data), headers=header)
            if res and res.status_code == 200 and res.json().get('result'):
                res_data = res.json()['result']
                if res_data['db'] == self.db and res_data['username'] == self.username:
                    check = True

        if not check:
            ssid = self._get_session()
            if ssid:
                self.ssid = ssid
            check = ssid

        return check
