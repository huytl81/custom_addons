# -*- coding: utf-8 -*-
import functools
import hashlib
import hmac
import logging
from datetime import timedelta

from odoo import http
from odoo.http import request
from odoo import _

import json

from .check_token import validate_token

_logger = logging.getLogger(__name__)

PAYMENT_METHOD = [
    'COD', 'BANK', 'VNPAY',
    'COD_SANDBOX', 'BANK_SANDBOX', 'VNPAY_SANDBOX'
]


class SaleOrderAPI(http.Controller):
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

    # Create Sale order
    # Khi user bam nut 'Mua ngay' va chuyen sang trang payment
    @validate_token
    @http.route('/api/sale_order/create', type='json', auth="none", methods=['POST'])
    def create_sale_order(self):
        model = 'sale.order'
        params = request.params

        result = {
            'success': False,
            'message': 'Đặt hàng không thành công'
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
            if not item['qty'] or item['qty'] < 1:
                continue
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
            result['message'] = 'Sản phẩm ko hợp lệ'
            return result

        # load đơn nháp (unconfirm) của KH
        unconfirm_order = request.env['sale.order'].sudo().search(domain=[
            ['partner_id', '=', pId],
            ['customer_confirmed', '=', False],
            ['online_order_state', '=', 'draft']
        ], order='id asc', limit=1)

        # nếu có đơn nháp thì reload lại đơn nháp đấy với ds sp mới
        if unconfirm_order:
            unconfirm_order.sudo().reload_order(items)

            return {
                'success': True,
                'message': 'Đặt hàng thành công',
                'id': unconfirm_order.id
            }


        input = {
            'partner_id': pId,
            'order_line': order_line,
            'shipping_method': 'delivery',
            'payment_method': 'COD',
            'customer_note': params.get('note', ''),
            'is_online_order': True,
        }

        zalo_source_id = self._get_zalo_utm_source()
        if zalo_source_id > 0:
            input['source_id'] = zalo_source_id

        # load sổ địa chỉ của KH
        address_list = request.env['res.partner'].search(domain=[
            ['parent_id', '=', pId],
            ['type', '=', 'delivery']
        ])

        if address_list and len(address_list) > 0:
            default_address = address_list[0]
            if len(address_list) > 1:
                for address in address_list:
                    if address.is_default_address == True:
                        default_address = address
            input['delivery_address_id'] = default_address.id

        # create order
        obj = request.env[model].sudo().create(input)

        if obj:
            # ap dung phi ship
            obj.apply_shipping_method()

            # calc and apply loyalty program
            discount_product = obj.company_id.sale_discount_product_id

            # check da co discount_product chua: neu chua -> tao
            if not discount_product:
                obj.company_id.sale_discount_product_id = request.env['product.product'].sudo().create({
                    'name': _('Discount'),
                    'type': 'service',
                    'invoice_policy': 'order',
                    'list_price': 0.0,
                    'company_id': obj.company_id.id,
                    'taxes_id': None,
                    }
                )
                discount_product = obj.company_id.sale_discount_product_id


            loyalty_cards = request.env['loyalty.card'].sudo().search(domain=[
                '&',
                ['partner_id', '=', pId],
                ['program_type', '=', 'loyalty']
            ])

            if loyalty_cards and len(loyalty_cards) > 0:
                cards = []
                for c in loyalty_cards:
                    if c.program_id.auto_apply == True and c.program_id.loyalty_tier_ids and len(c.program_id.loyalty_tier_ids) > 0:
                        cards.append(c)

                for card in cards:
                    # tinh toan va ap dung cac phan thuong theo tier cua card
                    if card.tier_id and card.tier_id.tier_reward_ids and len(card.tier_id.tier_reward_ids) > 0:
                        for reward in card.tier_id.tier_reward_ids:
                            if reward.value > 0 and reward.value_type:
                                amount = reward.value
                                if reward.value_type == 'percent':
                                    amount = obj.amount_total / 100 * reward.value
                                vals = {
                                    'order_id': obj.id,
                                    'product_id': discount_product.id,
                                    'name': 'Giam gia ' if reward.name == False else reward.name,  # lay ten tu reward
                                    'sequence': 999,
                                    'price_unit': -amount,  # tinh tu cong thuc
                                    'coupon_id': card.id,
                                    'is_reward_line': True,
                                    'is_loyalty_member_reward': True,  # phuc vu cho phan backend
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

    # Apply coupon code
    @validate_token
    @http.route('/api/sale_order/apply_code/<int:order_id>', type='json', auth="none", methods=['POST'])
    def apply_code(self, order_id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

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

    # Zalo checkout - Update payment transaction order_id (order_id se co sau khi Thanh cong o man hinh thanh toan cua app)
    @validate_token
    @http.route('/api/sale_order/update_payment_order_id/<int:order_id>', type='json', auth="none", methods=['POST'])
    def update_payment_order_id(self, order_id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

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
    def confirm_sale_order(self, order_id=-1):
        model = 'sale.order'
        params = request.httprequest.json

        result = {
            'success': False,
            'message': 'Không thể xác nhận đơn hàng'
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            # success = order.write({'customer_confirmed': True})
            order.customer_confirm()
            # tạo mac, mac này để payment create order bên phía app

            if order.customer_confirmed:
                order_lines = order.order_line
                order_line = []
                for line in order_lines:
                    order_line.append({
                        'id': line.product_id.id,
                        'amount': int(line.price_total)
                    })
                desc = 'tthd' + order.name
                amount = int(order.amount_total)
                method = order.payment_method
                # if method == 'cod' or method == 'bank':
                #     method = method + '_sandbox'
                payment_method = {
                    "id": method,
                    "isCustom": False   # Ngoai cac PT zalo cung cap
                }

                data = {
                    'desc': desc,
                    'amount': amount,
                    'method': json.dumps(payment_method).replace(': ', ':').replace(', ', ','),
                    'item': json.dumps(order_line).replace(': ', ':').replace(', ', ','),
                }

                key = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_checkout_private_key')
                mac = self.generate_mac(data, key)

                # for test
                # mac_string = 'amount=51000&desc=Thanh toan hd ABC&item=[{"id":1,"amount":21000},{"id":2,"amount":30000}]&method={\"id\": \"VNPAY_SANDBOX\", \"isCustom\": false}'
                # mac2 = hmac.new(key.encode(), mac_string.encode(), digestmod=hashlib.sha256).hexdigest()


                return {
                    'success': True,
                    'message': 'Xác nhận đơn hàng thành công',
                    'data': data,
                    'mac': mac,
                    'item': order_line,
                    # 'mac2': mac2,
                    'id': order_id,
                }

        return result

    # Sale order update payment method
    @validate_token
    @http.route('/api/sale_order/update_payment_method/<int:order_id>', type='json', auth="none", methods=['POST'])
    def update_payment_method(self, order_id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

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
    def update_shipping_method(self, order_id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

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
    def update_delivery_address(self, order_id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            if order.state in ['sale', 'cancel']:
                result['message'] = 'Cập nhật không thành công, đơn hàng đã xác nhận hoặc đã hủy'
                return result

            success = order.write({'delivery_address_id': delivery_address_id, 'partner_shipping_id': delivery_address_id})

            if success:
                order.reapply_shipping_fee()

                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        return result

    # Sale order update note
    @validate_token
    @http.route('/api/sale_order/update_note/<int:order_id>', type='json', auth="none",
                methods=['POST'])
    def update_note(self, order_id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

        if order:
            if order.partner_id.id != pId:
                result['message'] = 'Bạn không có quyền truy cập vào đơn hàng này'
                return result

            if order.state in ['sale', 'cancel']:
                result['message'] = 'Cập nhật không thành công, đơn hàng đã xác nhận hoặc đã hủy'
                return result

            success = order.write({'customer_note': params.get('note')})
            if success:
                return {
                    'success': True,
                    'message': 'Cập nhật thành công'
                }

        return result

    # List sale order
    @validate_token
    @http.route('/api/sale_order/page/<int:page>', type='json', auth="none", methods=['POST'])
    def list_sale_order(self, page=1):
        user = request.env.user
        if not user:
            return []

        params = request.httprequest.json

        pId = user.partner_id.id

        model = 'sale.order'

        domain = [
            ['partner_id', '=', pId]
        ]

        if params:
            status = params.get('filter_by_status', 'all')

            if status != 'all':
                if status in ['draft', 'processing', 'delivering', 'done', 'cancel']:
                    domain = [
                        '&',
                        ['partner_id', '=', pId],
                        ['online_order_state', '=', status],
                    ]

        result = []

        items = request.env[model].search(domain=domain)

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
            date_order = item.date_order + timedelta(hours=7)

            obj = {
                'id': item.id,
                'name': item.name,
                # 'order_line': order_line,
                'amount_total': item.amount_total,
                'order_date': date_order,
                'status': item.online_order_state,
                'delivery_status': 'draft',
                'payment_status': item.zalo_payment_state,
                'customer_confirmed': item.customer_confirmed,

                # chua co field
                # 'note': 'Ghi chu test',
                # 'payment_method': 'cod',
                # 'shipping_method': 'delivery',
            }
            result.append(obj)

        return result

    # Cancel sale order
    @validate_token
    @http.route('/api/sale_order/cancel/<int:order_id>', type='json', auth="none", methods=['POST'])
    def cancel_sale_order(self, order_id=-1):
        model = 'sale.order'
        user = request.env.user

        result = {
            'success': False,
            'message': 'Yêu cầu hủy đơn hàng không thành công'
        }

        if order_id <= 0 or not user or not user.id or not user.partner_id:
            return result

        pId = user.partner_id.id

        order = request.env[model].sudo().search(domain=[
            ['id', '=', order_id]
        ], limit=1)

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
    def get_payment_info(self, id=-1):
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

        order = request.env[model].sudo().search(domain=[
            ['id', '=', id]
        ], limit=1)

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
        desc = 'tthd' + order.name
        amount = int(order.amount_total)
        method = '{"id":"VNPAY_SANDBOX","isCustom":false}'

        data = {
            'desc': desc,
            'amount': amount,
            'method': json.dumps(payment_method).replace(': ', ':').replace(', ', ','),
            'item': json.dumps(order_line).replace(': ', ':').replace(', ', ','),
        }

        key = request.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_checkout_private_key')
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

    # Detail sale order
    @validate_token
    @http.route('/api/sale_order/<int:id>', type='json', auth="none", methods=['POST'])
    def get_sale_order(self, id=-1):
        model = 'sale.order'
        user = request.env.user
        if not user or id < 1:
            return None

        pId = user.partner_id.id

        order = request.env[model].sudo().search(domain=[
            ['id', '=', id]
        ], limit=1)

        if not order:
            return None

        if order.partner_id.id != pId:
            return None

        # reload order để tính toán lại chi phí đối với đơn hàng KH chưa xác nhận
        if order.customer_confirmed == False:
            order.reload_order()

        order_line = []
        delivery_fee = 0
        for line in order.order_line:
            if line.is_delivery:
                delivery_fee += line.price_total
                continue    # chi tinh phi ship, ko add vao line de hien thi tren app
            if line.is_reward_line or line.is_loyalty_member_reward:
                continue
            if not line.product_id or not line.product_template_id:
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

        date_order = order.date_order + timedelta(hours=7)
        result = {
            'id': order.id,
            'name': order.name,
            'order_line': order_line,
            'amount_total': order.amount_total,
            'amount_reward': order.reward_amount,  # gia tri giam gia
            'delivery_fee': delivery_fee,  # phi van chuyen
            # 'delivery_fee': order.delivery_fee,  # phi van chuyen
            'order_date': date_order,
            'status': order.online_order_state,
            'delivery_status': 'draft',
            'payment_status': 'unpaid' if order.zalo_payment_state != 'paid' else 'paid',
            'customer_confirmed': order.customer_confirmed,
            # 'status': order.state, OLD

            # chua co field
            'note': '' if order.customer_note == False else order.customer_note,
            'payment_method': order.payment_method,
            'shipping_method': order.shipping_method,
            'delivery_address_id': -1 if (
                        not order.delivery_address_id or order.delivery_address_id.id < 1) else order.delivery_address_id.id,
        }

        return result

    # Update order line from cart
    @validate_token
    @http.route('/api/sale_order/update_items/<int:id>', type='json', auth="none", methods=['POST'])
    def update_items(self, id=-1):
        model = 'sale.order'

        user = request.env.user

        params = request.params

        result = {
            'success': False,
            'message': 'Cập nhật mặt hàng không thành công'
        }

        if not user:
            result['success'] = False
            result['message'] = 'Thông tin người dùng không hợp lệ'
            return result

        pId = user.partner_id.id

        order = request.env[model].sudo().search(domain=[
            ['id', '=', id]
        ], limit=1)

        if not order:
            result['success'] = False
            result['message'] = 'Không tìm thấy đơn hàng'
            return result

        if order.partner_id.id != pId:
            result['success'] = False
            result['message'] = 'Bạn không có quyền truy cập đơn hàng này'
            return result

        cart = params.get('cart', [])
        clear = len(cart) <= 0

        order.reload_order(cart=cart, clear=clear)

        return {
            'success': True,
            'message': 'Cập nhật mặt hàng thành công'
        }

    @validate_token
    @http.route('/api/sale_order/draft_unconfirmed', type='json', auth="none", methods=['POST'])
    def get_draft_unconfirmed_order(self):
        user = request.env.user
        if not user:
            return {'success': False, 'message': 'Thông tin người dùng không hợp lệ'}

        pId = user.partner_id.id
        if not pId:
            return {'success': False, 'message': 'Không có thông tin khách hàng'}

        model = 'sale.order'
        domain = [
            ['partner_id', '=', pId],            
            ['customer_confirmed', '=', False],
            ['online_order_state', '=', 'draft']
        ]

        order = request.env[model].sudo().search(domain, order='id asc', limit=1)
        order_id = order.id if order else -1

        return {
            'success': True,
            'id': order_id
        }



