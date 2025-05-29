from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # payment method
    # selection
    customer_confirmed = fields.Boolean('Customer confirmed', default=False)
    # customer_cancel = fields.Boolean('Customer cancel', default=False)

    # state thong bao cho customer
    state_for_customer = fields.Selection([
        #chưa thanh toán - chờ xác nhận (nv - sale) - đang xử lý - đang giao hàng - đã giao - đã hủy
        # d

        ('draft', 'Mới'),
        ('unconfirm', 'Chờ xác nhận'),  # khi kh da confirm - nv chua xac nhan
        ('processing', 'Đang xử lý'),   # status khi nv xác nhận đơn (sale)
        ('delivering', 'Đang giao hàng'), # status (nv chủ động bấm chuyển trạng thái)
        ('done', 'Đã hoàn thành'),
        ('cancel', 'Đã hủy'),
    ], compute='_compute_state_for_customer')

    # state thong bao cho nhan vien
    # tree: payment_state, payment_method, shipping_method, state for em
    # state: Mới - Chưa giao hàng - Đang giao hàng - Đã giao hàng - Hoàn thanh - Đã
    # Tạm thời xử lý kết hợp state đơn giản bao gồm: mới - Đã xác nhận - Hoàn thành - Đã hủy. Kết hợp hiển thị
    state_for_employee = fields.Selection([
        ('draft', "Mới"),
        ('sale', "Đã xác nhận"),
        ('done', "Hoàn thành"),
        ('cancel', "Cancelled"),
    ], compute='_compute_state_for_employee')

    # payment state tren zalo
    # kich ban: Nv se check va thao tac thu cong (manual) de chuyen trang thai
    zalo_payment_state = fields.Selection([
        ('unpaid', 'Chưa thanh toán'),
        ('paid', 'Đã thanh toán'),
    ], default='unpaid')

    # zalo_shipping_state = fields.Selection([
    #     ('unpaid', 'Chưa thanh toán'),
    #     ('paid', 'Đã xác nhận'),
    # ], default='unpaid')

    payment_method = fields.Selection([
        ('cod', 'Thanh toán khi nhận hàng'),
        ('bank', 'Chuyển khoản'),
        ('vnpay', 'VNPAY'),
        ('vnpay_sandbox', 'VNPAY SANDBOX'),
        ('cod_sandbox', 'COD SANDBOX'),
        ('bank_sandbox', 'BANK SANDBOX'),
    ], default='cod')
    shipping_method = fields.Selection([
        ('delivery', 'Giao tận nơi'),
        ('go_to_shop', 'Tự đến lấy')
    ], default='delivery')

    delivery_address_id = fields.Many2one(
        comodel_name='res.partner',
        string="Delivery address",
        # required=True, change_default=True, index=True,
        # tracking=1,
        domain="[('type', '=', 'delivery')]")

    # diem nhan dc
    redeem_points = fields.Float('Loyalty points', default=0)
    delivery_fee = fields.Float('Delivery fee', compute='_compute_delivery_fee')

    # is online order:
    # phuc vu de filter o backend do hien tai o tren app khi bam mua hang la tao don luon roi
    is_online_order = fields.Boolean('Is online order', default=False)
    is_show_for_employee = fields.Boolean('Is online order', store=True, compute='_compute_show_for_employee')


    # payment transaction - mini app payment
    payment_transaction = fields.One2many(
        comodel_name='zalo.payment.transaction',
        inverse_name='order_id',
        string="Payment transaction",
    )

    def apply_loyalty_reward(self):
        self.ensure_one()

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

    @api.onchange('partner_id')
    def _onchange_parter_change_delivery_address(self):
        if self.partner_id:
            abc = '123'
            bb = 11
            for child in self.partner_id.child_ids:
                abbc = 11
                bb = child
                if child.is_default_address and child.type == 'delivery':
                    self.delivery_address_id = child.id
                cc = 11

    @api.depends('order_line')
    def _compute_delivery_fee(self):
        for order in self:
            delivery_amount = 0
            for line in order.order_line:
                if not line.is_delivery_fee_line:
                    continue
                delivery_amount += line.price_subtotal
            order.delivery_fee = delivery_amount

    # ghi de compute_reward_total (sale_loyalty/models/sale_order.py)
    @api.depends('order_line')
    def _compute_reward_total(self):
        for order in self:
            reward_amount = 0
            for line in order.order_line:
                #_me customize:
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

    @api.depends('state', 'is_online_order', 'customer_confirmed')
    def _compute_show_for_employee(self):
        for sale in self:
            sale.is_show_for_employee = True
            state = sale.state
            confirm = sale.customer_confirmed
            is_online_order = sale.is_online_order
            if is_online_order == True and state == 'draft' and confirm == False:
                sale.is_show_for_employee = False



    @api.depends('state', 'customer_confirmed')
    def _compute_state_for_customer(self):
        # self.ensure_one()
        for sale in self:
            state = sale.state
            confirm = sale.customer_confirmed
            # cus_cancel = sale.customer_cancel
            if state == 'cancel':
                sale.state_for_customer = 'cancel'
            elif state == 'sale':
                sale.state_for_customer = 'processing'
            elif confirm == True and state in ('draft', 'sent'):
                sale.state_for_customer = 'unconfirm'   # cus confirmed - chờ nv confirm
            # con trang thai: delivering + done
            else:
                sale.state_for_customer = 'draft'

    @api.depends('state', 'zalo_payment_state', 'customer_confirmed')
    def _compute_state_for_employee(self):
        # self.ensure_one()
        for sale in self:
            state = sale.state
            confirm = sale.customer_confirmed
            # cus_cancel = sale.customer_cancel
            if state == 'cancel':
                sale.state_for_employee = 'cancel'
            elif state == 'sent':
                sale.state_for_employee = 'draft'
            elif state == 'sale':
                sale.state_for_employee = 'sale'
            else:
                sale.state_for_employee = 'draft'

    def action_confirm(self):
        # if self.is_online_order == True and self.payment_method in ('vnpay', 'vnpay_sandbox'):
        #     if self.zalo_payment_state == 'unpaid':
        #         raise UserError(_(
        #             ""
        #         ))
        res = super().action_confirm()
        # chuyen trang thai don hang -> paid
        if self.is_online_order == True:
            self.zalo_payment_state = 'paid'

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
        return res

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

        return res

