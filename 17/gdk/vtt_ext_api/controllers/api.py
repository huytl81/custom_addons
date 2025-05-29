# -*- coding: utf-8 -*-
import functools
import hashlib
import hmac
import logging

import requests

from odoo import http
from odoo.http import request


import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import json


import base64
import xmlrpc.client as xmlrpclib

from datetime import date, datetime

_logger = logging.getLogger(__name__)

PAYMENT_METHOD = [
    'cod', 'bank', 'vnpay',
    'cod_sandbox', 'bank_sandbox', 'vnpay_sandbox'
]

def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        access_token = request.httprequest.headers.get("X-Openerp-Session-Id")
        if not access_token:
            return {
                'success': False,
                'message': 'missing access token in request header'
            }
        access_token = 'access_token_' + access_token
        access_token_data = request.env["vtt.api.access.token"].sudo().search([("token", "=", access_token)],
                                                                              order="id DESC", limit=1)

        if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return {
                'success': False,
                'message': 'access token invalid or expired'
            }
        request.update_env(user=access_token_data.user_id)
        u = request.env.user
        # request.session.uid = access_token_data.user_id.id
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap


class VttAPI(http.Controller):
    def generate_mac(sellf, params, private_key, auto_sort=True):
        """
        Hàm tạo mã xác thực (MAC) sử dụng HMAC SHA256 từ dữ liệu và khóa bí mật.

        Args:
          params: Dict chứa dữ liệu cần tạo MAC.
          private_key: Khóa bí mật dạng chuỗi.

        Returns:
          Mã xác thực MAC dạng chuỗi.
        """

        # Sắp xếp key của params theo thứ tự từ điển tăng dần
        keys = params.keys()
        if auto_sort:
            keys = sorted(params.keys())

        # Tạo mảng data dạng [{key=value}, ...]
        data_array = []
        for key in keys:
            value = params[key]
            if isinstance(value, dict):
                value = json.dumps(value)
            data_array.append(f"{key}={value}")

        # Chuyển đổi data_array về dạng string
        data_string = "&".join(data_array)
        # data_string = data_string.replace('\'', '"')

        # Tạo mã xác thực MAC
        mac = hmac.new(private_key.encode("utf-8"), data_string.encode(), digestmod=hashlib.sha256).hexdigest()

        return mac
        # return {
        #     'string': data_string,
        #     'mac': mac
        # }

    def _get_zalo_utm_source(self):
        id = -1

        obj = request.env['utm.source'].sudo().search(domain=[
            ['name', '=', 'Zalo']
        ])
        if obj:
            id = obj.id
        else:
            source = request.env['utm.source'].sudo().create({
                'name': 'Zalo'
            })
            if source:
                id = source.id

        return id

    # return raw json data, ko bi boc vao json_rpc nua
    #
    @http.route('/api/miniapp/sb_callback', type='http', auth='public', methods=['POST'], csrf=False)
    def zalo_mini_app_callback(self):
        # abc = request
        params = request.httprequest.json

        result = {
            'returnCode': 1,
            'returnMessage': 'Thành công'
        }

        order_21 = request.env['sale.order'].sudo().browse(10)

        data = params.get('data', None)
        mac = params.get('mac', '')
        overallMac = params.get('overallMac', '')
        key = '3238e5115d4525fffe4e0a810d1fed0b'

        order_21.write({'note': json.dumps(data)})

        #
        response_data = {
            "data": {
                "amount": 100000,
                "method": "VNPAY_SANDBOX",
                "orderId": "1247119728271001068310574_1718783821211",
                "transId": "240619_1457012111490300220139602768262",
                "appId": "1007171034541595268",
                "extradata": "%7B%22storeName%22%3A%22C%E1%BB%ADa%20h%C3%A0ng%20A%22%2C%22storeId%22%3A%22123%22%2C%22orderGroupId%22%3A%22345%22%2C%22myTransactionId%22%3A%2212345678%22%2C%22notes%22%3A%22%C4%90%C3%A2y%20l%C3%A0%20gi%C3%A1%20tr%E1%BB%8B%20g%E1%BB%ADi%20th%C3%AAm%22%7D",
                "resultCode": 1,
                "description": "Thanh%20to%C3%A1n%20h%C3%B3a%20%C4%91%C6%A1n%20%C4%91i%E1%BB%87n%20n%C6%B0%E1%BB%9Bc",
                "message": "Giao d\u1ecbch th\u00e0nh c\u00f4ng",
                "paymentChannel": "VNPAY_SANDBOX"
            },
            "overallMac": "eac4616e0fbd822b0aa8c61e96ecee9917e8645300c690ffc38aadc4a41f6293",
            "mac": "3b2e54b68391b0db3c63e7eafa4119b2c4ac071df6cb324666a83dab69d1e81b"
        }

        if data and mac and overallMac:
            payment_order_id = data['orderId']
            trans_id = data['transId']

            if not payment_order_id:
                result['returnCode'] = -1
                result['returnMessage'] = 'Không tìm thấy payment order hoặc trans liên quan'
                return request.make_json_response(result)

            check_trans = request.env['zalo.payment.transaction'].sudo().search(domain=[
                ['trans_id', '=', trans_id]
            ], limit=1)

            # check kt trans đã tồn tại chưa
            if check_trans:
                result['returnCode'] = 2
                result['returnMessage'] = 'Trans đã tồn tại'
                return request.make_json_response(result)

            trans = request.env['zalo.payment.transaction'].sudo().search(domain=[
                ['payment_order_id', '=', payment_order_id]
            ], limit=1)

            if not trans:
                result['returnCode'] = -1
                result['returnMessage'] = 'Không tìm thấy payment order hoặc trans liên quan'
                return request.make_json_response(result)

            if trans.order_id.id < 1:
                result['returnCode'] = -1
                result['returnMessage'] = 'Đơn hàng ko tồn tại'
                # result['data'] = params
                return request.make_json_response(result)


            order = request.env['sale.order'].sudo().browse(trans.order_id.id)
            # order = request.env['sale.order'].sudo().search(domain=[
            #     ['id', '=', trans.order_id]
            # ], limit=1)

            if not order or order.id < 1:
                result['returnCode'] = -1
                result['returnMessage'] = 'Đơn hàng ko tồn tại'
                # result['data'] = params
                # order_21.write({'note': json.dumps(result)})
                return request.make_json_response(result)

            appId = data['appId']
            amount = data['amount']
            description = data['description']
            message = data['message']
            resultCode = data['resultCode']
            transId = data['transId']
            method = data['method']
            extra_data = data['extradata']
            payment_channel = data['paymentChannel']

            # prepare to check mac
            data_for_mac = {
                'appId': appId,
                'amount': amount,
                'description': description,
                'orderId': payment_order_id,
                'message': message,
                'resultCode': resultCode,   # 1 | -1
                'transId': transId,
            }

            req_mac = self.generate_mac(data_for_mac, key, False)

            if req_mac != mac:
                result['returnCode'] = -1
                result['returnMessage'] = 'Mac không hợp lệ'
                # result['data'] = params
                # order_21.write({'note': json.dumps(result)})
                return request.make_json_response(result)

            # prepare to check overall mac
            req_overall_mac = self.generate_mac(data, key)

            if req_overall_mac != overallMac:
                result['returnCode'] = -1
                result['returnMessage'] = 'OveralMac không hợp lệ'
                # result['data'] = params
                # order_21.write({'note': json.dumps(result)})
                return request.make_json_response(result)

            success = trans.write({
                'amount': amount,
                'method': method,
                'trans_id': transId,
                'app_id': appId,
                'extra_data': extra_data,
                'result_code': resultCode,
                'message': message,
                'payment_channel': payment_channel,
                'mac': mac,
                'overall_mac': overallMac,
            })

            if success:
                result['returnCode'] = 1
                result['returnMessage'] = 'Thành công'

                # result['data'] = params
            #     order_21.write({'note': json.dumps(result)})

                # ghi nhan vao order
                order.write({
                    'zalo_payment_state': 'paid'
                })
        #
        # data = response_data['data']
        # mac = response_data['mac']
        # overallMac = response_data['overallMac']
        #
        # data_for_mac = 'appID=' + data['appId'] + '&amount=' + str(data['amount']) + '&description=' + data['description'] + '&orderId=' + data['orderId'] + '&message=' + data['message'] + '&resultCode=' + data['resultCode'] + '&transId=' + data['transId']
        #
        #
        # abc = '"appId={appId}&amount={amount}&description={description}&orderId={orderId}&message={message}&resultCode={resultCode}&transId={transId}";'
        #
        # message = 'abbb'
        # usc = {
        #     'abc': 1,
        #     'clean': 'asdkoas'
        # }
        # message = json.dumps(params)
        #
        # mail_channel = request.env['discuss.channel'].sudo().browse(2)
        # mail_channel.message_post(body=message)

        return request.make_json_response(result)

    @http.route('/api/zalopay/create_order', type='json', auth='public', methods=['POST'])
    def zalopay_create_order(self):
        # get order info
        # create mac
        # return data + mac

        item = [
            {'id': 1, 'amount': 21000},
            {'id': 2, 'amount': 30000},
        ]

        data = {
            'desc': 'Thanh toan hd ABC',
            'amount': 51000,
            'method': json.dumps({
                'id': 'VNPAY_SANDBOX',
                'isCustom': False,
            }),
            'item': item,
        }

        key = '035a840017179d4217fe59017367c8be'
        mac = self.generate_mac(data, '035a840017179d4217fe59017367c8be')


        mac_string = 'amount=51000&desc=Thanh toan hd ABC&item=[{"id":1,"amount":21000},{"id":2,"amount":30000}]&method={"id":"VNPAY_SANDBOX","isCustom":false}'
        mac2 = hmac.new(key.encode(), mac_string.encode(), digestmod=hashlib.sha256).hexdigest()

        result = {
            'data': data,
            'item': item,
            'mac': mac,
            'mac2': mac2
        }
        return result


        # order = request.env['sale.order'].sudo().search(domain=[
        #     ['id', '=', 6]
        # ], limit=1)
        #
        # key = '035a840017179d4217fe59017367c8be'
        # mes = 'amount=50500&desc="\"Thanh toán 50.000 as\""&extradata="{ // toàn bộ extradata sẽ được truyền qua embedData (ZaloPay) hoặc extraData (MoMo)\n    storeName: \"Cửa hàng A\", // field này sẽ được truyền trực tiếp qua storeName (MoMo)\n    storeId: \"123\", // field này sẽ được truyền trực tiếp qua storeId (MoMo)\n    orderGroupId: \"345\" // field này sẽ được truyền trực tiếp qua orderGroupId (MoMo)\n    myTransactionId: \"12345678\", // transaction id riêng của hệ thống của bạn\n    notes: \"Đây là giá trị gửi thêm\",\n  }"&item="[\n    { id: \"1\", amount: 20000 },\n    { id: \"2\", amount: 30000 },\n  ]"&method="{\n    id: \"ZALOPAY_SANDBOX\", // Phương thức thanh toán\n    isCustom: false, // false: Phương thức thanh toán của Platform, true: Phương thức thanh toán riêng của đối tác\n  }"'
        #
        # response_data = {
        #     "data": {
        #         "amount": 100000,
        #         "method": "VNPAY_SANDBOX",
        #         "orderId": "1247119728271001068310574_1718783821211",
        #         "transId": "240619_1457012111490300220139602768262",
        #         "appId": "1007171034541595268",
        #         "extradata": "%7B%22storeName%22%3A%22C%E1%BB%ADa%20h%C3%A0ng%20A%22%2C%22storeId%22%3A%22123%22%2C%22orderGroupId%22%3A%22345%22%2C%22myTransactionId%22%3A%2212345678%22%2C%22notes%22%3A%22%C4%90%C3%A2y%20l%C3%A0%20gi%C3%A1%20tr%E1%BB%8B%20g%E1%BB%ADi%20th%C3%AAm%22%7D",
        #         "resultCode": 1,
        #         "description": "Thanh%20to%C3%A1n%20h%C3%B3a%20%C4%91%C6%A1n%20%C4%91i%E1%BB%87n%20n%C6%B0%E1%BB%9Bc",
        #         "message": "Giao d\u1ecbch th\u00e0nh c\u00f4ng",
        #         "paymentChannel": "VNPAY_SANDBOX"
        #     },
        #     "overallMac": "eac4616e0fbd822b0aa8c61e96ecee9917e8645300c690ffc38aadc4a41f6293",
        #     "mac": "3b2e54b68391b0db3c63e7eafa4119b2c4ac071df6cb324666a83dab69d1e81b"
        # }
        #
        # data = response_data['data']
        # mac = response_data['mac']
        # overallMac = response_data['overallMac']
        #
        # data_for_mac = 'appID=' + data['appId'] + '&amount=' + str(data['amount']) + '&description=' + data[
        #     'description'] + '&orderId=' + data['orderId'] + '&message=' + data['message'] + '&resultCode=' + str(data[
        #                    'resultCode']) + '&transId=' + data['transId']
        #
        # mes = data_for_mac
        #
        # mac = hmac.new(
        #     key.encode("UTF-8"),
        #     msg=mes.encode(),
        #     digestmod=hashlib.sha256
        # ).hexdigest().upper()
        #
        # mac1 = hmac.new(
        #     key.encode("UTF-8"),
        #     msg=mes.encode(),
        #     digestmod=hashlib.sha256
        # ).hexdigest()
        #
        # abc = '123'


        # return {
        #     'mac': mac,
        #     'mac1': mac1
        # }

    # Get Company info
    @http.route('/api/company/info', type='json', auth="public", methods=['POST'])
    def company_info(self):
        model = 'res.company'

        com = request.env[model].sudo().browse(1)

        if com:
            return {
                'company_name': com.name,
                'phone': '' if com.phone == False else com.phone,
                'address': '' if com.street == False else com.street,
                'app_qr': '/image/company/1/zalo_app_qr',
                'bank_qr': '/image/company/1/bank_qr',
                'link': '' if com.zalo_app_link == False else com.zalo_app_link,
            }
        return {
            'success': False,
            'message': 'Không có thông tin công ty'
        }


    ### Personal Info
    # Update Personal Info
    @validate_token
    @http.route('/api/user/update_info', type='json', auth="none", methods=['POST'])
    def user_update_info(self):
        # abc = request
        model = 'res.partner'
        params = request.params

        # httprequest = request.httprequest
        # current_access_token = httprequest.environ.get('HTTP_X_OPENERP_SESSION_ID')
        #
        # token_obj = request.env['vtt.access.token'].sudo().search(domain=[['access_token', '=', current_access_token]])
        # if token_obj:
        #     id = token_obj[0].partner_id

        user = request.env.user     # code lay user khi chay that
        # lam tam
        # user = request.env['res.users'].sudo().search(domain=[['login', '=', 'test']])

        input = {}

        if user:
            id = user.partner_id.id
            params['id'] = id
            input['id'] = id

        if id <= 0:
            return {
                'success': False,
                'message': 'Cập nhật không thành công! Id ko tồn tại'
            }

        name = params.get('name', False)
        phone = params.get('phone', False)
        email = params.get('email', False)
        birth_day = params.get('birth_day', False)
        sex = params.get('sex', False)

        if name != False and name != '':
            input['name'] = name
        if phone != False and phone != '':
            input['phone'] = phone
        if email != False and type(email) == str:
            if (email.endswith('@gmail.com') or email.endswith('@yahoo.com') or
                               email.endswith('@yahoo.com.vn') or email.endswith('@outlook.com') or email.endswith('@outlook.com.vn') or
                               ('@' in email and email.endswith('.vn')) or ('@' in email and email.endswith('.com'))
                                ):
                input['email'] = email
            else:
                return {
                    'success': False,
                    'message': 'Email nhập vào không hợp lệ'
                }
        if email == None or (type(email) == str and email.strip() == '') or email == False:
            input['email'] = None

        if birth_day != False:
            try:
                date.fromisoformat(birth_day) # loi
                input['birth_day'] = birth_day
            except ValueError:
                return {
                    'success': False,
                    'message': 'Ngày sinh nhập vào không hợp lệ'
                }
        if sex != False:
            if sex not in ['male', 'female']:
                return {
                    'success': False,
                    'message': 'Giới tính nhập vào không hợp lệ'
                }
            input['sex'] = sex

        obj = request.env[model].sudo().browse(id)

        if obj:
            record = obj.write(input)      #true / false
            if record == False:
                return {
                    'success': False,
                    'message': 'Cập nhật không thành công!'
                }

        return {
            'success': True,
            'message': 'Cập nhật thành công'
        }



    # Get User profile
    @validate_token
    @http.route('/api/user/profile', type='json', auth="none", methods=['POST'])
    def user_profile(self):
        model = 'res.partner'

        params = request.params

        user = request.env.user     # code lay user hien tai khi chay that

        if not user:
            return {
                'success': False,
                'message': 'Người dùng không tồn tại'
            }
        # for o in p.sale_order_ids:
        #     abc = ''
        #     cc = ''
        # tam khi chua co auth
        # user = request.env['res.users'].sudo().search(domain=[['login', '=', 'test']])
        if user:
            id = user.partner_id.id
            params['id'] = id


        if id <= 0:
            return None

        pId = user.partner_id

        count = request.env[model].sudo().search_count(domain=[['id', '=', id]])
        if count <= 0:
            return None

        obj = request.env[model].sudo().browse(id)
        # lvl, required_point, description, name

        # points, code, expiration_date, use_count, order_id
        # lich su load theo hoa don


        if obj and obj.id > 0:
            result = {
                # 'id': obj.id,
                'name': obj.name,
                'phone': '' if obj.phone == False else obj.phone,
                'email': '' if obj.email == False else obj.email,
                'birth_day': '' if obj.birth_day == False else obj.birth_day,
                'sex': 'male' if obj.sex == False else obj.sex,
                'image': '' if obj.zalo_picture == False else obj.zalo_picture,
            }

            # load loyalty info

            loyalty = request.env['loyalty.program'].sudo().search(domain=[
                '&',
                ['program_type', '=', 'loyalty'],
                ['is_zalo_loyalty_program', '=', True]
            ], limit=1)

            if loyalty:
                loyalty_info = {
                    'card_level': -1,
                    'card_name': '--------',
                    # 'card_level': program.level,
                    'description': '',
                    # 'code': max_point_card.code,
                    'current_points': 0,
                    'level_points': 0,
                    'next_level_points': 0,
                    'color': '#83e7c0',
                }

                # get default tier (tier dau tien)
                if loyalty.loyalty_tier_ids and len(loyalty.loyalty_tier_ids) > 0:
                    card_tier = loyalty.loyalty_tier_ids[0]
                    loyalty_info = {
                        'card_level': card_tier.level,
                        'card_name': card_tier.name,
                        'description': '' if card_tier.description == False else card_tier.description,
                        'current_points': 0,     #so du
                        'level_points': 0,
                        'next_level_points': card_tier.range_max,
                        'color': card_tier.color,
                    }

                card = request.env['loyalty.card'].sudo().search(domain=[
                    '&',
                    ['partner_id', '=', obj.id],
                    # '&',
                    ['program_id', '=', loyalty.id]
                ], limit=1)

                # if loyalty.loyalty_tier_ids and len(loyalty.loyalty_tier_ids) > 0:
                if card and card.id > 0 and card.tier_id and card.tier_id.id > 0:
                    card_tier = card.tier_id

                    nxt_lvl_name = '---'
                    if card_tier.next_level_id > 0:
                        next_tier = request.env['vtt.loyalty.tier'].sudo().browse(card_tier.next_level_id)
                        if next_tier:
                            nxt_lvl_name = next_tier.name

                    loyalty_info = {
                        'card_level': card_tier.level,
                        'card_name': card_tier.name,
                        'description': '' if card_tier.description == False else card_tier.description,
                        'current_points': card.points,     #so du
                        'level_points': card.level_points,
                        'next_level_points': card_tier.range_max,
                        'next_level_name': nxt_lvl_name,
                        'color': card_tier.color,
                        # 'icon': '/image/member_card/' + str(card_tier.id),
                    }
                result['loyalty_info'] = loyalty_info

            return result

        return None

    @http.route('/api/news/page/<int:page>', type='json', auth="public", methods=['POST'])
    def news_list(self, page=1):
        model = 'vtt.zalo.news'
        domain = []
        limit = 10
        offset = 0 if page <= 1 else (page -1) * limit
        result = []

        params = request.httprequest.json
        filter_by_name = ''
        if params:
            filter_by_name = params.get('filter_by_name', '')
            is_hot_news = params.get('is_hot_news', False)

        if filter_by_name != '':
            if is_hot_news:
                domain = [
                    '&',
                    ['title', 'ilike', filter_by_name],
                    ['is_hot_news', '=', True],
                ]
            else:
                domain = [
                    ['title', 'ilike', filter_by_name]
                ]
        else:
            if is_hot_news:
                domain = [
                    ['is_hot_news', '=', True]
                ]

        items = request.env[model].sudo().search(domain=domain, limit=limit,
                                                 offset=offset,order='publish_date desc')

        for item in items:
            obj = {
                'id': item.id,
                'name': '' if item.title == False else item.title,
                'description': '' if item.description == False else item.description,
                'public_link': '' if item.public_link == False else item.public_link,
                'publish_date': '' if item.publish_date == False else item.publish_date,
                'is_hot_news': item.is_hot_news,
                'author': '' if item.author == False else item.author,
                'image': '/image/news/' + str(item.id),
            }
            result.append(obj)

        return result
    #
    @http.route('/api/news/<int:id>', type='json', auth="public", methods=['POST'])
    def news_get(self, id, **kwargs):
        model = 'vtt.zalo.news'

        if id <= 0:
            return None
        count = request.env[model].sudo().search_count(domain=[['id', '=', id]])
        if count <= 0:
            return None

        obj = request.env[model].sudo().browse(id)
        if obj and obj.id > 0:
            result = {
                'id': obj.id,
                'name': '' if obj.title == False else obj.title,
                'description': '' if obj.description == False else obj.description,
                'public_link': '' if obj.public_link == False else obj.public_link,
                'publish_date': '' if obj.publish_date == False else obj.publish_date,
                'is_hot_news': obj.is_hot_news,
                'author': '' if obj.author == False else obj.author,
                'image': '/image/news/' + str(obj.id),
                # 'image': obj.image_512

            }
            return result

        return None


    # Product category

    @http.route('/api/product_category', type='json', auth="public", methods=['POST'])
    def product_category_list(self):
        model = 'zalo.product.category'
        domain = [
            # ['show_on_zalo', '=', True]
        ]
        limit = 10
        offset = 0
        result = []

        items = request.env[model].sudo().search(domain=domain, order='sequence ASC')

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'sequence': item.sequence,
                'image': '/image/category/' + str(item.id),
            }
            result.append(obj)

        return result

    # List product
    @http.route([
        '/api/product/page/<int:page>',
        '/api/product/page/<int:page>-<int:categ_id>'
        ]
        , type='json', auth="public", methods=['POST'])
    def product_list(self, page=1, categ_id=-1):
        model = 'product.template'

        params = request.httprequest.json
        filter_product_name = ''
        if params:
            filter_product_name = params.get('filter_by_name', '')

        domain = [
            '&',
            ['sale_ok', '=', True],
            ['zalo_categ_ids', '!=', False]
        ]

        if categ_id > 0:
            domain = [
                '&',
                ['sale_ok', '=', True],
                ['zalo_categ_ids', 'in', [categ_id]]
            ]

        if filter_product_name != '':
            if categ_id > 0:
                domain = [
                    '&',
                    ['sale_ok', '=', True],
                    '&',
                    ['zalo_categ_ids', 'in', [categ_id]],
                    ['name', 'ilike', filter_product_name],
                ]
            else:
                domain = [
                    '&',
                    ['sale_ok', '=', True],
                    '&',
                    ['zalo_categ_ids', '!=', False],
                    ['name', 'ilike', filter_product_name],
                ]

        limit = 10
        offset = 0 if page <= 1 else (page - 1) * limit
        result = []

        # fields = ['name', 'list_price', 'categ_id', 'description_sale']
        items = request.env[model].sudo().search(domain=domain, limit=limit,
                                                                           offset=offset)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'list_price': item.list_price,
                'description': '' if item.description_sale == False else item.description_sale,
                'image': '/image/product/' + str(item.id),
                'categ_id': categ_id
            }
            result.append(obj)

        return result

    # List product
    @http.route('/api/product/best_seller' , type='json', auth="public", methods=['POST'])
    def product_best_seller(self):
        model = 'product.template'

        domain = [
            '&',
            ['sale_ok', '=', True],
            ['zalo_categ_ids', '!=', False]
        ]

        limit = 5
        offset = 0
        result = []

        items = request.env[model].sudo().search(domain=domain, limit=limit, offset=offset)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'list_price': item.list_price,
                'description': '' if item.description_sale == False else item.description_sale,
                'image': '/image/product/' + str(item.id),
                'categ_id': item.categ_id.id
            }
            result.append(obj)

        return result

    # Get Product
    @http.route('/api/product/<int:id>', type='json', auth="public", methods=['POST'])
    def product_get(self, id):
        model = 'product.template'

        if id <= 0:
            return None

        count = request.env[model].sudo().search_count(domain=[['id', '=', id]])
        if count <= 0:
            return None

        obj = request.env[model].sudo().browse(id)
        if obj and obj.id > 0:
            # result = obj.read(fields=fields)[0]
            # r = obj.read()[0]
            # categ_obj = request.env['product.category'].sudo().browse(obj.categ_id.id).read()[0]
            result = {
                'id': obj.id,
                'name': obj.name,
                'description': obj.description_sale,
                'list_price': obj.list_price,
                'categ_id': obj.categ_id.id,
                'image': '/image/product/' + str(obj.id),
                # 'image': obj.image_512

            }

            return result

        return None

    # def _get_

    # Create Sale order
    @validate_token
    @http.route('/api/sale_order/create', type='json', auth="none", methods=['POST'])
    def sale_order_create(self):
        model = 'sale.order'
        params = request.params

        result = {
            'success': False,
            'message': 'Đặt hàng ko thành công'
        }

        user = request.env.user
        if not user:
            return result

        pId = user.partner_id.id

        if not params or not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        items = params.get('order_line', [])

        if len(items) < 1:
            result['message'] = 'Bạn chưa đặt hàng'
            return result

        order_line = []
        for item in items:
            pObj = request.env['product.product'].sudo().search(domain=[
                ['product_tmpl_id', '=', item['product_id']]
            ], limit=1)
            if pObj:
                product_id = pObj.id
                order_line.append((
                    0, 0, {
                        'product_id': product_id,
                        'product_uom_qty': item['qty']
                    }
                ))
        if len(order_line) < 1:
            return result

        input = {
            'partner_id': pId,
            'order_line': order_line,
            'shipping_method': 'delivery',
            'payment_method': 'cod',
            'note': params.get('note', ''),
            'is_online_order': True,
        }

        zalo_source_id = self._get_zalo_utm_source()
        if zalo_source_id > 0:
            input['source_id'] = zalo_source_id

        address_list = request.env['res.partner'].search(domain=[
            ['parent_id', '=', pId]
        ])

        if address_list and len(address_list) > 0:
            default_address = address_list[0]
            if len(address_list) > 1:
                for address in address_list:
                    if address.is_default_address == True:
                        default_address = address
            input['delivery_address_id'] = default_address.id


        obj = request.env[model].sudo().create(input)

        if obj:
            # calc and apply loyalty program
            discount_product = obj.company_id.sale_discount_product_id

            # return {
            #     'success': True,
            #     'message': 'Đặt hàng thành công',
            #     'dis': discount_product.id
            # }

            loyalty_cards = request.env['loyalty.card'].sudo().search(domain=[
                '&',
                ['partner_id', '=', pId],
                ['program_type', '=', 'loyalty']
            ])

            # return {
            #     'success': True,
            #     'message': 'Đặt hàng thành công',
            #     'dis': discount_product.id,
            #     'cards': json.dumps(loyalty_cards)
            # }

            if loyalty_cards and len(loyalty_cards) > 0:
                cards = []
                for c in loyalty_cards:
                    if c.program_id.auto_apply == True and c.program_id.loyalty_tier_ids and len(c.program_id.loyalty_tier_ids) > 0:
                        cards.append(c)

                for card in cards:
                    if card.tier_id and card.tier_id.tier_reward_ids and len(card.tier_id.tier_reward_ids) > 0:
                        for reward in card.tier_id.tier_reward_ids:
                            if reward.value > 0 and reward.value_type:
                                amount = reward.value
                                if reward.value_type == 'percent':
                                    amount = obj.amount_total / 100 * reward.value
                                vals = {
                                    'order_id': obj.id,
                                    'product_id': discount_product.id,
                                    'name': 'Giam gia ' if reward.name == False else reward.name, # lay ten tu reward
                                    'sequence': 999,
                                    'price_unit': -amount, # tinh tu cong thuc
                                    'coupon_id': card.id,
                                    'is_reward_line': True,
                                    'is_loyalty_member_reward': True, # phuc vu cho phan backend
                                    'is_percent_value': reward.value_type == 'percent',
                                    'loyalty_member_reward_value': reward.value,
                                    # 'tax_id': [Command.set(taxes.ids)],
                                }
                                request.env['sale.order.line'].sudo().create(vals)
            return {
                'success': True,
                'message': 'Đặt hàng thành công',
                'id': obj.id
            }

        return result

    # Create Sale order
    @validate_token
    @http.route('/api/sale_order/create_old', type='json', auth="none", methods=['POST'])
    def sale_order_create_old(self):
        model = 'sale.order'
        params = request.params

        result = {
            'success': False,
            'message': 'Đặt hàng ko thành công'
        }

        user = request.env.user
        if not user:
            return result

        pId = user.partner_id.id

        if not params or not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        items = params.get('order_line', [])

        if len(items) < 1:
            result['message'] = 'Bạn chưa đặt hàng'
            return result

        order_line = []
        for item in items:
            pObj = request.env['product.product'].sudo().search(domain=[
                ['product_tmpl_id', '=', item['product_id']]
            ])
            if pObj:
                product_id = pObj[0].id
                order_line.append((
                    0,0, {
                        'product_id': product_id,
                        'product_uom_qty': item['qty']
                    }
                ))
        if len(order_line) < 1:
            return result

        input = {
            'partner_id': pId,
            'order_line': order_line,
            'shipping_method': 'delivery',
            'payment_method': 'cod',
            'note': params.get('note', ''),
        }

        zalo_source_id = self._get_zalo_utm_source()
        if zalo_source_id > 0:
            input['source_id'] = zalo_source_id

        address_list = request.env['res.partner'].search(domain=[
            ['parent_id', '=', pId]
        ])

        if address_list and len(address_list) > 0:
            default_address = address_list[0]
            if len(address_list) > 1:
                for address in address_list:
                    if address.is_default_address == True:
                        default_address = address
            input['delivery_address_id'] = default_address.id

        # CHO PHAN UPDATE
        # delivery_id = params.get('delivery_address_id', -1)
        # shipping_method = params.get('shipping_method', False)
        # payment_method = params.get('payment_method', False)

        # if shipping_method == False or shipping_method not in ['delivery', 'go_to_shop']:
        #     result['message'] = 'Phương thức vận chuyển không hợp lệ'
        #     return result
        # if shipping_method == 'delivery':
        #     if delivery_id <= 0:
        #         result['message'] = 'Địa chỉ giao hàng không hợp lệ'
        #         return result
        #     input['shipping_method'] = shipping_method
        #     input['delivery_address_id'] = delivery_id
        # if payment_method == False or payment_method not in ['cod, bank_transfer']:
        #     result['message'] = 'Phương thức thanh toán không hợp lệ'
        #     return result

        obj = request.env[model].sudo().create(input)

        if obj:
            # calc and apply loyalty program
            loyalty_cards = request.env['loyalty.card'].sudo().search(domain=[
                '&',
                ['partner_id', '=', pId],
                ['program_type', '=', 'loyalty']
            ])

            customer_card_ids = []      # de phuc vu lay coupon id de apply vao sale order
            if loyalty_cards and len(loyalty_cards) > 0:
                max_point_card = loyalty_cards[0]
                if len(loyalty_cards) > 1:
                    for card in loyalty_cards:
                        if max_point_card.points < card.points:
                            max_point_card = card
                        customer_card_ids.append(card.id)

                # loyalty
                loyalty_programs = request.env['loyalty.program'].sudo().search(domain=[
                    ['program_type', '=', 'loyalty'],
                ])

                if loyalty_programs and len(loyalty_programs) > 0:
                    program = loyalty_programs[0]
                    current_point = 0
                    if len(loyalty_programs) > 1:
                        for p in loyalty_programs:
                            if max_point_card.points >= p.required_points and current_point <= p.required_points:
                                program = p
                                current_point = program.required_points

                    if program.reward_ids and len(program.reward_ids):
                        for reward in program.reward_ids:
                            if program.coupon_ids and len(program.coupon_ids) > 0:
                                # abc = program.coupon_ids[card.id]
                                for card in loyalty_cards:
                                    if card.id in program.coupon_ids.ids:
                                        obj._update_programs_and_rewards()      # ban dau sale order se chua load cac coupon co the ap dung nen phai goi de load trc
                                        obj._apply_program_reward(reward, card) # __ME: reward_id (from program), coupon = card
                                        obj._update_programs_and_rewards()

                        # code_reward = request.env['loyalty.reward'].sudo().browse(10)
                        # code_coupon = request.env['loyalty.card'].sudo().browse(27)
                        # #
                        # # # chuyen code nay de lam api apply ma giam gia
                        # # #
                        # # obj._try_apply_code('044e-51eb-4498')
                        # obj._update_programs_and_rewards()  # ban dau sale order se chua load cac coupon co the ap dung nen phai goi de load trc
                        # obj._apply_program_reward(code_reward, code_coupon)  # __ME: reward_id (from program), coupon = card
                        # obj._update_programs_and_rewards()
            # order_line is_reward_line, reward_id, coupon_id, reward_identifier_code, points_cost
            #

            return {
                'success': True,
                'message': 'Đặt hàng thành công',
                'id': obj.id
            }

        return result

    # Apply coupon code
    @validate_token
    @http.route('/api/sale_order/apply_code/<int:order_id>', type='json', auth="none", methods=['POST'])
    def sale_order_apply_code(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Áp dụng mã ưu đãi không thành công'
        }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        if not params and 'code' not in params:
            result['message'] = 'Mã ưu đãi không hợp lệ'
            return result

        code = params.get('code')

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            order_line = order.order_line
            leng = len(order_line)
            count_line_before = len(order_line)

            card = request.env['loyalty.card'].sudo().search(domain=[
                ['code', '=', code]
            ], limit=1)

            if card and card.id > 0:
                if card.program_id.active == False:
                    result['message'] = 'Chương trình giảm giá này đã hết hiệu lực'
                    return result

                # if card.use_count == int(card.points):
                if card.points < 1:
                    result['message'] = 'Mã giảm giá đã được sử dụng'
                    return result

                reward = card.program_id.reward_ids[0]

                order._update_programs_and_rewards()  # ban dau sale order se chua load cac coupon co the ap dung nen phai goi de load trc
                order._try_apply_code(code)
                order._update_programs_and_rewards()  # ban dau sale order se chua load cac coupon co the ap dung nen phai goi de load trc
                order._apply_program_reward(reward, card)  # __ME: reward_id (from program), coupon = card
                order._update_programs_and_rewards()

                bb = len(order.order_line)

                if len(order.order_line) > count_line_before:
                    return {
                        'success': True,
                        'message': 'Áp dụng mã giảm giá thành công'
                    }

        return result

    # Update sale order
    # Xac nhan sale order

    @validate_token
    @http.route('/api/sale_order/update_payment_order_id/<int:order_id>', type='json', auth="none", methods=['POST'])
    def sale_order_update_payment_order_id(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Cập nhật payment order không thành công'
        }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        payment_order_id = params.get('payment_order_id', None)

        if not payment_order_id:
            result['message'] = 'Payment order id không hợp lệ'
            return result

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            # update orderId nhận từ app và ghi vào odoo
            input = {
                'order_id': order.id,
                'payment_order_id': payment_order_id
            }

            success = request.env['zalo.payment.transaction'].sudo().create(input)

            if success:
                result['message'] = 'Cập nhật thành công'
                return result

        return result

    # Confirm sale order
    @validate_token
    @http.route('/api/sale_order/confirm/<int:order_id>', type='json', auth="none", methods=['POST'])
    def sale_order_confirm(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Không thể xác nhận đơn hàng'
        }

        # if not params or params.get('payment_method',
        #                             '') not in PAYMENT_METHOD:
        #     result['success'] = False
        #     result['message'] = 'Phương thức thanh toán không hợp lệ'
        #     return result
        #
        # payment_method = {
        #     "id": params.get('payment_method'),
        #     "isCustom": False
        # }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            success = order.write({'customer_confirmed': True})
            # tạo mac, mac này để payment create order bên phía app

            abc = order.order_line
            order_lines = abc
            order_line = []
            for line in order_lines:
                order_line.append({
                    'id': line.product_id.id,
                    'amount': int(line.price_total)
                })
            desc = 'TTHD.' + order.name
            amount = int(order.amount_total)
            method = order.payment_method
            # if method == 'cod' or method == 'bank':
            #     method = method + '_sandbox'
            payment_method = {
                "id": method,
                "isCustom": False
            }

            data = {
                'desc': desc,
                'amount': amount,
                'method': json.dumps(payment_method).replace(': ', ':').replace(', ', ','),
                'item': json.dumps(order_line).replace(': ', ':').replace(', ', ','),
            }



            key = '3238e5115d4525fffe4e0a810d1fed0b'
            mac = self.generate_mac(data, key)

            mac_string = 'amount=51000&desc=Thanh toan hd ABC&item=[{"id":1,"amount":21000},{"id":2,"amount":30000}]&method={\"id\": \"VNPAY_SANDBOX\", \"isCustom\": false}'
            mac2 = hmac.new(key.encode(), mac_string.encode(), digestmod=hashlib.sha256).hexdigest()

            if success:
                return {
                    'success': True,
                    'message': 'Xác nhận đơn hàng thành công',
                    'data': data,
                    'mac': mac,
                    'item': order_line,
                    'mac2': mac2,
                    'id': order_id,
                }

        return result

    # Sale order update payment method
    @validate_token
    @http.route('/api/sale_order/update_payment_method/<int:order_id>', type='json', auth="none", methods=['POST'])
    def sale_order_update_payment_method(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Thay đổi phương thức thanh toán không thành công'
        }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        if 'payment_method' not in params or params.get('payment_method') not in PAYMENT_METHOD:
            result['message'] = 'Phương thức thanh toán không hợp lệ'
            return result

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            if order.state in ['sale', 'cancel']:
                result['message'] = 'Cập nhật không thành công, đơn hàng đã xác nhận hoặc đã hủy'
                return result
            success = order.write({'payment_method': params.get('payment_method')})

            if success:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        return result

    # Sale order update shipping method
    @validate_token
    @http.route('/api/sale_order/update_shipping_method/<int:order_id>', type='json', auth="none",
                methods=['POST'])
    def sale_order_update_shipping_method(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Thay đổi hình thức giao hàng không thành công'
        }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not params or not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        if 'shipping_method' not in params or params.get('shipping_method') not in ['delivery', 'go_to_shop']:
            result['message'] = 'Hình thức vận chuyển không hợp lệ'
            return result

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            if order.state in ['sale', 'cancel']:
                result['message'] = 'Cập nhật không thành công, đơn hàng đã xác nhận hoặc đã hủy'
                return result
            success = order.write({'shipping_method': params.get('shipping_method')})

            if success:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        return result

    # Sale order update delivery address
    @validate_token
    @http.route('/api/sale_order/update_delivery_address/<int:order_id>', type='json', auth="none",
                methods=['POST'])
    def sale_order_update_delivery_address(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Thay đổi địa chỉ giao hàng không thành công'
        }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not params or not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        if not params or 'delivery_address_id' not in params or params.get('delivery_address_id', -1) < 1:
            result['message'] = 'Địa chỉ giao hàng không hợp lệ'
            return result

        delivery_address_id = params.get('delivery_address_id')

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            if order.state in ['sale', 'cancel']:
                result['message'] = 'Cập nhật không thành công, đơn hàng đã xác nhận hoặc đã hủy'
                return result

            success = order.write({'delivery_address_id': delivery_address_id})

            if success:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        return result

    # Sale order update note
    @validate_token
    @http.route('/api/sale_order/update_note/<int:order_id>', type='json', auth="none",
                methods=['POST'])
    def sale_order_update_note(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Cập nhật ghi chú không thành công'
        }

        user = request.env.user
        if not user:
            result['message'] = 'Không có thông tin khách hàng'
            return result

        pId = user.partner_id.id

        if not params or not pId:
            result['message'] = 'Không có thông tin khách hàng'
            return result
        if order_id < 1:
            result['message'] = 'Không có thông tin đơn hàng'
            return result

        if 'note' not in params:
            result['message'] = 'Không có ghi chú'
            return result

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            if order.state in ['sale', 'cancel']:
                result['message'] = 'Cập nhật không thành công, đơn hàng đã xác nhận hoặc đã hủy'
                return result

            success = order.write({'note': params.get('note')})
            if success:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        return result

    @validate_token
    @http.route('/api/sale_order/page/<int:page>', type='json', auth="none", methods=['POST'])
    def sale_order_list(self, page=1):
        user = request.env.user
        if not user:
            return []

        params = request.httprequest.json

        # params = request.params

        pId = user.partner_id.id

        model = 'sale.order'
        m_sale_order_line = 'sale.order.line'

        domain = [
            ['partner_id', '=', pId]
        ]

        if params:
            if params.get('filter_by_status', '') in ['draft', 'sale', 'cancel']:
                domain = [
                    '&',
                    ['partner_id', '=', pId],
                    ['state', '=', params.get('filter_by_status')],
                ]
            if params.get('filter_by_status', '') in ['confirmed']:
                domain = [
                    '&',
                    ['partner_id', '=', pId],
                    ['customer_confirmed', '=', True],
                ]


        result = []

        # fields = ['name', 'list_price', 'categ_id', 'description_sale']
        items = request.env[model].search(domain=domain)
        # items = request.env[model].search_read(domain=domain, fields=['name', 'amount_total', 'date_order', 'state_for_customer'])

        for item in items:
            # order_line = []
            # for line in item.order_line:
            #     order_line.append({
            #         'id': line.id,
            #         'product_id': line.product_template_id.id,
            #         'product_name': line.product_template_id.name,
            #         'price': line.price_unit,
            #         'qty': line.product_uom[0],
            #         'total': line.price_total,
            #     })
            obj = {
                'id': item.id,
                'name': item.name,
                # 'order_line': order_line,
                'amount_total': item.amount_total,
                'order_date': item.date_order,
                'status': item.state_for_customer,
                'delivery_status': 'draft',
                'payment_status': item.zalo_payment_state,
                
                # chua co field
                # 'note': 'Ghi chu test',
                # 'payment_method': 'cod',
                # 'shipping_method': 'delivery',
            }
            result.append(obj)

        return result

    @validate_token
    @http.route('/api/sale_order/cancel/<int:order_id>', type='json', auth="none", methods=['POST'])
    def sale_order_cancel(self, order_id=-1):
        model = 'sale.order'
        user = request.env.user

        result = {
            'success': False,
            'message': 'Yêu cầu hủy đơn hàng không thành công'
        }

        if order_id <= 0 or not user or not user.id or not user.partner_id:
            return result

        pId = user.partner_id.id

        order = request.env[model].sudo().browse(order_id)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            # if order.state ==
            # success = order.write({'customer_cancel': True})
            success = order.action_cancel()
            if success:
                return {
                    'success': True,
                    'message': 'Đã gửi yêu cầu hủy đơn hàng'
                }

        return result

    @validate_token
    @http.route('/api/sale_order/payment_info/<int:id>', type='json', auth="none", methods=['POST'])
    def sale_order_get_payment_info(self, id=-1):
        model = 'sale.order'
        user = request.env.user

        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Lấy thông tin thanh toán không thành công'
        }

        if not params or params.get('payment_method',
                                    '') not in PAYMENT_METHOD:
            result['success'] = False
            result['message'] = 'Phương thức thanh toán không hợp lệ'
            return result

        payment_method = {
            "id": params.get('payment_method'),
            "isCustom": False
        }

        if not user:
            result['success'] = False
            result['message'] = 'Thông tin người dùng không hợp lệ'
            return result

        pId = user.partner_id.id

        order = request.env[model].sudo().browse(id)

        if not order:
            result['success'] = False
            result['message'] = 'Không tìm thấy đơn hàng'
            return result

        if order.partner_id.id != pId:
            result['success'] = False
            result['message'] = 'Bạn không có quyền truy cập đơn hàng này'
            return result

        abc = order.order_line
        order_lines = abc
        order_line = []
        for line in order_lines:
            order_line.append({
                'id': line.product_id.id,
                'amount': int(line.price_total)
            })
        desc = 'TTHD.' + order.name
        amount = int(order.amount_total)
        method = '{"id":"VNPAY_SANDBOX","isCustom":false}'

        data = {
            'desc': desc,
            'amount': amount,
            'method': json.dumps(payment_method).replace(': ', ':').replace(', ', ','),
            'item': json.dumps(order_line).replace(': ', ':').replace(', ', ','),
        }

        key = '3238e5115d4525fffe4e0a810d1fed0b'
        mac = self.generate_mac(data, key)

        if not mac or mac == '':
            result['success'] = False
            result['message'] = 'Không tạo được thông tin thanh toán'
            return result

        return {
            'success': True,
            'message': 'Tạo thông tin thanh toán thành công',
            'data': data,
            'mac': mac,
            'item': order_line,
        }


    @validate_token
    @http.route('/api/sale_order/<int:id>', type='json', auth="none", methods=['POST'])
    def sale_order_get(self, id=-1):
        model = 'sale.order'
        user = request.env.user
        if not user:
            return None

        pId = user.partner_id.id
        m_sale_order_line = 'sale.order.line'

        # domain = [
        #     '&',
        #     ['partner_id', '=', pId],
        #     ['id', '=', id]
        # ]
        # result = []

        # fields = ['name', 'list_price', 'categ_id', 'description_sale']
        # items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain)

        order = request.env[model].sudo().browse(id)

        if not order:
            return None

        if order.partner_id.id != pId:
            return None

        order_line = []
        for line in order.order_line:
            if line.is_reward_line == True or line.is_loyalty_member_reward == True:
                continue
            display_name = line.name if line.is_reward_line else line.product_template_id.name
            order_line.append({
                'id': line.id,
                'product_id': line.product_template_id.id,
                'product_name': display_name,
                'price': line.price_unit,
                'qty': line.product_uom_qty,
                'total': line.price_total,
                'is_reward_line': True if line.is_reward_line == True or line.is_loyalty_member_reward == True else False,
                'image': '/image/product/' + str(line.product_template_id.id),
            })

        result = {
            'id': order.id,
            'name': order.name,
            'order_line': order_line,
            'amount_total': order.amount_total,
            'amount_reward': order.reward_amount,       # gia tri giam gia
            'delivery_fee': order.delivery_fee,         # phi van chuyen
            'order_date': order.date_order,
            'status': order.state_for_customer,
            'delivery_status': 'draft',
            'payment_status': 'unpaid' if order.zalo_payment_state != 'paid' else 'paid',
            # 'status': order.state, OLD

            # chua co field
            'note': '' if order.note == False else order.note,
            'payment_method': order.payment_method,
            'shipping_method': order.shipping_method,
            'delivery_address_id': -1 if (not order.delivery_address_id or order.delivery_address_id.id < 1) else order.delivery_address_id.id,
        }

        return result


    ## Sổ địa chỉ
    @validate_token
    @http.route('/api/address', type='json', auth="none", methods=['POST'])
    def address_list(self):
        user = request.env.user
        if not user:
            return []

        pId = user.partner_id.id

        model = 'res.partner'
        domain = [
            '&',
            ['parent_id', '=', pId],
            ['is_deleted', '=', False],
        ]
        result = []

        fields = ['name', 'list_price', 'categ_id', 'description_sale']
        items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'phone': item.phone,
                'street': item.street,
                'street2': item.street2,
                'is_default_address': item.is_default_address
            }
            result.append(obj)

        return result

    # Get So dia chi
    @validate_token
    @http.route('/api/address/<int:id>', type='json', auth="none", methods=['POST'])
    def address_get(self, id):
        model = 'res.partner'
        user = request.env.user
        if not user:
            return None

        pId = user.partner_id.id

        if id <= 0:
            return None
        count = request.env[model].sudo().search_count(
            domain=[
                '&',
                ['id', '=', id],
                '&',
                ['parent_id', '=', pId],
                ['is_deleted', '=', False]
            ])
        if count <= 0:
            return None

        obj = request.env[model].sudo().browse(id)

        if obj and obj.id > 0:
            if obj.active == False or obj.is_deleted == True:
                return None

            if obj.type != 'delivery' or not obj.parent_id or obj.parent_id.id != pId:
                return None

            result = {
                'id': obj.id,
                'name': obj.name,
                'phone': obj.phone,
                'street': obj.street,
                'street2': obj.street2,
                'is_default_address': obj.is_default_address
                # 'image': obj.image_512
            }

            return result
        return None

    # Create So dia chi
    @validate_token
    @http.route('/api/address/create', type='json', auth="none", methods=['POST'])
    def address_create(self):
        model = 'res.partner'
        params = request.params

        result = {
            'success': False,
            'message': 'Thêm sổ địa chỉ không thành công'
        }

        user = request.env.user
        if not user:
            return result

        pId = user.partner_id.id

        if not params or not pId:
            return result

        name = params.get('name')
        phone = params.get('phone')
        street = params.get('street')
        street2 = params.get('street2')
        is_default = params.get('is_default_address')

        input = {
            'name': name,
            'phone': phone,
            'street': street,
            'street2': street2,
            'is_default_address': is_default,
            'parent_id': pId,
            'type': 'delivery'
        }

        obj = request.env[model].sudo().create(input)

        if obj and obj.id > 0:
            # reset default address
            if is_default == True:
                address_list = request.env[model].sudo().search(domain=[
                    '&',
                    ['parent_id', '=', pId],
                    '&',
                    ['type', '=', 'delivery'],
                    ['id', 'not in', [obj.id]]
                ])

                if address_list and len(address_list) > 0:
                    for address in address_list:
                        address.write({'is_default_address': False})

            return {
                'success': True,
                'message': 'Đã thêm sổ địa chỉ',
                'id': obj.id,
            }
        return result

    # Update
    @validate_token
    @http.route('/api/address/update/<int:address_id>', type='json', auth="none", methods=['POST'])
    def address_update(self, address_id=-1):
        # abc = request
        model = 'res.partner'
        params = request.httprequest.json

        if params and 'params' in params:
            params = params.get('params')

        result = {
            'success': False,
            'message': 'Cập nhật không thành công'
        }

        user = request.env.user
        pId = user.partner_id.id

        if not params or address_id <= 0 or not user or not pId:
            return result

        id = address_id
        name = params.get('name', '')
        phone = params.get('phone', '')
        street = params.get('street', '')
        street2 = params.get('street2', '')
        is_default = params.get('is_default_address')

        input = {
            # 'name': name,
            # 'phone': phone,
            # 'street': street,
            # 'street2': street2,
            # 'is_default_address': is_default,
        }

        if name != '':
            input['name'] = name
        if phone != '':
            input['phone'] = phone;
        if street != '':
            input['street'] = street;
        if street2 != '':
            input['street2'] = street2;
        if 'is_default_address' in params and type(is_default) == type(False):
            input['is_default_address'] = is_default


        obj = request.env[model].sudo().browse(id)

        if obj:
            if obj.active == False or obj.is_deleted == True:
                result['message'] = 'Địa chỉ liên hệ này không tồn tại'
                return result

            if obj.type != 'delivery' or not obj.parent_id or obj.parent_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập dữ liệu này'
                return result

            record = obj.write(input)  # true / false

            if record == True and is_default == True:
                address_list = request.env[model].sudo().search(domain=[
                    '&',
                    ['parent_id', '=', pId],
                    '&',
                    ['type', '=', 'delivery'],
                    ['id', 'not in', [obj.id]]
                ])

                if address_list and len(address_list) > 0:
                    for address in address_list:
                        address.write({'is_default_address': False})

            if record:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công',
                    # 'input': input,
                    # 'params': params
                }

        result['message'] = 'Sổ địa chỉ hiện tại không tồn tại'
        return result

    # Update
    @validate_token
    @http.route('/api/address/remove/<int:address_id>', type='json', auth="none", methods=['POST'])
    def address_remove(self, address_id=-1):
        model = 'res.partner'

        result = {
            'success': False,
            'message': 'Xóa không thành công'
        }

        user = request.env.user
        pId = user.partner_id.id

        if address_id <= 0 or not user or pId <= 0:
            return result

        obj = request.env[model].sudo().browse(address_id)

        if obj:
            if obj.active == False or obj.is_deleted == True:
                result['message'] = 'Địa chỉ liên hệ này không tồn tại'
                return result

            if obj.type != 'delivery' or not obj.parent_id or obj.parent_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập dữ liệu này'
                return result

            record = obj.write({'is_deleted': True, 'active': False})  # true / false


            if record == True and obj.is_default_address == True:
                address_list = request.env[model].sudo().search(domain=[
                    '&',
                    ['parent_id', '=', pId],
                    '&',
                    ['type', '=', 'delivery'],
                    '&',
                    ['id', 'not in', [obj.id]],
                    ['is_deleted', '!=', True],
                ], limit=1)

                if address_list and len(address_list) > 0:
                    for address in address_list:
                        address.write({'is_default_address': True})

            if record:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        # result['message'] = 'Sổ địa chỉ hiện tại không tồn tại'
        return result

    ## can doi ten
    @validate_token
    @http.route('/api/customer_coupons', type='json', auth="none", methods=['POST'])
    def coupons_customer(self):
        model = 'loyalty.card'
        user = request.env.user

        result = []

        if not user or not user.partner_id or user.partner_id.id <= 0:
            return result

        pId = user.partner_id.id

        cards = request.env[model].sudo().search(domain=[
            '&',
            ['partner_id', '=', pId],
            # '&',
            ['program_type', 'in', ['coupons', 'gift_card', 'promo_code', 'next_order_coupons']],
            # ['points', '>', 0]
        ])

        if cards and len(cards) > 0:
            for card in cards:
                if card.program_id.active:
                    result.append({
                        'id': card.id,
                        'name': card.program_id.name,
                        'description': '' if card.program_id.description == False else card.program_id.description,
                        'expiration_date': '' if card.expiration_date == False else card.expiration_date,
                        'code': '' if card.code == False else card.code,
                        'qty': card.points,
                        'image': '/image/coupon/' + str(card.program_id.id),
                    })

        return result

    # Detail coupon
    @validate_token
    @http.route('/api/customer_coupons/<int:card_id>', type='json', auth="none", methods=['POST'])
    def coupons_get(self, card_id=-1):
        model = 'loyalty.card'

        user = request.env.user
        pId = request.env.user.partner_id.id


        if not user or not user.partner_id or user.partner_id.id < 1 or card_id < 1:
            return None

        card = request.env[model].sudo().browse(card_id)

        if card and card.id > 0 and card.partner_id.id == user.partner_id.id:
            return {
                'id': card_id,
                'card_name': '' if card.program_id.name == False else card.program_id.name,
                'description': '' if card.program_id.description == False else card.program_id.description,
                'code': '' if card.code == False else card.code,
                'expiration_date': '' if card.expiration_date == False else card.expiration_date,
                'image': '/image/coupon/' + str(card.program_id.id),
            }

        return None

    # Loyalty membership cards
    @http.route('/api/loyalty_membership_cards', type='json', auth="public", methods=['POST'])
    def loyalty_membership_cards(self):
        model = 'loyalty.program'
        domain = [
            '&',
            ['program_type', '=', 'loyalty'],
            ['is_zalo_loyalty_program', '=', True],
        ]
        result = []

        # loyalty = request.env[model].sudo()._get_next_level()

        loyalty = request.env[model].sudo().search(domain=domain, order='level ASC', limit=1)

        if loyalty and loyalty.loyalty_tier_ids and len(loyalty.loyalty_tier_ids):
            for item in loyalty.loyalty_tier_ids:
                obj = {
                    'id': item.id,
                    'card_name': item.name,
                    'description': '' if item.description == False else item.description,
                    'card_level': item.level,
                    'required_points': item.range_min,
                    'color': item.color,
                    'next_level_id': item.next_level_id,
                    # 'next_level_name': item.next_level_id.name,
                    # 'icon': '/image/member_card/' + str(item.id),
                    #
                    # 'image': ''
                }
                result.append(obj)

        return result

    @validate_token
    @http.route('/api/loyalty/point_accumulation_history', type='json', auth="none", methods=['POST'])
    def loyalty_point_accumulation_history(self):
        user = request.env.user
        if not user:
            return []

        pId = user.partner_id.id

        model = 'sale.order'
        m_sale_order_line = 'sale.order.line'

        domain = [
            '&',
            ['partner_id', '=', pId],
            ['state', '=', 'sale']
        ]

        result = []

        # fields = ['name', 'list_price', 'categ_id', 'description_sale']
        items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain, order='date_order DESC')

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                # 'order_line': order_line,
                'amount_total': item.amount_total,
                'order_date': item.date_order,
                'status': item.state,
                'accum_point': item.redeem_points
            }
            result.append(obj)

        return result

    @validate_token
    @http.route('/api/loyalty/exchange_reward/<int:program_id>', type='json', auth="none", methods=['POST'])
    def loyalty_exchange_reward(self, program_id=-1):
        model = 'loyalty.program'

        result = {
            'success': False,
            'message': 'Đổi thưởng không thành công'
        }

        if program_id < 1:
            result['message'] = 'Mã chương trình không hợp lệ'
            return result

        user = request.env.user
        if not user or not user.partner_id or user.partner_id.id < 1:
            result['message'] = 'Không có thông tin người dùng'
            return result

        pId = user.partner_id.id

        domain = [
            '&',
            ['partner_id', '=', pId],
            ['state', '=', 'sale']
        ]

        program = request.env[model].sudo().with_context(lang='vi_VN').search(domain=[
            ['id', '=', program_id]
        ], limit=1)

        if not program or program.id < 1:
            result['message'] = 'Không tìm thấy chương trình'
            return result

        vals = {
            'program_id': program.id,
            'points': program.init_points,  # lay tu chuong trinh
            # 'expiration_date': '',  # lay tu program
            'partner_id': pId,
        }

        #       check expiration date
        # if program.expiration_date:
        #     vals['expiration_date'] = program.expiration_date

        #       check co du diem ko
        exchange_points = 0
        cus_card = False
        if program.required_points > 0:
            if program.loyalty_program_apply_id and program.loyalty_program_apply_id.id > 0:
                apply_program = program.loyalty_program_apply_id
                cus_card = request.env['loyalty.card'].sudo().search(domain=[
                    '&',
                    ['partner_id', '=', pId],
                    ['program_id', '=', apply_program.id],
                ], limit=1)
                if not cus_card or cus_card.id < 1:
                    result['message'] = 'Thẻ chưa hoạt động'
                    return result
                if cus_card.points < program.required_points:
                    result['message'] = 'Bạn chưa đủ điểm tích lũy'
                    return result
                exchange_points = program.required_points

        card = request.env['loyalty.card'].sudo().create(vals)
        if card and card.id:
            if exchange_points > 0 and cus_card != False:
                cus_card.points -= exchange_points

            return {
                'success': True,
                'message': 'Đổi thưởng thành công'
            }

        return result

    ## list coupon cho phan doi thuong
    @validate_token
    @http.route('/api/loyalty/coupons', type='json', auth="none", methods=['POST'])
    def loyalty_coupons(self):
        # lam don gian moi chi load va xac dinh co ban cac program da ap dung doi thuong
        # chua lam doi thuong nang cao hon
        model = 'loyalty.program'
        user = request.env.user

        result = []

        if not user or not user.partner_id or user.partner_id.id <= 0:
            return result

        pId = user.partner_id.id

        programs = request.env[model].sudo().search(domain=[
            # '&',
            ['program_type', '=', 'coupons'],
        ])

        card_ids = []
        cards = request.env['loyalty.card'].sudo().search(domain=[
            ['partner_id', '=', pId]
        ])
        for card in cards:
            card_ids.append(card.id)

        if programs and len(programs) > 0:
            for program in programs:
                is_redeemed = len(card_ids) > 0
                if len(card_ids) > 0:
                    is_redeemed = card.id in card_ids
                result.append({
                    'id': program.id,
                    'name': program.name,
                    'description': '' if program.description == False else program.description,
                    'expiration_date': '' if program.date_to == False else program.date_to,
                    'required_points': program.required_points,
                    # 'code': '' if card.code == False else card.code,
                    'qty': program.init_points,
                    'is_redeemed': is_redeemed,
                    'image': '/image/coupon/' + str(program.id),
                })

        return result

    # lam ui news, category



    # Get User profile
    # @http.route('/api/user/profile1', type='json', auth="user", methods=['POST'])
    # def user_profile1(self):
    #     model = 'res.partner'

    # member card - loyalty program
    # current card level
    # calc start - end - current

    # apply giảm giá tự động cho đơn hàng theo level card
    # apply mã giảm giá

    # load phieu giam gia
    # voucher vs coupon gan giong nhau, cung loai




    # ******************************************** ----- END API ----- ************************************************