# -*- coding: utf-8 -*-
import json
import math

import requests

from odoo import http
from odoo.http import request


from datetime import date, datetime

from .check_token import validate_token



class PartnerAPI(http.Controller):
    ## get address - country state (Tinh/TP)
    @validate_token
    @http.route('/api/address/get_country_state', type='json', auth="none", methods=['POST'])
    def get_country_state(self):
        user = request.env.user
        if not user:
            return []

        model = 'res.country.state'

        country_VN = request.env['res.country'].sudo().search(domain=[
            ['code', '=', 'VN']
        ], limit=1)

        if not country_VN:
            return []

        country_id = country_VN.id

        domain = [
            ['shipping_allowed', '=', True],
            # ['country_id', '=', country_id],
        ]

        # for zalo review
        # domain = [
        #     ['code', 'in', ['VN-HN', 'VN-DN', 'VN-SG', 'VN-HP']]
        # ]
        result = []

        items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
            }
            result.append(obj)

        return result

    ## get address - district (Quan/Huyen)
    @validate_token
    @http.route('/api/address/get_districts', type='json', auth="none", methods=['POST'])
    def get_districts(self):
        user = request.env.user
        if not user:
            return []

        params = request.httprequest.json
        state_id = params.get('state_id', -1)

        if state_id < 1:
            return []

        check_country_state = request.env['res.country.state'].sudo().search_count(domain=[['id', '=', state_id]])

        if check_country_state < 1:
            return []

        model = 'res.district'

        domain = [
            ['shipping_allowed', '=', True],
            ['state_id', '=', state_id],
        ]
        result = []

        items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                # 'ghn_district_id': item.ghn_district_id,
            }
            result.append(obj)

        return result

    ## get address - ward (Phuong/Xa)
    @validate_token
    @http.route('/api/address/get_wards', type='json', auth="none", methods=['POST'])
    def get_wards(self):
        user = request.env.user
        if not user:
            return []

        params = request.httprequest.json
        district_id = params.get('district_id', -1)

        if district_id < 1:
            return []

        check_district = request.env['res.district'].sudo().search_count(domain=[['id', '=', district_id]])

        if check_district < 1:
            return []

        model = 'res.ward'

        domain = [
            ['shipping_allowed', '=', True],
            ['district_id', '=', district_id],
        ]
        result = []

        items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                # 'ghn_ward_id': item.ghn_ward_id,
            }
            result.append(obj)

        return result

    @validate_token
    @http.route('/api/user/profile', type='json', auth="none", methods=['POST'])
    def user_profile(self):
        model = 'res.partner'

        params = request.params

        user = request.env.user  # code lay user hien tai khi chay that

        if not user:
            return {
                'success': False,
                'message': 'Người dùng không tồn tại'
            }

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

        if obj and obj.id > 0:
            # Get the most recent order ID
            recent_draft_order = request.env['sale.order'].sudo().search([
                ['partner_id', '=', obj.id],
                ['customer_confirmed', '=', False],
                ['online_order_state', '=', 'draft']
            ], limit=1)
            recent_draft_order_id = recent_draft_order.id if recent_draft_order else -1

            result = {
                'name': obj.name,
                'phone': '' if obj.phone == False else obj.phone,
                'email': '' if obj.email == False else obj.email,
                'birth_day': '' if obj.birth_day == False else obj.birth_day,
                'sex': 'male' if obj.sex == False else obj.sex,
                'image': '' if obj.zalo_picture == False else obj.zalo_picture,
                'unconfirm_draft_order_id': recent_draft_order_id,  # Add recent draft order ID to the result
                'followed_oa': False if not obj.followed_oa else obj.followed_oa
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
                    'description': '',
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
                        'current_points': 0,  # so du
                        'level_points': 0,
                        'next_level_points': card_tier.range_max,
                        'color': card_tier.color,
                    }

                card = request.env['loyalty.card'].sudo().search(domain=[
                    '&',
                    ['partner_id', '=', obj.id],
                    ['program_id', '=', loyalty.id]
                ], limit=1)

                if card and card.id > 0 and card.tier_id and card.tier_id.id > 0:
                    card_tier = card.tier_id

                    nxt_lvl_name = '---'
                    if card_tier.next_level_id > 0:
                        next_tier = request.env['vtt.loyalty.tier'].sudo().browse(card_tier.next_level_id)
                        if next_tier:
                            nxt_lvl_name = next_tier.name

                    loyalty_info = {
                        'card_id': card_tier.id,
                        'card_level': card_tier.level,
                        'card_name': card_tier.name,
                        'description': '' if card_tier.description == False else card_tier.description,
                        'current_points': math.floor(card.points),  # so du
                        'level_points': card.level_points,
                        'next_level_points': card_tier.range_max,
                        'next_level_name': nxt_lvl_name,
                        'color': card_tier.color,
                    }
                result['loyalty_info'] = loyalty_info

            return result

        return None

    ### Personal Info
    # Update Personal Info
    @validate_token
    @http.route('/api/user/update_info', type='json', auth="none", methods=['POST'])
    def user_update_info(self):
        # abc = request
        model = 'res.partner'
        params = request.params

        user = request.env.user  # code lay user khi chay that
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
        if email != False and type(email) == str and email.strip() != '':
            if (email.endswith('@gmail.com') or email.endswith('@yahoo.com') or
                    email.endswith('@yahoo.com.vn') or email.endswith('@outlook.com') or email.endswith(
                        '@outlook.com.vn') or
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
                date.fromisoformat(birth_day)  # check loi
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
            record = obj.write(input)  # true / false
            if record == False:
                return {
                    'success': False,
                    'message': 'Cập nhật không thành công!'
                }

        return {
            'success': True,
            'message': 'Cập nhật thành công'
        }

    @validate_token
    @http.route('/api/user/update_phone_number', type='json', auth="none", methods=['POST'])
    def user_update_phone_number(self):
        model = 'res.partner'

        user = request.env.user  # code lay user khi chay that
        p_id = -1

        if user:
            p_id = user.partner_id.id

        if p_id <= 0:
            return {
                'success': False,
                'message': 'Cập nhật không thành công! Id ko tồn tại'
            }

        # headers = request.httprequest.headers
        # http = request.httprequest

        params = request.httprequest.json
        access_token = ''
        phone_token = ''
        if params:
            access_token = params.get('access_token')
            phone_token = params.get('phone_code')

        # access_token = request.httprequest.headers.get("access_token")
        # phone_token = request.httprequest.headers.get("phone_code")       # phone token

        if access_token == '' or phone_token == '':
            return {
                'success': False,
                'message': 'Access token or phone token is invalid',
                'access': access_token,
                'code': phone_token,
                # 'abc': abc,
                # 'header': json.dumps(headers)
            }

        # get secret key
        secret_key = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_secret_key')

        if not secret_key:
            return {
                'success': False,
                'message': 'App secret key is invalid'
            }

        headers = {
            'access_token': access_token,
            'code': phone_token,
            'secret_key': secret_key,
        }

        response = requests.get('https://graph.zalo.me/v2.0/me/info', headers=headers)

        if response.status_code == 200:
            r_data = json.loads(response.text)
            error = r_data['error']

            if error == 0:
                if r_data['data'] and r_data['data']['number']:
                    phone = r_data['data']['number']

                    obj = request.env[model].sudo().browse(p_id)

                    if obj:
                        record = obj.write({
                            'phone': phone
                        })  # true / false
                        if record == True:
                            return {
                                'success': True,
                                'message': 'Cập nhật thành công!'
                            }

        abc = 12

        return {
            'success': False,
            'message': 'Cập nhật không thành công'
        }


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
        
        items = request.env[model].sudo().with_context(lang='vi_VN').search(domain=domain)

        for item in items:
            state = item.state_id.name if item.state_id.name != None and item.state_id.name != False else ''
            district = item.district_id.name if item.district_id.name != None and item.district_id.name != False else ''
            ward = item.ward_id.name if item.ward_id.name != None and item.ward_id.name != False else ''
            street = item.street if item.street != None and item.street != False else ''

            obj = {
                'id': item.id,
                'name': item.name,
                'phone': item.phone,
                'street': street,
                'street2': item.street2,
                'address': street + ', ' + ward + ', ' + district + ', ' + state,
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

            state = obj.state_id.name if obj.state_id.name != None and obj.state_id.name != False else ''
            district = obj.district_id.name if obj.district_id.name != None and obj.district_id.name != False else ''
            ward = obj.ward_id.name if obj.ward_id.name != None and obj.ward_id.name != False else ''
            street = obj.street if obj.street != None and obj.street != False else ''

            result = {
                'id': obj.id,
                'name': obj.name,
                'phone': obj.phone,
                'street': street,
                'street2': obj.street2,
                'address': street + ', ' + ward + ', ' + district + ', ' + state,
                # 'state_id': obj.state_id,
                # 'district_id': obj.district_id,
                # 'ward_id': obj.ward_id,
                'is_default_address': obj.is_default_address
                # 'image': obj.image_512
            }
            if obj.state_id and obj.state_id.id > 0:
                result['state_id'] = obj.state_id.id
                result['state_name'] = obj.state_id.name
            if obj.district_id and obj.district_id.id > 0:
                result['district_id'] = obj.district_id.id
                result['district_name'] = obj.district_id.name
            if obj.ward_id and obj.ward_id.id > 0:
                result['ward_id'] = obj.ward_id.id
                result['ward_name'] = obj.ward_id.name

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

        name = params.get('name', '')
        phone = params.get('phone', '')
        street = params.get('street', '')
        street2 = params.get('street2', '') # co the bo
        is_default = params.get('is_default_address', False)

        state_id = params.get('state_id', -1)
        district_id = params.get('district_id', -1)
        ward_id = params.get('ward_id', -1)

        country_VN = request.env['res.country'].sudo().search(domain=[
            ['code', '=', 'VN']
        ], limit=1)

        if name == '' or phone == '' or street == '':
            result['message'] = 'Tên, số điện tho���i, địa chỉ ko đc để trống'
            return result

        if state_id < 1 or district_id < 1 or not country_VN or country_VN.id < 1:
            result['message'] = 'Thông tin địa chỉ không hợp lệ'
            return result

        input = {
            'name': name,
            'phone': phone,
            'street': street,
            'street2': street2,
            'country_id': country_VN.id,
            'state_id': state_id,
            'district_id': district_id,
            # 'ward_id': ward_id,

            'is_default_address': is_default,
            'parent_id': pId,
            'type': 'delivery'
        }
        if ward_id > 0:
            ward = request.env['res.ward'].sudo().browse(ward_id)
            if ward:
                if ward.district_id.id == district_id:
                    input['ward_id'] = ward_id
                else:
                    input['ward_id'] = None
        else:
            input['ward_id'] = None

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

        name = params.get('name', '')
        phone = params.get('phone', '')
        street = params.get('street', '')
        street2 = params.get('street2', '')  # co the bo
        is_default = params.get('is_default_address', False)

        state_id = params.get('state_id', -1)
        district_id = params.get('district_id', -1)
        ward_id = params.get('ward_id', -1)

        # country_VN = request.env['res.country'].sudo().search(domain=[
        #     ['code', '=', 'VN']
        # ], limit=1)

        input = {}

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
        if state_id > 0:
            input['state_id'] = state_id
        if district_id > 0:
            input['district_id'] = district_id
        if ward_id > 0:
            ward = request.env['res.ward'].sudo().browse(ward_id)
            if ward:
                if ward.district_id.id == district_id:
                    input['ward_id'] = ward_id
                else:
                    input['ward_id'] = None
            else:
                input['ward_id'] = None
        else:
            input['ward_id'] = None


        obj = request.env[model].sudo().browse(address_id)

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
