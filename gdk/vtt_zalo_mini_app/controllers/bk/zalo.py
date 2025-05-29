# -*- coding: utf-8 -*-
import datetime
import functools
import hashlib
import hmac
import logging

import requests

from odoo import http
from odoo.http import request

import json

_logger = logging.getLogger(__name__)

PAYMENT_METHOD = [
    'cod', 'bank', 'vnpay',
    'cod_sandbox', 'bank_sandbox', 'vnpay_sandbox'
]

EVENTS = [
    'follow',
]

class ZaloAPI(http.Controller):
    # *********** Zalo webhook events *************
    # event: follow
    def handle_event_oa_follow(self, data):
        data_sample = {
            "oa_id": "4024926008133882615",
            "follower": {"id": "8958041078911298472"},
            "event_name": "follow", #unfollow
            "source": "oa_profile",
            "app_id": "3349222483842580322",
            "timestamp": "1724921862647"
        }

        p = request.env['res.partner'].sudo().search(domain=[
            ['id', '=', 7]
        ], limit=1)

        if 'follower' not in data.keys():
            if p:
                p.write({'comment': 'fol'})
            return

        if 'oa_id' not in data.keys():
            p.write({'comment': 'oa_id'})
            return

        #
        event_name = data['event_name']
        event_timestamp = int(data['timestamp']) / 1000
        event_time = (datetime.datetime.fromtimestamp(event_timestamp)).strftime('%Y-%m-%d %H:%M:%S')

        # check co dung OA ko
        oa_id = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_id')
        oa_access_token = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')

        oa_user_id = data['follower']['id']
        user_id_by_app = data.get('user_id_by_app', '')

        if oa_user_id:
            # unfollow
            # - check partner ->
            #   - neu co: chuyen trang thai
            #   - neu ko: return (vi chua co tk, trang thai unfollow dong nghia ko the goi API lay thong tin user dc)

            if event_name == 'unfollow':
                # can cap nhat bo sung neu co user_id_by_app
                partner = request.env['res.partner'].sudo().search(domain=[
                    ['zalo_id_by_oa', '=', oa_user_id],
                ], limit=1)

                if not partner:
                    return

                partner.write({
                    'followed_oa': False,
                    'unfollowed_oa_time': event_time
                })

            # follow
            if event_name == 'follow':
                headers = {
                    'access_token': oa_access_token,
                }

                response = requests.get(
                    'https://openapi.zalo.me/v3.0/oa/user/detail?data={"user_id":"' + oa_user_id + '"}',
                    headers=headers,
                )

                if response.status_code == 200:
                    r_data = response.json()
                    if 'data' not in r_data.keys() or 'error' not in r_data.keys() or r_data.get('error', 0) != 0:
                        if p:
                            p.write({'comment': json.dumps(oa_access_token)})
                        return

                    u_profile = r_data.get('data')

                    if p:
                        p.write({'comment': json.dumps(u_profile)})

                    if u_profile:
                        user_id_by_app = u_profile.get('user_id_by_app', '')
                        is_followed = u_profile.get('user_is_follower', False)
                        display_name = u_profile.get('display_name', '')
                        avatar = u_profile.get('avatar', '')

                        # check da co lien he chua
                        partner = request.env['res.partner'].sudo().search(domain=[
                            '|',
                            ['zalo_id', '=', user_id_by_app],
                            ['zalo_id_by_oa', '=', user_id_by_app],
                        ], limit=1)

                        vals = {
                            'zalo_id_by_oa': oa_user_id,
                            'name': display_name,
                            'zalo_name': display_name,
                            'zalo_picture': avatar,
                            #
                            'followed_oa': is_followed,
                            'followed_oa_time': event_time,
                        }
                        if user_id_by_app != '':
                            vals['zalo_id'] = user_id_by_app

                        # if p:
                        #     vals['partner'] = 'bbb'
                        #     if partner:
                        #         vals['partner'] = partner.id
                        #     p.write({'comment': json.dumps(vals)})

                        if not partner:
                            vals['first_time_followed_oa'] = event_time
                            p = request.env['res.partner'].sudo().create(vals)

                            if p:
                                return {
                                    'success': True,
                                    'message': 'Cập nhật thành công 1'
                                }
                        else:
                            success = partner.write(vals)
                            if success:
                                return {
                                    'success': True,
                                    'message': 'Cập nhật thành công 2'
                                }

                        if p:
                            p.write({'comment': 'suc 3'})

                        return {
                            'success': False,
                            'message': 'Cập nhật không thành công 3'
                        }

                lo = response.json()
                p.write({'comment': json.dumps(lo)})







        # lay thong tin: follower[id], timestamp
        # goi API de lay thong tin: de ra dc zalo user id (app)
        # https://openapi.zalo.me/v3.0/oa/user/detail?data={"user_id":"4572947693969771653"} + access_token tren header: CURL -> python code
        # check neu co tk roi thi chuyen thanh followed, chua co tk thi tao tk --> Ko tao tk, chi tao partner --> Check kt da co partner nao co user_id_by_app chua, neu co thi cap nhat bo sung them thong tin tren partner do
        # * can bo sung them field: zalo_oa_user_id

        user_profile = {
            "data": {
                "user_id": "8958041078911298472",
                "user_id_by_app": "5902882255260862156",
                "display_name": "Trong Giap",
                "user_alias": "Trong Giap",
                "is_sensitive": False,
                "user_last_interaction_date": "30/08/2024",
                "user_is_follower": False,
                "avatar": "https://s120-ava-talk.zadn.vn/d/9/d/e/1/120/510b4d41b859f5b9998bef47370417a6.jpg",
                "avatars": {
                    "240": "https://s240-ava-talk.zadn.vn/d/9/d/e/1/240/510b4d41b859f5b9998bef47370417a6.jpg",
                    "120": "https://s120-ava-talk.zadn.vn/d/9/d/e/1/120/510b4d41b859f5b9998bef47370417a6.jpg"
                },
                "tags_and_notes_info": {
                    "notes": [],
                    "tag_names": []
                }
            },
            "error": 0,
            "message": "Success"
        }



        ab = ''

        return True
    # *********** END *************

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

    # zalo webhook
    # can rename link: -> /api/zalo_webhook
    @http.route('/zalo_webhook/user_revoke_consent', type='json', auth="public", methods=['POST'])
    def webhook_user_revoke_consent(self):
        params = request.httprequest.json

        signature = request.httprequest.headers.get("X-ZEvent-Signature", '')
        if not signature or signature == '' or not params or 'timestamp' not in params.keys() or 'event_name' not in params.keys() or 'oa_id' not in params.keys():
            return {'success': False, 'message': 'Thông tin gửi đến ko hợp lệ'}

        # params['sign'] = signature
        p_s = { 'prams': params, 'sign': signature}

        # for test: ghi vao để kt dữ liệu từ webhook
        p = request.env['res.partner'].sudo().search(domain=[
            ['id', '=', 7]
        ], limit=1)

        if p:
            p.write({'comment': json.dumps(p_s)})

        ##  check dam bao toan ven du lieu
        # mac = sha256(appId + data + timestamp + oa_secret_key)

        timestamp = params['timestamp']
        # timestamp = datetime.datetime.fromtimestamp(int(params['timestamp']) / 1000)

        error = params.get('error', 0)

        # handle lỗi từ zalo gửi đến
        if error != 0:
            return {'success': False, 'message': 'Đã có lỗi xảy ra'}

        oa_id = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_id')
        oa_id_from_request = params.get('oa_id', False)

        if oa_id != oa_id_from_request:
            return {
                'success': False,
                'message': 'Failed'
            }

        oa_secret_key = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_secret_key') # trong zalo developer > webhook
        app_id = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_id')  # super app
        oa_access_token = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')  # super app


        if not oa_secret_key or not app_id or not oa_id or not oa_access_token or not oa_id_from_request:
            return {
                'success': False,
                'message': 'Failed'
            }

        # sinh mac de compare
        s_data = json.dumps(params).replace(': ', ':').replace(', ', ',')
        combined_string = app_id + s_data + timestamp + oa_secret_key
        mac = hashlib.sha256(combined_string.encode('utf-8')).hexdigest()

        # check de dam bao toan ven du lieu: mac == signature (from header: X-ZEvent-Signature)
        if signature.startswith('mac='):
            signature = signature[4:]

        if signature != mac:
            p.write({'comment': json.dumps({
                'signature': signature,
                'mac': mac,
                'data': json.dumps(params),
                'combine_string': combined_string,
            })})

            return {
                'success': False,
                'message': 'Failed'
            }

        event = params.get('event_name')

        if event == 'follow' or event == 'unfollow':
            self.handle_event_oa_follow(params)

        return {
            'success': True,
            'message': 'Success'
        }


    # return raw json data, ko bi boc vao json_rpc nua
    # sb callback hiện tại xử lý cho checkout VNPAY
    @http.route('/api/miniapp/sb_callback', type='http', auth='public', methods=['POST'], csrf=False)
    def zalo_mini_app_callback(self):
        params = request.httprequest.json

        result = {
            'returnCode': 1,
            'returnMessage': 'Thành công'
        }

        data = params.get('data', None)
        mac = params.get('mac', '')
        overallMac = params.get('overallMac', '')
        # key = '3238e5115d4525fffe4e0a810d1fed0b'
        key = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_checkout_private_key')

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
                return request.make_json_response(result)

            order = request.env['sale.order'].sudo().browse(trans.order_id.id)

            if not order or order.id < 1:
                result['returnCode'] = -1
                result['returnMessage'] = 'Đơn hàng ko tồn tại'
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
                'resultCode': resultCode,  # 1 | -1
                'transId': transId,
            }

            req_mac = self.generate_mac(data_for_mac, key, False)

            if req_mac != mac:
                result['returnCode'] = -1
                result['returnMessage'] = 'Mac không hợp lệ'
                return request.make_json_response(result)

            # prepare to check overall mac
            req_overall_mac = self.generate_mac(data, key)

            if req_overall_mac != overallMac:
                result['returnCode'] = -1
                result['returnMessage'] = 'OveralMac không hợp lệ'
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

                # ghi nhan da thanh toan vao order
                order.write({
                    'zalo_payment_state': 'paid'
                })

        # type la http + make_json_response de tra ve json
        return request.make_json_response(result)
