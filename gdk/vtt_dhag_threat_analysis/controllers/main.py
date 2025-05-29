# -*- coding: utf-8 -*-

import logging
from datetime import datetime

# from odoo.addons.mail.controllers.mail import MailController
from odoo import http
from odoo.http import request

FIELDS_EXCLUDE = {'many2many', 'many2one', 'one2many', 'many2one_reference',
                  'properties', 'properties_definition'}

_logger = logging.getLogger(__name__)


class DHAGController(http.Controller):

    def auth_api_key(self, api_key):
        """This function is used to authenticate the api-key when sending a
        request"""
        user_id = request.env["res.users.apikeys"]._check_credentials(scope='rpc', key=api_key)
        return user_id

    @http.route('/dhag/api/key/', type='json', auth='public', methods=['POST'])
    def get_api_key(self, **kwargs):
        args = {
            'success': False,
            'message': 'Failed',
            'dt_submission': False,
            'results': {}
        }
        # Authenticate
        # api_key = request.httprequest.headers.get('api-key')
        # auth_api = self.auth_api_key(api_key)
        username = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        db = request.httprequest.headers.get('db')
        uid = request.httprequest.headers.get('uid')
        # if not auth_api:
        request.session.authenticate(db, username, password)

        new_key = request.env['res.users.apikeys'].sudo().with_user(uid)._generate(None, 'My Next key')

        args = {
            'success': False,
            'message': 'Failed',
            'dt_submission': datetime.now(),
            'results': {'apikey': new_key}
        }

        return args

    def extract_datas(self, uid, datas):
        result = {}
        # With followup create
        for m in datas:
            model = request.env[m].sudo().with_user(uid)

            if m == 'res.users':
                if datas[m].get('create'):
                    result[m] = {}
                    users = model.search([])
                    for res_id in datas[m]['create']:
                        r_vals = {k: v for k, v in datas[m]['create'][res_id].items() if k != 'partner_id'}
                        r = users.filtered(lambda u: u.login == r_vals['login'])
                        if not r:
                            r = model.create(r_vals)
                        result[m].update({res_id: r.id})
                        if 'res.partner' in result:
                            result['res.partner'][datas[m]['create'][res_id]['partner_id']] = r.partner_id.id
                        else:
                            result['res.partner'] = {datas[m]['create'][res_id]['partner_id']: r.partner_id.id}

            if m == 'investigate.location':
                if datas[m].get('create'):
                    result[m] = {}
                    for res_id in datas[m]['create']:
                        r_vals = {k: v for k, v in datas[m]['create'][res_id].items() if k != 'address_id'}
                        r = model.create(r_vals)
                        result[m].update({res_id: r.id})
                        if 'res.partner' in result:
                            result['res.partner'][datas[m]['create'][res_id]['address_id']] = r.address_id.id
                        else:
                            result['res.partner'] = {datas[m]['create'][res_id]['address_id']: r.address_id.id}

        # Other create
        for m in datas:
            model = request.env[m].sudo().with_user(uid)

            if m not in ('res.users', 'investigate.location'):
                if datas[m].get('create'):
                    result[m] = {}
                    for res_id in datas[m]['create']:
                        r = model.create(datas[m]['create'][res_id])
                        result[m].update({res_id: r.id})

        # Edit
        for m in datas:
            model = request.env[m].sudo().with_user(uid)
            if datas[m].get('edit'):
                for res_id in datas[m]['edit']:
                    r_vals = {k: v for k, v in datas[m]['edit'][res_id].items() if k != 's_id'}
                    r_id = model.browse(int(datas[m]['edit'][res_id]['s_id']))
                    if r_id:
                        r_id.with_user(uid).write(r_vals)

        # Relations fields
        for m in datas:
            model = request.env[m].sudo().with_user(uid)
            if datas[m].get('relation'):
                for ml in datas[m]['relation']:
                    rd = model.browse(result[m][ml])
                    ml_vals = {}
                    for c_field in datas[m]['relation'][ml]:
                        comodel = model._fields[c_field].comodel_name
                        if type(datas[m]['relation'][ml][c_field][1]) is list:
                            ml_vals[c_field] = datas[m]['relation'][ml][c_field][1]
                        elif type(datas[m]['relation'][ml][c_field][1]) is dict:
                            c_field_data = [v for k, v in datas[m]['relation'][ml][c_field][1].items() if v not in (False, None, 0)]
                            if comodel in result:
                                c_field_data += [result[comodel][k] for k, v in datas[m]['relation'][ml][c_field][1].items() if v in (False, None, 0)]
                            ml_vals[c_field] = c_field_data
                        else:
                            if datas[m]['relation'][ml][c_field][1] not in (False, None, 0):
                                c_field_data = datas[m]['relation'][ml][c_field][1]
                            else:
                                if comodel in result:
                                    c_field_data = result[comodel].get(datas[m]['relation'][ml][c_field][0])
                                else:
                                    c_field_data = datas[m]['relation'][ml][c_field][0]
                            ml_vals[c_field] = c_field_data
                    if ml_vals:
                        rd.write(ml_vals)
        return result

    @http.route('/dhag/api/upload/', type='json', auth='public', methods=['POST'])
    def threat_upload(self, **kwargs):
        args = {
            'success': False,
            'message': 'Failed',
            'dt_submission': False,
            'results': {}
        }
        # Authenticate
        api_key = request.httprequest.headers.get('api-key')
        auth_api = self.auth_api_key(api_key)
        username = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        db = request.httprequest.headers.get('db')
        if not auth_api:
            request.session.authenticate(db, username, password)

        # if request.jsonrequest:
        # res = request.jsonrequest
        # params = kwargs.get('params')
        params = kwargs
        if params:

            result = self.extract_datas(auth_api, params)

            args.update({
                'success': True,
                'message': 'Success',
                'dt_submission': datetime.now(),
                'results': result,
            })
        return args

    def prepare_download_data(self, dt=None):
        data = {}
        log_domain = []
        if dt:
            log_domain.append(('create_date', '>', dt))
        logs = request.env['auditlog.log'].sudo().search(log_domain).sorted(lambda l: l.create_date)
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
                rd = request.env[m.model].sudo().browse(ml.res_id)
                ml_data = {c_field.field_name: c_field.new_value_text for c_field in ml.line_ids if
                           c_field.field_id.ttype not in FIELDS_EXCLUDE}
                m_create[ml.res_id] = ml_data
                # Followup create
                if m.model == 'res.users':
                    m_create[ml.res_id]['partner_id'] = rd.partner_id.id
                elif m.model == 'investigate.location':
                    m_create[ml.res_id]['address_id'] = rd.address_id.id

                # Relation fields
                ml_many2one = {c_field.field_name: rd[c_field.field_name].id for c_field in ml.line_ids if c_field.field_id.ttype == 'many2one' and not (
                            m.model in ('res.users', 'investigate.location') and c_field.field_name == 'partner_id')}
                ml_many2many = {c_field.field_name: rd[c_field.field_name].ids for c_field in ml.line_ids if c_field.field_id.ttype == 'many2many'}

                ml_relation = ml_many2one
                ml_relation.update(ml_many2many)
                if ml_relation:
                    m_relation[ml.res_id] = ml_relation

            # Records update
            m_logs_edit = m_logs.filtered(lambda l: l.method == 'write')
            m_edit = {}
            for ml in m_logs_edit:
                rd = request.env[m.model].sudo().browse(ml.res_id)
                ml_data = {c_field.field_name: c_field.new_value_text for c_field in ml.line_ids if
                           c_field.field_id.ttype not in FIELDS_EXCLUDE}
                if ml.res_id in m_create:
                    m_create[ml.res_id].update(ml_data)
                else:
                    m_edit[ml.res_id] = ml_data

                # Relation fields
                ml_many2one = {c_field.field_name: rd[c_field.field_name].id for c_field in ml.line_ids if c_field.field_id.ttype == 'many2one'}
                ml_many2many = {c_field.field_name: rd[c_field.field_name].ids for c_field in ml.line_ids if c_field.field_id.ttype == 'many2many'}

                ml_relation = ml_many2one
                ml_relation.update(ml_many2many)
                if ml_relation:
                    if ml.res_id in m_relation:
                        m_relation[ml.res_id].update(ml_relation)
                    else:
                        m_relation[ml.res_id] = ml_relation

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
                        data['res.partner']['create'] = {k: v for k, v in data['res.partner']['create'] if
                                                         k != ml_partner_id}
        # Users only
        users_all = request.env['res.users'].sudo().search([])
        data['users'] = {u.login: {'uid': u.id, 'partner_id': u.partner_id.id} for u in users_all}

        return data

    @http.route('/dhag/api/download/', type='json', auth='public', methods=['POST'])
    def threat_download(self, **kwargs):
        args = {
            'success': False,
            'message': 'Failed',
            'dt_submission': False,
            'results': []
        }
        # Authenticate
        api_key = request.httprequest.headers.get('api-key')
        auth_api = self.auth_api_key(api_key)
        username = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        db = request.httprequest.headers.get('db')
        if not auth_api:
            request.session.authenticate(db, username, password)

        params = kwargs

        dt = params.get('dt')
        data = self.prepare_download_data(dt)

        args.update({
            'success': True,
            'message': 'Success',
            'dt_submission': datetime.now(),
            'results': data
        })

        return args