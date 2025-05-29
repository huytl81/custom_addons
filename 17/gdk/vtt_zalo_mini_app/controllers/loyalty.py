# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

from .check_token import validate_token


class LoyaltyAPI(http.Controller):
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