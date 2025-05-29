import datetime
import requests

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import json

class SaleOrder(models.Model):
    _inherit = "sale.order"

    # payment method
    # selection
    customer_confirmed = fields.Boolean('Khách hàng xác nhận', default=False)
    # customer_cancel = fields.Boolean('Customer cancel', default=False)

    customer_note = fields.Char('Ghi chú của khách hàng')

    online_order_state = fields.Selection([
        ('draft', 'Mới'),
        ('processing', 'Đang xử lý'),   # status khi nv xác nhận đơn (sale)
        ('delivering', 'Đang giao hàng'), # status (nv chủ động bấm chuyển trạng thái)
        ('done', 'Đã hoàn thành'),
        ('cancel', 'Đã hủy'),
    ], default='draft')

    # payment state tren zalo
    # kich ban: Nv se check va thao tac thu cong (manual) de chuyen trang thai
    zalo_payment_state = fields.Selection([
        ('unpaid', 'Chưa thanh toán'),
        ('paid', 'Đã thanh toán'),
    ], default='unpaid')

    payment_method = fields.Selection([
        ('COD', 'Thanh toán khi nhận hàng'),
        ('BANK', 'Chuyển khoản'),
        ('VNPAY', 'VNPAY'),
        ('VNPAY_SANDBOX', 'VNPAY SANDBOX'),
        ('COD_SANDBOX', 'COD SANDBOX'),
        ('BANK_SANDBOX', 'BANK SANDBOX'),
    ], default='COD')

    shipping_method = fields.Selection([
        ('delivery', 'Giao tận nơi'),
        ('go_to_shop', 'Tự đến lấy')
    ], default='delivery')

    # state su dung cho employee? xem cac state cua ben GiaoHangNhanh
    delivery_state = fields.Selection([
        ('draft', 'Chưa giao hàng'),
        ('processing', 'Đang xử lý'),
        ('delivering', 'Đang giao hàng'),
        ('done', 'Đã giao hàng'),
        ('cancel', 'Đã hủy'),
    ], default='draft')

    delivery_address_id = fields.Many2one(
        comodel_name='res.partner',
        string="Giao tới",
        # required=True, change_default=True, index=True,
        # tracking=1,
        domain="['&', ('type', '=', 'delivery'), ('parent_id', '=', partner_id)]")

    # diem nhan dc
    redeem_points = fields.Float('Điểm tích lũy', default=0)
    delivery_fee = fields.Float('Phí ship', compute='_compute_delivery_fee')

    # is online order:
    # phuc vu de filter o backend do hien tai o tren app khi bam mua hang la tao don luon roi
    is_online_order = fields.Boolean('Đơn hàng online', default=False)
    is_show_for_employee = fields.Boolean('Show for employee', store=True, compute='_compute_show_for_employee')

    # sau khi xong nv se tick done
    done_status = fields.Boolean('Is done', default=False)

    full_text_delivery_address = fields.Char('Địa chỉ giao hàng')




    # payment transaction - mini app payment
    payment_transaction = fields.One2many(
        comodel_name='zalo.payment.transaction',
        inverse_name='order_id',
        string="Payment transaction",
    )

    # refresh order: Phục vụ cho các đơn hàng online đặt hàng thông qua API sẽ cập nhật lại đơn hàng khi KH chưa xác nhận đơn (customer_confirmed = False)
    def reload_order(self, cart=[], clear=False):

        has_cart = len(cart) > 0

        temp = []

        # case KH cập nhật lại giỏ hàng
        if has_cart or clear:
            for line in self.order_line:
                line.unlink()

            for item in cart:
                p_id = item['product_id']
                qty = item['qty']
                if p_id <= 0 or qty <= 0:
                    continue

                product = self.env['product.product'].sudo().search(domain=[
                    ['product_tmpl_id', '=', p_id]
                ], limit=1)

                if not product:
                    continue

                temp.append((
                    0, 0, {
                        'order_id': self.id,
                        'product_id': product.id,
                        'product_uom_qty': qty
                    }
                    )
                )
        else:
            # case reload lại đơn hàng khi KH vào xem lại đơn chưa xác nhận (api get order)
            # lấy ds sp, remove phí ship, loyalty reward
            for line in self.order_line:
                # check line có phải loyalty hay phí ship ko, neu true -> loai bo
                # is_reward_line is_loyalty_member_reward is_delivery
                if line.is_delivery or line.is_loyalty_member_reward or line.is_reward_line:
                    continue
                if line.product_id and line.product_id.id > 0 and line.product_uom_qty > 0:
                    temp.append((
                        0, 0, {
                            # 'order_id': self.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty
                        }
                        )
                    )
                    line.unlink()

        # add sp
        if len(temp) > 0:
            # self.env['sale.order.line'].sudo().create(temp)
            self.sudo().write({'order_line': temp})

        if clear == False:
            self.reapply_shipping_fee()
            self.apply_loyalty_reward()




        # tính toán lại chi phí vận chuyển, loyalty




    # @api.onchange('order_line', 'partner_id')
    # def _onchange_recompute_loyalty_reward(self):
    #     if self.is_online_order:
    #         self.apply_loyalty_reward()

    # apply loyalty reward theo hang the thanh vien (chuc nang danh cho backend)
    def apply_loyalty_reward(self):
        # du kien code de tinh toan apply loyalty reward theo hang the thanh vien
        # self.ensure_one()

        for line in self.order_line:
            if line.is_loyalty_member_reward:
                line.unlink()

        if not self.partner_id or self.amount_total <= 0:
            return

        discount_product = self.company_id.sale_discount_product_id

        if not discount_product:
            self.company_id.sale_discount_product_id = self.env['product.product'].sudo().create({
                'name': _('Discount'),
                'type': 'service',
                'invoice_policy': 'order',
                'list_price': 0.0,
                'company_id': self.company_id.id,
                'taxes_id': None,
                }
            )
            discount_product = self.company_id.sale_discount_product_id

        loyalty_cards = self.env['loyalty.card'].sudo().search(domain=[
            '&',
            ['partner_id', '=', self.partner_id.id],
            ['program_type', '=', 'loyalty']
        ])

        if loyalty_cards and len(loyalty_cards) > 0:
            cards = []
            for c in loyalty_cards:
                if c.program_id.auto_apply == True and c.program_id.loyalty_tier_ids and len(
                        c.program_id.loyalty_tier_ids) > 0:
                    cards.append(c)

            for card in cards:
                # tinh toan va ap dung cac phan thuong theo tier cua card
                if card.tier_id and card.tier_id.tier_reward_ids and len(card.tier_id.tier_reward_ids) > 0:
                    for reward in card.tier_id.tier_reward_ids:
                        if reward.value > 0 and reward.value_type:
                            amount = reward.value
                            if reward.value_type == 'percent':
                                amount = self.amount_total / 100 * reward.value
                            vals = {
                                'order_id': self.id,
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
                            self.env['sale.order.line'].sudo().create(vals)

        abc = '123'
        bb = 1
        # self._update_programs_and_rewards()
        # claimable_rewards = self._get_claimable_rewards()
        # if len(claimable_rewards) == 1:
        #     coupon = next(iter(claimable_rewards))
        #     if len(claimable_rewards[coupon]) == 1:
        #         self._apply_program_reward(claimable_rewards[coupon], coupon)
        #         return True
        # elif not claimable_rewards:
        #     return True
        # return self.env['ir.actions.actions']._for_xml_id('sale_loyalty.sale_loyalty_reward_wizard_action')



    # ghi de code module vtt_ghn_intergration
    # bo sung de xu ly code amount dua tren payment_method COD, BANK, VNPAY (xac dinh tien thu ho)
    ###GHN-OK dc su dung o module vtt_ghn_intergration > action_confirm nen khi chua cai dat vtt_ghn_intergration thi se ko can
    # def create_ghn_order(self):
    #     self.ensure_one()

    #     if self.carrier_id.delivery_type != 'ghn_shipping':
    #         return {}

    #     # request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create"
    #     request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create"
    #     ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
    #     ghn_shop_id = self.warehouse_id.ghn_shop_id
    #     if ghn_shop_id and ghn_token:
    #         headers = {
    #             'Content-type': 'application/json',
    #             'Token': ghn_token,
    #             'shop_id': ghn_shop_id
    #         }
    #     else:
    #         raise UserError(_('The GHN Token or shop_id is not valid.'))

    #     if not self.required_note:
    #         raise UserError(_('Delivery Note is required.'))
    #     if not self.payment_type:
    #         raise UserError(_('Payment Option is required.'))
    #     note = ''
    #     service_fee = 0.0
    #     is_reward_discount = False
    #     is_reward_free_ship = False
    #     for line in self.order_line:
    #         if line.display_type:
    #             note = note + line.name +'\n'
    #         if line.is_delivery:
    #             service_fee = service_fee + line.price_subtotal
    #         """
    #         if line.is_reward_line:
    #             applied_programs = self._get_applied_programs_with_rewards_on_current_order()
    #             if applied_programs:
    #                 for applied_program in applied_programs:
    #                     if applied_program.reward_type == 'free_shipping':
    #                         self.write({'payment_type': '1'})  # seller pay
    #                         is_reward_free_ship = True
    #                     else:
    #                         # self.write({'payment_type': '2'})    # buyer pay
    #                         is_reward_discount = True
    #         """

    #     if (not is_reward_free_ship and not is_reward_discount) or (not is_reward_free_ship and is_reward_discount):
    #         cod_amount = self.amount_total - service_fee
    #     else:
    #         cod_amount = self.amount_total

    #     # cod ghi de: bo sung de xu ly tinh tien thu ho
    #     if self.zalo_payment_state == 'paid' or self.payment_method in ['BANK', 'VNPAY', 'BANK_SANDBOX', 'VNPAY_SANDBOX']:
    #         cod_amount = 0

    #     insurance_value = 0.0
    #     for line in self.order_line:
    #         if line.product_id.product_tmpl_id.sale_ok:
    #             insurance_value = insurance_value + line.price_subtotal

    #     return_phone = ''
    #     company_phone = self.env.user.company_id.partner_id.phone
    #     if company_phone:
    #         return_phone = ''.join(filter(lambda i: i.isdigit(), company_phone.replace('+84', '0')))
    #     to_phone = ''
    #     partner_shipping_phone = self.partner_shipping_id.phone
    #     if partner_shipping_phone:
    #         to_phone = ''.join(filter(lambda i: i.isdigit(), partner_shipping_phone.replace('+84', '0')))
    #     else:
    #         if self.partner_id.phone:
    #             to_phone = ''.join(filter(lambda i: i.isdigit(), self.partner_id.phone.replace('+84', '0')))
    #         else:
    #             raise UserError(_('Please provide recipient contact phone/ mobile.'))

    #     if cod_amount > 5000000:
    #         raise UserError(_('Order > 5tr'))

    #     data = {
    #         "payment_type_id": int(self.payment_type),    # who pay the ship, free ship = 1 (seller pay)
    #         "note": note,
    #         "required_note": self.required_note,
    #         "return_phone": return_phone,         # only 10 numbers
    #         "return_address": self.warehouse_id.partner_id.street,
    #         "return_district_id": self.warehouse_id.partner_id.district_id.ghn_district_id,
    #         "return_ward_code": self.warehouse_id.partner_id.ward_id.ghn_ward_id,
    #         "client_order_code": "",
    #         "to_name": self.partner_id.name,
    #         "to_phone": to_phone,
    #         "to_address": self.partner_shipping_id.street,
    #         "to_ward_code": self.partner_shipping_id.ward_id.ghn_ward_id,
    #         "to_district_id": self.partner_shipping_id.district_id.ghn_district_id,
    #         "cod_amount": int(cod_amount),
    #         "content": self.name,
    #         "weight": self.weight,
    #         "height": self.height,
    #         "length": self.length,
    #         "width": self.width,
    #         "pick_station_id": 0,
    #         "insurance_value": int(insurance_value),
    #         "service_id": 0,
    #         "service_type_id": int(self.carrier_id.service)     # Input value 1: Express , 2: Standard or 3: Saving (if not input service_id) => But only Standard
    #     }
    #     req = requests.post(request_url, data=json.dumps(data), headers=headers)
    #     req.raise_for_status()
    #     content = req.json()
    #     return content

    @api.model_create_multi
    def create(self, values):
        # override:
        # - Thay đổi partner_shipping_id theo delivery_address_id
        # - Bổ sung để tính phí

        for input in values:
            if 'is_online_order' in input.keys() or input['is_online_order'] != True:
                if 'delivery_address_id' in input.keys() and input['delivery_address_id'] > 0:
                    input['partner_shipping_id'] = input['delivery_address_id']

        order = super(SaleOrder, self).create(values)
        if order:
            order._change_full_text_delivery_address()
        return order

    # Ham cap nhat cac dia chi nam trong pham vi GHN cung cap dich vu (dia ban GHN hoat dong)
    # 2024/10/08 - Hiện tại dùng để cập nhật tạm thời, sau có thể tách riêng ra 1 tính năng để cập nhật lại các địa chỉ mà GHN cung cấp dịch vụ
    # def update_ghn_location_service_status(self):
    #     # m_state = 'res.country.state'
    #     # m_district = 'res.district'
    #     m_ward = 'res.ward'
    #
    #     wards = self.env[m_ward].sudo().search(domain=[
    #         ['country_id', '=', 241]
    #     ])
    #
    #     for ward in wards:
    #         ward.state_id.ghn_allowed = True
    #         ward.district_id.ghn_allowed = True
    #         ward.ghn_allowed = True

    ###GHN-OK cap nhat trang thai van chuyen (phuc vu ca cron job + btn check trang thai)
    # def check_carrier_delivery_status(self):
    #     if self.ghn_order_code:
    #         request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/detail"
    #         ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
    #         # ghn_shop_id = self.warehouse_id.ghn_shop_id
    #         if ghn_token:
    #             headers = {
    #                 'Content-type': 'application/json',
    #                 'Token': ghn_token,
    #                 # 'shop_id': ghn_shop_id
    #             }
    #         else:
    #             raise UserError(_('The GHN Token or shop_id is not valid.'))

    #         data = {
    #             'order_code': self.ghn_order_code,
    #         }

    #         req = requests.post(request_url, data=json.dumps(data), headers=headers)
    #         req.raise_for_status()
    #         content = req.json()

    #         if 'data' in content:
    #             status = content['data']['status']

    #             if status == 'delivering':
    #                 self.online_order_state = 'delivering'
    #                 self.delivery_state = 'delivering'
    #             if status == 'delivered':
    #                 self.delivery_state = 'done'
                # if status in ['delivery_fail', '']

    # apply_shipping_method
    # -> default
    # -> ghn

    ###GHN-OK
    def apply_shipping_method(self):
        # xu ly tinh phi ship cho don hang
        # warehouse = self.warehouse_id.partner_id

        from_location = self.company_id
        # try:
        #     if self.warehouse_id and self.warehouse_id.partner_id:
        #         from_location = self.warehouse_id
        # except Exception as e:
        #     a = ''

        warehouse = from_location.partner_id


        if not warehouse or not warehouse.district_id or not warehouse.ward_id \
                or not self.partner_shipping_id or not self.partner_shipping_id.district_id or not self.partner_shipping_id.ward_id:
            return

        from_district = warehouse.district_id
        from_ward = warehouse.ward_id

        to_district = self.partner_shipping_id.district_id
        to_ward = self.partner_shipping_id.ward_id

        if not from_district or not from_ward or not to_district or not to_ward:
            return

        carrier = self.env['delivery.carrier'].sudo().search(domain=[
            ['is_default_for_online_order', '=', True]
        ], limit=1)

        if carrier:
            ###GHN-OK
            if carrier and carrier.delivery_type == 'ghn_shipping':
                ab = ''
                # ghn_from_district_id = from_district.ghn_district_id
                # ghn_from_ward_id = from_ward.ghn_ward_id

                # ghn_to_district_id = to_district.ghn_district_id
                # ghn_to_ward_code = to_ward.ghn_ward_id

                # if ghn_from_district_id < 1 or ghn_to_district_id < 1 or not ghn_from_ward_id or not ghn_to_ward_code:
                #     return

                # carrier = self.env['delivery.carrier'].sudo().search(domain=[
                #     ['is_default_for_online_order', '=', True]
                # ], limit=1)

                # self._apply_ghn_shipping_method(carrier, ghn_from_district_id, ghn_from_ward_id, ghn_to_district_id, ghn_to_ward_code)
            else:
                # apply default shipping method
                self._apply_default_shipping_method(carrier, to_ward)


    def _apply_default_shipping_method(self, carrier, to_ward):
        shipping_fee = 0
        if to_ward:
            shipping_fee = to_ward.default_shipping_method_price
        self.set_delivery_line(carrier, shipping_fee)


    # ap phi van chuyen
    ###GHN-OK
    # def _apply_ghn_shipping_method(self, carrier, from_district_id, from_ward_id, to_district_id, to_ward_code):
    #     if carrier:
    #         service_type_id = int(carrier.service)
    #         if service_type_id <= 0:
    #             return

    #         # cal phi ship tam tinh
    #         request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee"
    #         ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
    #         if ghn_token:
    #             headers = {
    #                 'Content-type': 'application/json',
    #                 'Token': ghn_token,
    #             }
    #         else:
    #             raise UserError(_('Please recheck GHN Token.'))



    #         if not from_district_id and not from_ward_id:
    #             raise UserError(_('Please recheck store address (district/ ward).'))

    #         if not service_type_id:
    #             raise UserError(_('Please choose service type.'))

    #         if not to_district_id and not to_ward_code:
    #             raise UserError(_('Please recheck address information (district/ ward) of recipient.'))
    #         if not self.required_note:
    #             raise UserError(_('The Delivery Note is required.'))
    #         if not self.payment_type:
    #             raise UserError(_('The Payment Note is required.'))

    #         # amount_total = self.product_sale_ok_amount_total()  # is total price of product's sale_ok

    #         amount_total = 0
    #         for line in self.order_line:
    #             if line.product_id.product_tmpl_id.sale_ok:
    #                 amount_total = amount_total + line.price_subtotal

    #         if amount_total > GHN_MAX_INSURANCE_FEE:
    #             raise UserError(
    #                 _('The GHN Shipping method is only available for order under or equal 10.000.000 VND, by GNH policy.'))

    #         height = 1
    #         length = 1
    #         weight = 1
    #         width = 1

    #         data = {
    #             "from_district_id": from_district_id,
    #             "from_ward_id": from_ward_id,
    #             "service_type_id": service_type_id,
    #             "to_district_id": to_district_id,
    #             "to_ward_code": to_ward_code,
    #             "height": height,
    #             "length": length,
    #             "weight": weight,
    #             "width": width,
    #             "insurance_fee": int(amount_total),
    #             "coupon": None
    #         }
    #         req = requests.post(request_url, data=json.dumps(data), headers=headers)
    #         req.raise_for_status()
    #         content = req.json()

    #         ghn_fee = 0
    #         if 'data' in content:
    #             # content['data']['insurance_fee'] = data['insurance_fee']
    #             ghn_fee = content['data']['total']


    #         ### check ok -> add line
    #         if weight <= 0:
    #             raise UserError(_('Package weight must be greater than 0.'))
    #         if weight and height and length and width:
    #             if not height and not length and not width:
    #                 raise UserError(_('Please provide weight or size of delivery package.'))
    #             if carrier.service:
    #                 if ghn_fee:
    #                     if amount_total > PHI_KHAI_GIA:
    #                         ghn_fee = ghn_fee + (amount_total / 100) * 0.5
    #                     self.set_delivery_line(carrier, ghn_fee)
    #                     # self.write({
    #                     #     'recompute_delivery_price': False,
    #                     #     'delivery_message': self.delivery_message,
    #                     #     'required_note': self.required_note,
    #                     #     'payment_type': self.payment_type
    #                     # })

    def reapply_shipping_fee(self):
        for line in self.order_line:
            if not line.is_delivery:
                continue
            line.unlink()

        self.apply_shipping_method()

    @api.onchange('partner_id')
    def _onchange_parter_change_delivery_address(self):
        if self.partner_id and self.is_online_order == True:
            for child in self.partner_id.child_ids:
                bb = child
                if child.is_default_address and child.type == 'delivery':
                    self.delivery_address_id = child.id
                    # p = self.partner_shipping_id
                    # self.partner_shipping_id = self.delivery_address_id
                    pp = ''

    @api.onchange('delivery_address_id')
    def _onchange_change_partner_shipping(self):
        if self.delivery_address_id and self.is_online_order == True:
            self.partner_shipping_id = self.delivery_address_id.id
            self._change_full_text_delivery_address()
            # self.update({'partner_shipping_id': self.delivery_address_id.id})
            pp = ''

    @api.depends('order_line')
    def _compute_delivery_fee(self):
        for order in self:
            delivery_amount = 0
            for line in order.order_line:
                if not line.is_delivery_fee_line:
                    continue
                delivery_amount += line.price_subtotal
            order.delivery_fee = delivery_amount

    # ghi de (override) compute_reward_total (sale_loyalty/models/sale_order.py)
    # bo sung phan tinh gia tri giam gia order line reward theo hang the thanh vien
    @api.depends('order_line')
    def _compute_reward_total(self):
        for order in self:
            reward_amount = 0
            for line in order.order_line:
                #_me customize:
                if line.is_delivery:
                    continue
                if line.is_loyalty_member_reward:
                    reward_amount += line.price_subtotal
                #_me - end
                if not line.reward_id:
                    continue
                if line.reward_id.reward_type != 'product':
                    reward_amount += line.price_subtotal
                else:
                    # Free product are 'regular' product lines with a price_unit of 0
                    reward_amount -= line.product_id.lst_price * line.product_uom_qty
            order.reward_amount = reward_amount

    @api.depends('state', 'customer_confirmed', 'zalo_payment_state', 'payment_method')
    def _compute_show_for_employee(self):
        for sale in self:
            is_online_order = sale.is_online_order
            if is_online_order == False:
                continue

            sale.is_show_for_employee = False

            state = sale.state
            cus_confirm = sale.customer_confirmed
            zalo_payment_state = sale.zalo_payment_state
            payment_method = sale.payment_method

            if cus_confirm == False:
                sale.is_show_for_employee = False
                continue

            # cod
            if payment_method in ['COD', 'COD_SANDBOX']:
                sale.is_show_for_employee = True
                continue

            # payment_method in ['VNPAY','BANK'] + SANDBOX
            if zalo_payment_state == 'paid':
                sale.is_show_for_employee = True
                continue

    # chuyen online_order_state -> processing
    # 2024-08-29: Khi NV bam Xac nhan thi chuyen trang thai processing luon
    # def action_processing(self):
    #     # co gui tin ZNS o buoc nay ko
    #     if self.online_order_state == 'draft':
    #         self.online_order_state = 'processing'

    # chuyen online_order_state -> delivering

    # khi KH xac nhan
    def customer_confirm(self):
        self.customer_confirmed = True
        self.date_order = datetime.datetime.now()
        self._change_full_text_delivery_address()

    def action_delivering(self):
        # co gui tin ZNS o buoc nay ko
        if self.online_order_state not in ['done', 'cancel']:
            self.online_order_state = 'delivering'

    def action_done(self):
        if self.online_order_state != 'cancel':
            if self.state != 'sale':
                self.action_confirm()
            self.online_order_state = 'done'

    def action_paid(self):
        if self.zalo_payment_state != 'paid':
            self.zalo_payment_state = 'paid'

    def action_confirm(self):
        res = super().action_confirm()

        self.online_order_state = 'processing'
        self.customer_confirmed = True
        self._change_full_text_delivery_address()

        # load cac uu dai de tinh points nhan dc tu don hang
        coupon_id = -1
        ammount_change = 0
        for coupon, change in self._get_point_changes().items():
            if coupon.program_type == 'loyalty' and coupon.program_id.auto_apply == True and coupon.partner_id.id == self.partner_id.id:
                coupon_id = coupon.id
                ammount_change = change
            # coupon.points += change
        # self._send_reward_coupon_mail()
        if coupon_id > 0:
            c = self.env['loyalty.card'].sudo().browse(coupon_id)
            if c and c.id > 0:
                point = c.level_points + self.amount_total
                # point = c.level_points + ammount_change
                c.level_points = 0 if not c.level_points else c.level_points
                success = c.write({'level_points': point})
                if success:
                    # ghi nhan redeem point nhan dc vao don hang (phuc vu cho phan lich su tich diem)
                    self.redeem_points = ammount_change

        # send zns
        self.action_send_zns_payment()

        return res

    # hàm lấy full text d/c giao hàng
    def _change_full_text_delivery_address(self):
        address = ''
        if self.delivery_address_id and self.delivery_address_id.ward_id:
            street = self.delivery_address_id.street
            ward = self.delivery_address_id.ward_id
            if ward.state_id and ward.district_id:
                district = ward.district_id
                state = ward.state_id
                address = ', '.join((street, ward.name, district.name, state.name))
        self.full_text_delivery_address = address

    # send zns thông báo đặt hàng thành công
    def action_send_zns_payment(self):
        # zns
        zns_template_id = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zns_tmpl_payment_id')
        oa_access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')

        order = self

        if order.partner_id and zns_template_id and oa_access_token:
            partner = order.partner_id
            p_name = partner.name
            p_phone = partner.phone

            if p_phone:
                if order.date_order:
                    date_order = order.date_order.strftime('%H:%M:%S %d/%m/%Y')
                    amount = str(order.amount_total)

                    headers = {
                        'access_token': oa_access_token,
                        'Content-Type': 'application/json',
                    }

                    json_data = {
                        'mode': 'development',
                        'phone': p_phone,
                        'template_id': zns_template_id,
                        'template_data': {
                            'date_order': date_order,
                            'name': p_name,
                            'amount_total': amount,
                            'order_code': order.name,
                        },
                    }

                    response = requests.post('https://business.openapi.zalo.me/message/template', headers=headers, json=json_data)

    def _action_cancel(self):
        previously_confirmed = self.filtered(lambda s: s.state == 'sale')

        coupon_id = -1
        ammount = self.amount_total
        for coupon, changes in previously_confirmed._get_point_changes().items():
            if coupon.program_type == 'loyalty' and coupon.program_id.auto_apply == True and coupon.partner_id.id == self.partner_id.id:
                coupon_id = coupon.id
                # ammount_change = changes
        res = super()._action_cancel()
        # total = 0
        # xoa redeem point
        self.redeem_points = 0
        if coupon_id > 0:
            c = self.env['loyalty.card'].sudo().browse(coupon_id)
            if c and c.id > 0:
                point = 0 if c.level_points - ammount <= 0 else c.level_points - ammount
                c.level_points = 0 if not c.level_points else c.level_points
                c.write({'level_points': point})

        self.online_order_state = 'cancel'

        return res

    def action_draft(self):
        res = super().action_draft()

        self.online_order_state = 'draft'

        return res