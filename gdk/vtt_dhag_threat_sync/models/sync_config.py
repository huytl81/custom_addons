# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID
import requests
import json
from odoo.exceptions import UserError
import base64

FIELDS_EXCLUDE = {'many2many', 'many2one', 'one2many', 'many2one_reference',
                  'properties', 'properties_definition'}


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
    dt_download = fields.Datetime('Last Download')

    api_key = fields.Char('API Key')

    request_ids = fields.One2many('threat.sync.request', 'sync_config_id', 'Requests')

    # ---------------Download
    def extract_datas(self, datas):
        result = {}
        # With followup create
        for m in datas:
            if m == 'users':
                for ml in datas[m]:
                    rd = self.env['res.users'].sudo().with_user(SUPERUSER_ID).search([('login', '=', ml)])
                    if rd:
                        rd.s_id = datas[m][ml]['uid']
                        rd.partner_id.s_id = datas[m][ml]['partner_id']

            if m == 'res.users':
                model = self.env[m].sudo().with_user(SUPERUSER_ID)
                if datas[m].get('create'):
                    result[m] = {}
                    users = model.search([])
                    for res_id in datas[m]['create']:
                        r_vals = {k: v for k, v in datas[m]['create'][res_id].items() if k != 'partner_id'}
                        r_vals['s_id'] = int(res_id)
                        r = users.filtered(lambda u: u.login == r_vals['login'])
                        if not r:
                            r = model.create(r_vals)
                        result[m].update({res_id: r.id})
                        if 'res.partner' in result:
                            result['res.partner'][datas[m]['create'][res_id]['partner_id']] = r.partner_id.id
                        else:
                            result['res.partner'] = {datas[m]['create'][res_id]['partner_id']: r.partner_id.id}

            if m == 'investigate.location':
                model = self.env[m].sudo().with_user(SUPERUSER_ID)
                if datas[m].get('create'):
                    result[m] = {}
                    for res_id in datas[m]['create']:
                        r_vals = {k: v for k, v in datas[m]['create'][res_id].items() if k != 'address_id'}
                        r_vals['s_id'] = int(res_id)
                        r = model.create(r_vals)
                        result[m].update({res_id: r.id})
                        if 'res.partner' in result:
                            result['res.partner'][datas[m]['create'][res_id]['address_id']] = r.address_id.id
                        else:
                            result['res.partner'] = {datas[m]['create'][res_id]['address_id']: r.address_id.id}

        # Other create
        for m in datas:
            if m != 'users':
                model = self.env[m].sudo().with_user(SUPERUSER_ID)

                if m not in ('res.users', 'investigate.location'):
                    if datas[m].get('create'):
                        result[m] = {}
                        for res_id in datas[m]['create']:
                            r_vals = datas[m]['create'][res_id]
                            r_vals['s_id'] = int(res_id)
                            r = model.create(datas[m]['create'][res_id])
                            result[m].update({res_id: r.id})

        # Edit
        for m in datas:
            if m != 'users':
                model = self.env[m].sudo().with_user(SUPERUSER_ID)
                if datas[m].get('edit'):
                    for res_id in datas[m]['edit']:
                        r_vals = {k: v for k, v in datas[m]['edit'][res_id].items() if k != 's_id'}
                        r_id = model.search([('s_id', '=', int(res_id))])
                        if r_id:
                            r_id.with_user(SUPERUSER_ID).write(r_vals)

        # Relations fields
        for m in datas:
            if m != 'users':
                model = self.env[m].sudo().with_user(SUPERUSER_ID)
                if datas[m].get('relation'):
                    for ml in datas[m]['relation']:
                        rd = model.browse(result[m][ml])
                        ml_vals = {}
                        for c_field in datas[m]['relation'][ml]:
                            comodel = model._fields[c_field].comodel_name
                            comodel_sudo = self.env[comodel].sudo()
                            if type(datas[m]['relation'][ml][c_field]) is list:
                                ml_comodel_id = comodel_sudo.search([('s_id', 'in', datas[m]['relation'][ml][c_field])]).ids
                                if comodel in result:
                                    ml_comodel_id += [result[comodel].get(k) for k in datas[m]['relation'][ml][c_field]]
                                ml_comodel_id = list(set(ml_comodel_id))
                                ml_vals[c_field] = ml_comodel_id
                            else:
                                if datas[m]['relation'][ml][c_field]:
                                    ml_comodel_id = False
                                    if comodel in result:
                                        ml_comodel_id = result[comodel].get(datas[m]['relation'][ml][c_field])
                                    if not ml_comodel_id:
                                        ml_comodel_id = comodel_sudo.search([('s_id', '=', datas[m]['relation'][ml][c_field])]).id
                                    c_field_data = ml_comodel_id
                                else:
                                    c_field_data = datas[m]['relation'][ml][c_field]
                                ml_vals[c_field] = c_field_data
                        if ml_vals:
                            rd.write(ml_vals)
        return result

    def download_datas(self):
        sess_authen = self.get_session_info()
        if sess_authen:
            header = {
                'Content-Type': 'application/json',
                # 'X-Openerp-Session-Id': self.ssid,
                'api_key': self.api_key,
                'db': self.db,
                'login': self.username,
                'password': self.pwd,
            }
            data = {
                "jsonrpc": "2.0"
            }
            if self.dt_download:
                data.update({
                    'params': {'dt': self.dt_download}
                })

            # Download data
            url_pull_data = 'http://' + '/'.join(s.strip('/') for s in (self.host, '/dhag/api/download/'))
            res = requests.post(url_pull_data, data=json.dumps(data, default=str), headers=header)
            if res and res.status_code == 200 and res.json().get('result'):
                if res.json()['result']['success']:
                    results = res.json()['result']['results']
                    download_data = self.extract_datas(results)
                    count_data = sum([len(m.keys()) for m in download_data])
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
                        'success': False,
                        'message': _('Synchronize failed.')
                    }
        else:
            return {
                'success': False,
                'message': _('Authenticate failure!\nThe Synchronize configuration seem need to update.')
            }

    # ---------------Upload
    def _prepare_upload_data(self):
        data = {}
        log_domain = []
        if self.dt:
            log_domain.append(('create_date', '>', self.dt))
        logs = self.env['auditlog.log'].search(log_domain).sorted(lambda l: l.create_date)
        log_models = logs.mapped('model_id')
        for m in log_models:
            m_many2one = {}
            m_many2many = {}
            m_relation = {}
            m_logs = logs.filtered(lambda l: l.model_id == m)
            # Records new
            m_logs_create = m_logs.filtered(lambda l: l.method == 'create')
            m_create = {}
            for ml in m_logs_create:
                rd = self.env[m.model].browse(ml.res_id)
                ml_data = {c_field.field_name: c_field.new_value_text for c_field in ml.line_ids if c_field.field_id.ttype not in FIELDS_EXCLUDE and c_field.field_name not in ('s_id', 'from_last_sync_submit')}
                m_create[ml.res_id] = ml_data
                # Followup create
                if m.model == 'res.users':
                    m_create[ml.res_id]['partner_id'] = rd.partner_id.id
                elif m.model == 'investigate.location':
                    m_create[ml.res_id]['address_id'] = rd.address_id.id

                # Relation fields
                ml_many2one = {c_field.field_name: (
                    rd[c_field.field_name].id,
                    's_id' in rd[c_field.field_name] and rd[c_field.field_name]['s_id'] or False
                ) for c_field in ml.line_ids if c_field.field_id.ttype == 'many2one' and not (m.model in ('res.users', 'investigate.location') and c_field.field_name == 'partner_id')}
                ml_many2many = {c_field.field_name: (
                    rd[c_field.field_name].ids,
                    's_id' in rd[c_field.field_name] and rd[c_field.field_name].get_s_id() or rd[c_field.field_name].ids
                ) for c_field in ml.line_ids if c_field.field_id.ttype == 'many2many'}

                ml_relation = ml_many2one
                ml_relation.update(ml_many2many)
                if ml_relation:
                    m_relation[ml.res_id] = ml_relation

                # if ml_many2one:
                #     m_many2one[ml.res_id] = ml_many2one
                # if ml_many2many:
                #     m_many2many[ml.res_id] = ml_many2many

            # Records update
            m_logs_edit = m_logs.filtered(lambda l: l.method == 'write')
            m_edit = {}
            for ml in m_logs_edit:
                rd = self.env[m.model].browse(ml.res_id)
                ml_data = {c_field.field_name: c_field.new_value_text for c_field in ml.line_ids if c_field.field_id.ttype not in FIELDS_EXCLUDE}
                if ml.res_id in m_create:
                    m_create[ml.res_id].update(ml_data)
                else:
                    m_edit[ml.res_id] = ml_data

                # Relation fields
                ml_many2one = {c_field.field_name: (
                    rd[c_field.field_name].id,
                    's_id' in rd[c_field.field_name] and rd[c_field.field_name]['s_id'] or False
                ) for c_field in ml.line_ids if c_field.field_id.ttype == 'many2one'}
                ml_many2many = {c_field.field_name: (
                    rd[c_field.field_name].ids,
                    's_id' in rd[c_field.field_name] and rd[c_field.field_name].get_s_id() or rd[c_field.field_name].ids
                ) for c_field in ml.line_ids if c_field.field_id.ttype == 'many2many'}

                ml_relation = ml_many2one
                ml_relation.update(ml_many2many)
                if ml_relation:
                    if ml.res_id in m_relation:
                        m_relation[ml.res_id].update(ml_relation)
                    else:
                        m_relation[ml.res_id] = ml_relation

                # if ml_many2one:
                #     if ml.res_id in m_many2one:
                #         m_many2one[ml.res_id].update(ml_many2one)
                #     else:
                #         m_many2one[ml.res_id] = ml_many2one
                # if ml_many2many:
                #     if ml.res_id in m_many2many:
                #         m_many2many[ml.res_id].update(ml_many2many)
                #     else:
                #         m_many2many[ml.res_id] = ml_many2many

            m_create = {k: v for k, v in m_create.items() if v}
            m_edit = {k: v for k, v in m_edit.items() if v}
            m_relation = {k: v for k, v in m_relation.items() if v}

            data[m.model] = {
                'create': m_create,
                'edit': m_edit,
                # 'many2one': m_many2one,
                # 'many2many': m_many2many,
                'relation': m_relation}

        # Users and Partners
        for m in data:
            if m in ('res.users', 'investigate.location'):
                for ml in data[m]['create']:
                    if 'partner_id' in data[m]['create'][ml]:
                        # Followup create
                        ml_partner_id = data[m]['create'][ml]['partner_id']
                        data['res.partner']['create'] = {k: v for k, v in data['res.partner']['create'] if k != ml_partner_id}

        return data

    def upload_datas(self):
        sess_authen = self.get_session_info()
        if sess_authen:
            header = {
                'Content-Type': 'application/json',
                # 'X-Openerp-Session-Id': self.ssid,
                'api_key': self.api_key,
                'db': self.db,
                'login': self.username,
                'password': self.pwd,
            }
            data = {
                "jsonrpc": "2.0"
            }

            push_data = self._prepare_upload_data()
            count_data = sum([len(push_data[m]['create'].keys()) for m in push_data]) + sum([len(push_data[m]['edit'].keys()) for m in push_data])

            # Pull data
            vals = {'sync_config_id': self.id, 'state': 'failed'}
            pull = self.download_datas()
            if pull and pull['success']:
            # if True:
                vals.update({
                    'state': 'success',
                    'total_upload': 0,
                    'total_download': pull['results']
                })

                # Push data
                url_push_data = 'http://' + '/'.join(s.strip('/') for s in (self.host, '/dhag/api/upload/'))
                data.update({
                    'params': push_data
                })

                res = requests.post(url_push_data, data=json.dumps(data, default=str), headers=header)
                if res and res.status_code == 200 and res.json().get('result'):
                    if res.json()['result']['success']:
                        vals.update({
                            # 'upload_content': json.dumps(count_data, default=str),
                            # 'download_content': json.dumps(pull.get('results'), default=str),
                            'total_upload': count_data
                        })
                        if res.json()['result']['results']:
                            res_data = res.json()['result']['results']
                            for m in res_data:
                                self.env[m].update_s_id(res_data[m])
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
                if check and not self.api_key:
                    url_apikey = 'http://' + '/'.join(
                        s.strip('/') for s in (self.host, '/dhag/api/key/'))
                    data_apikey = {
                        "jsonrpc": "2.0",
                        "params": {
                            "db": self.db,
                            "login": self.username,
                            "password": self.pwd,
                            "uid": res_data['uid']
                        }
                    }
                    res_apikey = requests.post(url_apikey, data=json.dumps(data_apikey), headers=header)
                    if res_apikey and res_apikey.status_code == 200 and res_apikey.json().get('result'):
                        self.api_key = res_apikey.json()['result']['results']['apikey']

        if not check:
            ssid = self._get_session()
            if ssid:
                self.ssid = ssid
            check = ssid

        return check
