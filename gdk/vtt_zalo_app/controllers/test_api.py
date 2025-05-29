# -*- coding: utf-8 -*-
import hashlib
import hmac
import random

import requests

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import json
import datetime
import base64
import xmlrpc.client as xmlrpclib
# import jwt
from datetime import datetime, timedelta

from odoo import api
from odoo.tools import image_guess_size_from_field_name

import logging
_logger = logging.getLogger(__name__)

from odoo import _

class TestAPI(http.Controller):
    # Phuc vu cho viec test

    @http.route('/api/test', type='json', auth="public", methods=['POST'])
    def api_test(self):
        params = request.httprequest.json

        s_date = params.get('date', '')

        s = False

        if s_date != '':
            d = request.env['sale.order'].sudo().search(domain=[
                ['date_order', '>=', s_date]
            ])
            if d:
                s = True

        ab = request.env['sale.order'].sudo().search(domain=[

        ])

        c = request.env['sale.order'].sudo().browse(1)

        date1 = ' no '
        date2 = ' no 2'
        if ab:
            a = ab[0]
            date1 = a.date_order

        if c:
            date2 = c.date_order

        return {
            'success': True,
            'param': json.dumps(params),
            'date1': date1,
            'date2': date2,
            'search': s
        }

    @http.route('/api/test_api_com', type='json', auth="public", methods=['POST'])
    def test_api_com(self):
        com = request.env['res.company'].sudo().browse(1)
        discount_product = com.sale_discount_product_id

        if not discount_product:
            com.sale_discount_product_id = request.env['product.product'].sudo().create({
                    'name': _('Discount'),
                    'type': 'service',
                    'invoice_policy': 'order',
                    'list_price': 0.0,
                    'company_id': com.id,
                    'taxes_id': None,
                }
            )

        done = com.sale_discount_product_id


        return 'result'


    # ******************************************** ----- API ----- ****************************************************
    # webhook
    @http.route('/vtt/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
    ###                 OLD

    @http.route('/vtt/api/authenticate', type='json', auth="none", methods=['POST'])
    def authenticate(self, db, login, password, base_location=None):
        # user = request.env['res.users'].sudo().search_read(domain=[['login', '=', login]], fields=['name', 'state'],
        #                                                    limit=1)
        # # print(user)
        #
        # if (user and user[0]['state'] == 'new'):
        #     # print(user[0]['state'])
        #     return {
        #         "error": {
        #             "code": 200,
        #             "message": "Odoo Server Error",
        #             "data": {
        #                 "name": "vtt.exceptions.accountIsNotActive",
        #                 "debug": "",
        #                 "message": "Access Denied",
        #                 "arguments": [
        #                     "Access Denied"
        #                 ],
        #                 "context": {}
        #             }
        #         }
        #     }

        abc = request.session.authenticate(db, login, password)
        # abc = request.env['ir.http'].session_info()
        # bbb = ''
        ccc = request.env['ir.http'].session_info()

        return ccc


    # API dang ky cho LHV
    @http.route('/vtt/api/do_register', type='json', auth="none", methods=['POST'])
    def do_register(self, uname, pwd):
        # issuc = request.env['res.users'].sudo().do_register(uname, pwd)
        groups_id = request.env.ref('base.group_portal')
        values = {
            'active': True,
            "login": uname,
            "password": pwd,
            "name": uname,
            'groups_id': groups_id,
            'company_id': 1,
            'company_ids': [(6, 0, [1])]
        }
        rec = request.env['res.users'].sudo().create(values)

        return ''

    # API dang ky cho LHV
    @http.route('/vtt/api/register', type='json', auth="none", methods=['POST'])
    def register(self, uname, pwd):
        url = "http://localhost:8084"
        # url = "http://lhv.victo.vn"
        # db = "lhv"
        db = "test_17"
        username = 'admin'
        password = '123'
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [
            {'name': uname, 'login': uname, 'company_ids': [1], 'company_id': 1,
             'password': pwd, 'sel_groups_1_9_10': 10, 'state': 'new'}])
        user = request.env['res.users'].sudo().search([['id', '=', user_id]])
        if user:
            request.session.authenticate(db, username, password)
            print('auth')

        user.action_reset_password()
        # sale_module_categ_id = models.execute_kw(db, uid, password, 'ir.module.category', 'search',
        #                                          [('name', '=', 'sales')])
        # # SEARCHES AND LINKING CUSTOMER TO THE GROUP SALES MANAGER
        # if sale_module_categ_id:
        #     sale_manager_group_id = models.execute_kw(db, uid, password, 'res.group', 'search',
        #                                               [('name', '=', 'sales '),
        #                                                ('category_id', '=', sale_module_categ_id[0])])
        #     if sale_manager_group_id:
        #         models.execute_kw(db, uid, password, 'res.group', 'write', sale_manager_group_id,
        #                           {'users': [(4, user_id)]})
        # # SEARCHES AND LINKING CUSTOMER TO THE GROUP WAREHOUSE MANAGER
        # warehouse_module_categ_id = models.execute_kw(db, uid, password, 'ir.module.category', 'search',
        #                                               [('name', '=', 'sales')])
        # if warehouse_module_categ_id:
        #     warehouse_manager_group_id = models.execute_kw(db, uid, password, 'res.group', 'search',
        #                                                    [('name', '=', 'sales '),
        #                                                     ('category_id', '=', warehouse_module_categ_id[0])])
        #     if warehouse_manager_group_id:
        #         models.execute_kw(db, uid, password, 'res.group', 'write', warehouse_manager_group_id,
        #                           {'users': [(4, user_id)]})

        # db = "Odoo8TestMac"
        # username = 'admin'
        # password = 'admin'
        # common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        # uid = common.authenticate(db, username, password, {})
        # models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # user_id = models.execute_kw(db, uid, password, 'res.users', 'create', [
        #     {'name': "userAPI9", 'login': 'userapi9@gmail.com', 'company_ids': [1], 'company_id': 1,
        #      'new_password': '123456', 'sel_groups_39_40': 40, 'sel_groups_9_44_10': 10, 'sel_groups_29_30': 30,
        #      'sel_groups_36_37': 37, 'sel_groups_21_22_23': 23, 'sel_groups_5': 5}])

        # print('register>>>>')
        return {
            'abc': 'hello'
        }

    # -------------------------------------

    # search ignore permission trong pham vi cac model cho phep
    @http.route('/vtt/api/search_ignore_permission', type='json', auth="user", methods=['POST'])
    def search_ignore_permission(self, request):
        # print('search ignore')
        # print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }

        # allowed model
        allowed_model = ['sale.order', 'sale.order.line', 'account.move', 'sale.subscription',
                         'sale.subscription.template', 'sale.subscription.line', 'sale.subscription.stage',
                         'product.product', 'product.template', 'product.category', 'utm.source']
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params.get('model', '')
            if (model == '' or model not in allowed_model):
                args['message'] = 'wrong model or access denied'
                return args
            domain = params.get('domain', [])
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])
            limit = params.get('limit', None)
            offset = params.get('offset', 0)
            order = params.get('order', None)
            search_count = params.get('search_count', False)

            count = request.env[model].sudo().search_count(domain)
            if search_count == False:
                result = request.env[model].sudo().with_context(lang='vi_VN').search_read(domain=domain, fields=fields,
                                                                                          limit=limit, offset=offset,
                                                                                          order=order)
                # remove all field with false value following ignore_false_fields parameter
                if ignore_false_fields:
                    result_str = json.dumps(result, default=str)
                    for field in ignore_false_fields:
                        r = ', "' + field + '": false'
                        result_str = result_str.replace(r, '')
                    result = json.loads(result_str)
                args['result']['items'] = result

            args['result']['total_items'] = count
            args['success'] = True
            args['message'] = 'success'
            # print(args)
        return args

    # search base
    @http.route('/vtt/api/vttbase/search', type='json', auth='user', methods=['POST'], csrf=False)
    def base_search(self):
        re = request
        # return ''
        return self._base_search(re)

    # get base
    @http.route('/vtt/api/vttbase/get', type='json', auth='user', methods=['POST'])
    def base_get(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params.get('model')
            id = params.get('id')
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])

            obj = request.env[model].with_context(lang='vi_VN').browse(id)

            if obj:
                result = obj.read(fields)
                # remove all field with false value following ignore_false_fields parameter
                if ignore_false_fields:
                    result_str = json.dumps(result)
                    for field in ignore_false_fields:
                        r = ', "' + field + '": false'
                        result_str = result_str.replace(r, '')
                    result = json.loads(result_str)

                args = {
                    'success': True,
                    'message': 'Success',
                    'result': {
                        'item': result[0]
                    }
                }
        return args

    @http.route('/vtt/api/get_ignore_permission', type='json', auth='user', methods=['POST'])
    def get_ignore_permission(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        # allowed model
        allowed_model = ['sale.order', 'sale.order.line']
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params.get('model')
            model = params.get('model', '')
            if (model == '' or model not in allowed_model):
                args['message'] = 'wrong model or access denied'
                return args
            id = params.get('id')
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])

            obj = request.env[model].sudo().with_context(lang='vi_VN').browse(id)

            if obj:
                result = obj.read(fields)
                # remove all field with false value following ignore_false_fields parameter
                if ignore_false_fields:
                    result_str = json.dumps(result)
                    for field in ignore_false_fields:
                        r = ', "' + field + '": false'
                        result_str = result_str.replace(r, '')
                    result = json.loads(result_str)

                args = {
                    'success': True,
                    'message': 'Success',
                    'result': {
                        'item': result[0]
                    }
                }
        return args

    # base save (create | update)
    @http.route('/vtt/api/vttbase/save', type='json', auth='user', methods=['POST'])
    def base_save(self):
        re = request
        re1 = request.httprequest
        if re1.json:
            data = re1.json
            params = data['parameters']
            # print(params)
            input = params.get('input')
            id = input.get('id', -1)
            if id and id > 0:
                return self._base_edit(re)
            return self._base_create(re)

    # user remove device id
    @http.route('/vtt/api/user/registry_device', type='json', auth='user', methods=['POST'])
    def user_registry_device(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            token = params.get('fcm_token')
            uid = params.get('id')
            result = request.env['vtt.user.app.device'].search([['fcm_token', '=', token]])
            if not result:
                request.env['vtt.user.app.device'].create({
                    'user_id': uid,
                    'fcm_token': token
                })
                args = {
                    'success': True,
                    'message': 'Success'
                }
        return args

    # user remove device id
    @http.route('/vtt/api/user/remove_device', type='json', auth='user', methods=['POST'])
    def user_remove_device(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            # print(params)
            token = params.get('fcm_token')
            if token:
                result = request.env['vtt.user.app.device'].search([['fcm_token', '=', token]])
                if result:
                    result.unlink()
                    args = {
                        'success': True,
                        'message': 'Success'
                    }
        return args

    # @http.route('/vtt/api/mailactivity/doneactivity', type='json', auth='user', methods=['POST'])
    # def mail_actvity_done(self, request):
    #     #print('test base')
    #     args = {
    #         'success': False,
    #         'message': 'Failed',
    #         'results': []
    #     }
    #     if request.jsonrequest:
    #         data = request.jsonrequest
    #         params = data['parameters']
    #         #print(params)
    #         message = params.get('message', '')  # ...
    #         input = params['input']
    #         if input:
    #             id = input.get('id', -1)
    #
    #             activity = request.env['mail.activity'].browse(id)
    #             # if message != '':
    #             #     result = activity.action_feedback(feedback=message)
    #             # else:
    #             #     activity.action_done()
    #             args['success'] = True
    #             args['message'] = 'success'
    #
    #     return args

    # @http.route('/vtt/api/testbase/doneactivity', type='json', auth='user', methods=['POST'])
    # def test_doneactivity(self, request):
    #     #print('test base')
    #     args = {
    #         'success': False,
    #         'message': 'Failed',
    #         'results': []
    #     }
    #     if request.jsonrequest:
    #         data = request.jsonrequest
    #         params = data['parameters']
    #         message = params.get('message', '') #...
    #         id = params.get('id', -1)
    #
    #
    #         activity = request.env['mail.activity'].browse(id)
    #         if message != '':
    #             result = activity.action_feedback(feedback=message)
    #         else:
    #             activity.action_done()
    #     return ''

    # @http.route('/vtt/api/testbase/uploadattachment', type='json', auth='user', methods=['POST'])
    # def test_upload_attachment(self, request):
    #     #print('test base')
    #     args = {
    #         'success': False,
    #         'message': 'Failed',
    #         'results': []
    #     }
    #     if request.jsonrequest:
    #         data = request.jsonrequest
    #         params = data['parameters']
    #         base64_datas = params['datas']  # ...
    #         datas = base64_datas[base64_datas.index('base64,') + 7:]
    #
    #         Model = request.env['ir.attachment']
    #         attachment = Model.create({
    #             'name': 'blomm.jpg',
    #             'datas': datas,
    #                 'res_model': 'project.task',
    #                 'res_id': 20
    #         })
    #
    #     return ''

    # ******************************************** ----- END API ----- ************************************************

    # ******************************************** ----- BASE ----- ***************************************************
    # search
    def _base_search(self, request):
        # print('base search')
        # print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        re = request.httprequest
        if re.json:
            data = re.json
            # params = data['parameters']
            params = data.get('params')
            model = params.get('model')
            domain = params.get('domain', [])
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])
            limit = params.get('limit', None)
            offset = params.get('offset', 0)
            order = params.get('order', None)
            search_count = params.get('search_count', False)

            count = request.env[model].search_count(domain)
            if search_count == False:
                rr = request.env[model].sudo().search(domain=[])
                result = request.env[model].sudo().with_context(lang='vi_VN').search_read(domain=domain,
                                                                                          fields=fields,
                                                                                          limit=limit,
                                                                                          offset=offset,
                                                                                          order=order)
                # remove all field with false value following ignore_false_fields parameter
                if ignore_false_fields:
                    result_str = json.dumps(result, default=str)
                    for field in ignore_false_fields:
                        r = ', "' + field + '": false'
                        result_str = result_str.replace(r, '')
                    result = json.loads(result_str)
                args['result']['items'] = result

            args['result']['total_items'] = count
            args['success'] = True
            args['message'] = 'success'
            # print(args)
        return args

    # Create
    def _base_create(self, request):
        args = {
            'success': False,
            'message': 'Create failed',
            'result': {}
        }
        re = request.httprequest
        if re.json:
            data = re.json
            params = data['parameters']

            model = params.get('model')
            input = params['input']
            attachments = params.get('attachments', False)

            if input:
                obj = request.env[model].create(input)
                record = obj.read()
                if record and record[0]['id'] > 0:
                    if attachments != False:
                        for attachment in attachments:
                            attachment['res_id'] = record[0]['id']
                            attachment['res_model'] = model
                            request.env['ir.attachment'].create(attachment)

                    args.update({
                        'success': True,
                        'message': 'Success',
                        'result': {
                            'id': record[0]['id']
                        }
                    })
            # print(args)
        return args

    # Update
    def _base_edit(self, request):
        args = {
            'success': False,
            'message': 'Edit failed',
            'results': []
        }
        re = request.httprequest
        if re.json:
            data = re.json
            # data = request.jsonrequest
            params = data['parameters']
            model = params.get('model')
            input = params.get('input')
            id = input.get('id', -1)
            if input and id > 0:
                obj = request.env[model].browse(id)

                if input and obj:
                    record = obj.write(input)
                    args.update({
                        'success': True,
                        'message': 'Success',
                        'result': {
                            'id': id
                        }
                    })
        return args

    # ******************************************** ----- END BASE ----- ***********************************************