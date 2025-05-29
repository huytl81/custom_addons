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

class EvAPI(http.Controller):
    # ******************************************** ----- API ----- ****************************************************

    # @http.route('/api/tect', type='json', auth='custom_auth', methods=['POST'])
    # def tecct(self):
    #     # user = request.env["res.users"].sudo().authenticate(
    #     #     'test_17',
    #     #     'admin',
    #     #     '123',
    #     #     request.httprequest.environ.get("HTTP_USER_AGENT"),
    #     # )
    #
    #     user = request.env.user
    #
    #     return 'abc'

    # @http.route('/api/zalo_auth_check', type='json', auth="user", methods=['POST'])
    # def zalo_auth_check(self, zalo_access_token):
    #     aee = request.env.user  # user hien tai theo token
    #     partner = aee.partner_id
    #     return 'accc'

    # webhook
    @http.route('/zalo_webhook/user_revoke_consent', type='json', auth="public", methods=['POST'])
    def webhook_user_revoke_consent(self):
        result = {
            'success': False,
            'message': 'Failed'
        }
        return {
            'success': True,
            'message': 'Success'
        }


    def _calculate_hmac_sha256(self, data, secret_key):
        return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

    def __check_zalo_access_token(self, zalo_access_token):
        # ZALO_APP_SECRET_KEY = "T654FlNXvO4OxF5jLnMD"        # app key ben frontend
        # ZALO_APP_SECRET_KEY = "Sy44mX2ExWY1OVHyqBwS"        # app key viettotal: SaleMate
        ZALO_APP_SECRET_KEY = "w84fOKk2bP2OTc69w7wP"  # app key victo - ban hang
        # ZALO_APP_SECRET_KEY = "4j7N7G784MLbPUqX76YT"      # app key from tk viettotal

        header_appsecret_proof = self._calculate_hmac_sha256(zalo_access_token, ZALO_APP_SECRET_KEY)

        options = {
            "url": "https://graph.zalo.me/v2.0/me",
            "method": "GET",
            "headers": {
                "access_token": zalo_access_token,
                # "appsecret_proof": '9d4a4da1ea6ca5108fa60f377ec6836526826144e779abad7324db1752b88389'
                "appsecret_proof": header_appsecret_proof
            },
            "params": {
                "fields": "id,name,birthday,picture,phone"
            }
        }

        response = requests.request(**options)

        if response.status_code == 200:
            print("Response Code:", response.status_code)
            print("Response Body:", response.json())
            return response.json()
        else:
            print("Error:", response.text)

        return {'Error': 'eeee'}

    ### lam API check zalo profile

    @http.route('/api/zalo_auth', type='json', auth="none", methods=['POST'])
    def zalo_auth(self, zalo_access_token):
        result = {
            'success': False,
            'message': 'Authentication failed'
        }

        # check zalo access token and get info
        headers = request.httprequest.headers
        zalo_token = zalo_access_token
        zalo_check = self.__check_zalo_access_token(zalo_token)

        if 'error' not in zalo_check or zalo_check['error'] > 0:
            result['error_code'] = zalo_check['error']
            result['message'] = zalo_check['message']
            return result

        zalo_id = zalo_check['id']
        zalo_name = zalo_check['name']
        zalo_avatar = ''

        if 'picture' in zalo_check and 'data' in zalo_check['picture'] and 'url' in zalo_check['picture']['data']:
            zalo_avatar = zalo_check['picture']['data']['url']

        host_url = request.httprequest.host_url  # host_url ? root_url?
        # url = "http://localhost:8084"

        # get host url + db name
        start = host_url.index('://')
        first_sub = host_url[start + 3:]
        db_name = first_sub
        end = -1
        base_url = host_url
        try:
            end = first_sub.index('/')
        except ValueError:
            res = "Element not in list !"

        if end > 0:
            db_name = first_sub[:end]
            base_url = host_url[:start + 3 + end]

        is_local = False
        if 'localhost' in base_url:
            is_local = True

        # config connection - server
        url = base_url
        db = db_name
        # admin
        addmin_username = 'admin'
        addmin_pass = 'locphat@6668'

        zl_user = 'zalo_' + zalo_id
        zl_pass = 'KSJDIJ%cjaij@%x14CzX'

        # for test - su dung tk zalo co san
        # zl_user = 'zalo_2492799013895845264'

        if is_local:
            db = 'test_salemate_clone'
            addmin_username = 'admin'
            addmin_pass = '123'

        # check co tk tren odoo chua
        user = request.env['res.users'].sudo().search(domain=[
            ['login', '=', zl_user]
        ])

        if not user:
            # dk
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, addmin_username, addmin_pass, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # create
            user_id = models.execute_kw(db, uid, addmin_pass, 'res.users', 'create', [
                {
                    'name': zalo_name,
                    'login': zl_user,
                    'password': zl_pass,
                    'company_ids': [1], 'company_id': 1,
                    'sel_groups_1_9_10': 10,
                    'state': 'new',
                    'is_zalo_account': True
                }])

            if not user_id or user_id <= 0:
                return result

            access_token = request.env["vtt.api.access_token"].find_or_create_token(user_id=user_id.id, create=True)

            p = models.execute_kw(db, uid, addmin_pass, 'res.users', 'read', [[user_id], ['partner_id']])

            # accc = akk[0]
            pId = p[0]['partner_id'][0]
            if pId > 0:
                models.execute_kw(db, uid, addmin_pass, 'res.partner', 'write', [[pId], {
                    'zalo_id': zalo_id,
                    'zalo_name': zalo_name,
                    'zalo_picture': zalo_avatar,
                }])

        # login
        try:
            res = request.session.authenticate(db, zl_user, zl_pass)
            user = request.env.user
            access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user.id, create=True)
            if access_token:
                access_token = access_token.replace('access_token_', '')

                return {
                    'success': True,
                    'message': 'Authenticated',
                    'access_token': access_token
                }

            return result
        except Exception as e:
            # if 'Access Denied' in e.args[0]:
            #     abc = 'ee'
            # session_info = request.env['ir.http'].session_info()
            return result

    @http.route('/api/zalo_auth_new', type='json', auth="none", methods=['POST'])
    def zalo_auth_new(self, zalo_access_token):
        result = {
            'success': False,
            'message': 'Authentication failed'
        }

        # check zalo access token and get info

        host_url = request.httprequest.host_url  # host_url ? root_url?
        # url = "http://localhost:8084"

        # get host url + db name
        start = host_url.index('://')
        first_sub = host_url[start + 3:]
        db_name = first_sub
        end = -1
        base_url = host_url
        try:
            end = first_sub.index('/')
        except ValueError:
            res = "Element not in list !"

        if end > 0:
            db_name = first_sub[:end]
            base_url = host_url[:start + 3 + end]

        is_local = False
        if 'localhost' in base_url:
            is_local = True

        # config connection - server
        url = base_url

        # admin
        db = 'test_salemate_clone_2024-04-25'
        addmin_username = 'admin'
        addmin_pass = 'locphat@6668'

        zl_user = 'zalo3' + str(random.random())

        # dk
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, addmin_username, addmin_pass, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # create
        user_id = models.execute_kw(db, uid, addmin_pass, 'res.users', 'create', [
            {
                'name': 'zalo_012',
                'login': zl_user,
                'password': '123',
                'company_ids': [1], 'company_id': 1,
                'sel_groups_1_9_10': 10,
                'state': 'new',
                'is_zalo_account': True
            }])

        if not user_id or user_id <= 0:
            return result

        # access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user_id, create=True)

        p = models.execute_kw(db, uid, addmin_pass, 'res.users', 'read', [[user_id], ['partner_id']])

        # accc = akk[0]
        pId = p[0]['partner_id'][0]
        if pId > 0:
            models.execute_kw(db, uid, addmin_pass, 'res.partner', 'write', [[pId], {
                'zalo_id': '111',
                'zalo_name': 'zalo_01',
                'zalo_picture': '2222',
            }])

        # login
        try:
            res = request.session.authenticate(db, zl_user, '123')
            user = request.env.user
            access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user.id, create=True)
            if access_token:
                access_token = access_token.replace('access_token_', '')

                return {
                    'success': True,
                    'message': 'Authenticated',
                    'access_token': access_token
                }

            return result
        except Exception as e:
            # if 'Access Denied' in e.args[0]:
            #     abc = 'ee'
            # session_info = request.env['ir.http'].session_info()
            return result


    @http.route('/api/zalo_auth_test', type='json', auth="none", methods=['POST'])
    def zalo_auth_test(self, zalo_access_token):
        result = {
            'success': False,
            'message': 'Authentication failed'
        }
        if zalo_access_token == 'Failed':
            return result

        aee = request.env.user

        # db = 'test_salemate'
        # db = 'test-salemate.victo.vn'
        db = 'test-salemate__2024-06-09'

        # login = 'admin'
        login = 'test'
        # password = 'locphat@6668'
        password = '123'
        if zalo_access_token == 'local':
            # db = 'test_salemate_clone_2024-06-09'
            login = 'admin'
            password = 'locphat@6668'

        if zalo_access_token == 'portal':
            db = 'test_salemate_clone'
            login = 'portal2'
            password = '123'

        if zalo_access_token == 'giap':
            # db = 'test_salemate_clone'
            login = 'zalo_2492799013895845264'
            password = 'KSJDIJ%cjaij@%x14CzX'

        if zalo_access_token == 'giap-local':
            # db = 'test_salemate_clone_2024-04-25'
            login = 'zalo_6263459577396773282'
            password = 'KSJDIJ%cjaij@%x14CzX'

        if zalo_access_token.startswith('zalo_'):
            login = zalo_access_token
            password = 'KSJDIJ%cjaij@%x14CzX'

        request.session.authenticate(db, login, password)

        user = request.env.user

        access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user.id, create=True)
        if access_token:
            access_token = access_token.replace('access_token_', '')

            return {
                'success': True,
                'message': 'Authenticated',
                'access_token': access_token
            }

        return result

    @http.route('/vtt/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)

    @http.route(['/vtt/image',
                 '/vtt/image/<string:xmlid>',
                 '/vtt/image/<string:xmlid>/<string:filename>',
                 '/vtt/image/<string:xmlid>/<int:width>x<int:height>',
                 '/vtt/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',

                 '/vtt/image/<string:model>/<int:id>',
                 '/vtt/image/<string:model>/<int:id>/<int:width>x<int:height>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>/<string:filename>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',

                 '/vtt/image/<int:id>',
                 '/vtt/image/<int:id>/<string:filename>',
                 '/vtt/image/<int:id>/<int:width>x<int:height>',
                 '/vtt/image/<int:id>/<int:width>x<int:height>/<string:filename>',
                 '/vtt/image/<int:id>-<string:unique>',
                 '/vtt/image/<int:id>-<string:unique>/<string:filename>',
                 '/vtt/image/<int:id>-<string:unique>/<int:width>x<int:height>',
                 '/vtt/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'], type='http',
                auth="public")
    def vtt_get_image(self, xmlid=None, model='', id=None, field='raw',
                      filename_field='name', filename=None, mimetype=None, unique=False,
                      download=False, width=0, height=0, crop=False, access_token=None,
                      nocache=False):

        field = 'image_1024'

        odoo_model = 'ir.attachment'
        allowed_models = {
            'news': '',
            'product': 'product.template',
            'user': 'res.partner',
            'company': 'res.company'
        }

        if model not in allowed_models:
            return 'Access denied'

        odoo_model = allowed_models[model]

        return self._content_image(xmlid, odoo_model, id, field, filename_field, filename, mimetype, unique, download,
                                   width, height, crop, access_token, nocache)

    @http.route([
        '/image/<string:model>/<int:id>',
        '/image/<string:model>/<int:id>/<string:field>', ], type='http',
        auth="public")
    def vtt_source_image(self, model='ir.attachment', id=None, field='image_1024'):
        odoo_model = 'ir.attachment'
        allowed_models = {
            'news': 'vtt.zalo.news',
            'product': 'product.template',
            'user': 'res.partner',
            'company': 'res.company',
            'coupon': 'loyalty.program',
            'category': 'zalo.product.category',
            'member_card': 'vtt.loyalty.tier',
        }

        if model not in allowed_models:
            return 'Access denied'

        if model == 'news' and field == 'image_1024':
            field = 'image'
        if model == 'company' and field == 'image_1024':
            field = 'bank_qr'
        if model == 'coupon' and field == 'image_1024':
            field = 'image'
        if model == 'category' and field == 'image_1024':
            field = 'image'
        if model == 'member_card' and field == 'image_1024':
            field = 'icon'

        odoo_model = allowed_models[model]

        return self._content_image(None, odoo_model, id, field)

    # lay image
    def _content_image(self, xmlid=None, model='', id=None, field='raw',
                       filename_field='name', filename=None, mimetype=None, unique=False,
                       download=False, width=0, height=0, crop=False, access_token=None,
                       nocache=False):

        try:
            record = request.env['ir.binary'].sudo()._find_record(xmlid, model, id and int(id), access_token)
            stream = request.env['ir.binary'].sudo()._get_image_stream_from(
                record, field, filename=filename, filename_field=filename_field,
                mimetype=mimetype, width=int(width), height=int(height), crop=crop,
            )
        except UserError as exc:
            if download:
                raise request.not_found() from exc
            # Use the ratio of the requested field_name instead of "raw"
            if (int(width), int(height)) == (0, 0):
                width, height = image_guess_size_from_field_name(field)
            record = request.env.ref('web.image_placeholder').sudo()
            stream = request.env['ir.binary'].sudo()._get_image_stream_from(
                record, 'raw', width=int(width), height=int(height), crop=crop,
            )

        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        res = stream.get_response(**send_file_kwargs)
        res.headers['Content-Security-Policy'] = "default-src 'none'"
        return res




    ###                 OLD















    @http.route('/vtt/api/authenticate', type='json', auth="none", methods=['POST'])
    def authenticate(self, db, login, password, base_location=None):
        user = request.env['res.users'].sudo().search_read(domain=[['login', '=', login]], fields=['name', 'state'],
                                                           limit=1)
        # print(user)

        if (user and user[0]['state'] == 'new'):
            # print(user[0]['state'])
            return {
                "error": {
                    "code": 200,
                    "message": "Odoo Server Error",
                    "data": {
                        "name": "vtt.exceptions.accountIsNotActive",
                        "debug": "",
                        "message": "Access Denied",
                        "arguments": [
                            "Access Denied"
                        ],
                        "context": {}
                    }
                }
            }

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