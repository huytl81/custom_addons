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

from odoo import SUPERUSER_ID

class ZaloAuthAPI(http.Controller):
    def _generate_hmac_sha256(self, data, secret_key):
        return hmac.new(secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()

    # ham goi zalo api để check access token + lấy profile user
    def __check_zalo_access_token(self, zalo_access_token, zalo_app_secret_key):
        header_appsecret_proof = self._generate_hmac_sha256(zalo_access_token, zalo_app_secret_key)

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
    #
    # @http.route('/api/zalo_autht', type='json', auth="none", methods=['POST'])
    # def zalo_autht(self):
    #     model = 'sale.order'
    #     obj = request.env[model].with_user(SUPERUSER_ID).sudo().browse(3)
    #     if obj:
    #         id = obj._create_invoices()
    #         if id:
    #             cc = obj.invoice_status
    #             id.message_post(body='from zalo')
    #             # bb = id.action_post()
    #             cc = ''
    #
    #     return True

    @http.route('/api/zalo_auth_auth', type='json', auth="none", methods=['POST'])
    def zalo_auth_auth(self, zalo_access_token, partner_id):
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

        if is_local:
            db_name = 'singchiak_2024-12-24'

        # config connection - server
        url = base_url
        db = db_name
        

        addmin_username = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_account_api_key')
        addmin_pass = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_auth_api_key')
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, addmin_username, addmin_pass, {})
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

        date = datetime.now()
        d = date.strftime("%Y-%m-%d %H:%M:%S")


        # create
        user_id = models.execute_kw(db, uid, addmin_pass, 'res.users', 'create', [
            {
                'name': 'zalo ' + d,
                'login': 'zalo_' + d,
                'password': 'aaaa',
                'company_ids': [1], 'company_id': 1,
                'partner_id': partner_id,
                'sel_groups_1_9_10': 10,
                'state': 'new',
                'is_zalo_account': True
            }])

        if not user_id or user_id <= 0:
            return 'result 0'

        p = models.execute_kw(db, uid, addmin_pass, 'res.users', 'read', [[user_id], ['partner_id']])

        # Ghi thong tin zalo profile cua nguoi dung vao thong tin partner
        pId = p[0]['partner_id'][0]
        if pId > 0:
            models.execute_kw(db, uid, addmin_pass, 'res.partner', 'write', [[pId], {
                'zalo_id': '' + d,
                'zalo_name': 'zalo_name',
                'zalo_picture': 'zalo_avatar',
            }])
        return ''

    # api zalo auth, phục vụ cho việc auth từ phía mini app
    @http.route('/api/zalo_auth', type='json', auth="none", methods=['POST'])
    def zalo_auth(self, zalo_access_token, id_by_oa=None, is_followed=False):
        result = {
            'success': False,
            'message': 'Authentication failed'
        }

        # check zalo access token and get info
        headers = request.httprequest.headers
        zalo_token = zalo_access_token
        # goi den zalo server de check access token va thong tin
        zalo_app_secret_key = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_secret_key')
        zalo_check = self.__check_zalo_access_token(zalo_token, zalo_app_secret_key)

        request.env['zalo.webhook.data'].sudo().create({
            'signature': 'zalo_auth',
            'data': json.dumps(zalo_check),
        })

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
        # get addmin username + pass (key)
        addmin_username = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_account_api_key')
        addmin_pass = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_auth_api_key')

        zl_user = 'zalo_' + zalo_id
        zl_pass = 'KSJDIJ%cjaij@%x14CzX'

        # test local phai khai bao dung thong tin db, admin user, pass
        if is_local:
            db = 'singchiak_2024-12-24'
            # addmin_username = 'admin'
            # addmin_pass = '183782e8ba001649b5455a120fe8e880bbcadcd5'
        

        # check co tk tren odoo chua
        user = request.env['res.users'].sudo().search(domain=[
            ['login', '=', zl_user]
        ])        

        access_token = ''

        if not user:
            user_vals = {
                'name': zalo_name,
                'login': zl_user,
                'password': zl_pass,
                'company_ids': [1], 'company_id': 1,
                'sel_groups_1_9_10': 10,
                'state': 'new',
                'is_zalo_account': True
            }
            # check trên partner
            if id_by_oa and id_by_oa != '':
                partner = request.env['res.partner'].sudo().search(domain=[
                    ['zalo_id_by_oa', '=', id_by_oa]
                ])
                if partner and partner.id > 0:
                    # cấp user cho partner --> Tạo user gắn partner id        
                    # Check            
                    # .............
                    user_vals['partner_id'] = partner.id
                


            # dk            
            common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, addmin_username, addmin_pass, {})
            models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))
            # create
            user_id = models.execute_kw(db, uid, addmin_pass, 'res.users', 'create', [user_vals])

            if not user_id or user_id <= 0:
                return result

            p = models.execute_kw(db, uid, addmin_pass, 'res.users', 'read', [[user_id], ['partner_id']])

            # Ghi thong tin zalo profile cua nguoi dung vao thong tin partner
            pId = p[0]['partner_id'][0]
            if pId > 0:
                models.execute_kw(db, uid, addmin_pass, 'res.partner', 'write', [[pId], {
                    'zalo_id': zalo_id,
                    'zalo_name': zalo_name,
                    'zalo_picture': zalo_avatar,
                }])

            # tao access token
            # access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user_id, create=True)     #OLD
            token_vals = request.env['vtt.api.access.token'].prepare_vals_to_create_token(user_id)
            token_id = models.execute_kw(db, uid, addmin_pass, 'vtt.api.access.token', 'create', [token_vals])
            token = models.execute_kw(db, uid, addmin_pass, 'vtt.api.access.token', 'read', [[token_id], ['token']])
            
            if token_id > 0 and token and len(token) > 0:
                access_token = token[0]['token']
        else:
            access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user.id, create=True)
        # login
        try:
            res = request.session.authenticate(db, zl_user, zl_pass)
            user = request.env.user

            # access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user.id, create=True)     # code OLD
            if access_token and access_token != '':
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

        zalo_token = 'YMdX7VPP7028QE4UyLyS1ebfvXZzGMKEwXN56UGhT4JFVTSJyabrPT03w2lsJa1kqmd8Dj9RHadABj9Utnny5TvZmchmFsXnudRb49mnNaY8KyOnaXOqMkWffX_3NHbVjp6q6PrT6t6QBuKwj74bVhmxhm6XNovyjMcSAfe807I4TgG-ZpqEI8DD_2wO0rfsfaxICBCQMtIHSiaiYmLpSxzWu32LL5bmbZYgBPPx3tIQKEaOiJnjMOmCm3UGPdnhinZnBfLfGq2e9CeVqLjlU_9fonBBLbTFyGJtFumxIbZvM-epq2v8AULHka-Q0WK9dd62OeHE27MnBQq9h1CCQwbHc0k-CJr7bmR62hjZMnIy1DXab3D-EsbD1iily44O2W'
        # goi den zalo server de check access token va thong tin
        zalo_app_secret_key = '4GWZIBC8RB7pWeRlWeIO'
        zalo_check = self.__check_zalo_access_token(zalo_token, zalo_app_secret_key)

        if 'error' not in zalo_check or zalo_check['error'] > 0:
            result['error_code'] = zalo_check['error']
            result['message'] = zalo_check['message']    

        zalo_id = zalo_check['id']
        zalo_name = zalo_check['name']
        zalo_avatar = ''
        # LUC NAO TEST THI LAI MO LAI CODE

        # if zalo_access_token == 'Failed':
        #     return result
        #
        # json = request.httprequest.json
        #
        # params = json.get('params')
        # aee = request.env.user
        #
        # host_url = request.httprequest.host_url  # host_url ? root_url?
        # # url = "http://localhost:8084"
        #
        # # get host url + db name
        # start = host_url.index('://')
        # first_sub = host_url[start + 3:]
        # db_name = first_sub
        # end = -1
        # base_url = host_url
        # try:
        #     end = first_sub.index('/')
        # except ValueError:
        #     res = "Element not in list !"
        #
        # if end > 0:
        #     db_name = first_sub[:end]
        #     base_url = host_url[:start + 3 + end]
        #
        # login = 'test'
        # password = '123'
        #
        # aaa = params.get('login', '')
        # bbb = params.get('pass', '')
        #
        # if aaa != '':
        #     login = params.get('login')
        # if bbb != '':
        #     password = params.get('pass')
        #
        # is_local = False
        # if 'localhost' in base_url:
        #     is_local = True
        #     db_name = params.get('db')
        #
        # if zalo_access_token.startswith('zalo_'):
        #     login = zalo_access_token
        #     password = 'KSJDIJ%cjaij@%x14CzX'
        #
        # request.session.authenticate(db_name, login, password)
        #
        # user = request.env.user
        #
        # access_token = request.env["vtt.api.access.token"].find_or_create_token(user_id=user.id, create=True)
        # if access_token:
        #     access_token = access_token.replace('access_token_', '')
        #
        #     return {
        #         'success': True,
        #         'message': 'Authenticated',
        #         'access_token': access_token
        #     }

        return result



