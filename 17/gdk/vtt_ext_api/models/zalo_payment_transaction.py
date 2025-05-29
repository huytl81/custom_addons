# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ZaloPaymentTransaction(models.Model):
    _name = "zalo.payment.transaction"

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string="Order Reference",
        required=True,
    )

    #
    amount = fields.Integer(string='Amount')
    method = fields.Char(string='Payment method')
    payment_order_id = fields.Char(string='Payment order id')
    trans_id = fields.Char(string='Transaction id')
    app_id = fields.Char(string='App id')
    extra_data = fields.Char(string='Extra data')
    result_code = fields.Integer(string='Result code')  # 1 = succ, -1 = fail
    message = fields.Char(string='Message')
    payment_channel = fields.Char(string='Payment channel')

    mac = fields.Char(string='Mac')
    overall_mac = fields.Char(string='Overall Mac')

    payment_create_mac = fields.Char(string='Mac for payment create order')
    data_to_create_mac = fields.Char(string='Json string data to create Mac')

    # check order status
    return_code = fields.Integer(string='Return code')  # Mã trả về khi check trạng thái
    trans_time = fields.Integer(string='Trans time')
    is_processing = fields.Boolean(string='Is processing', default=False)
    merchant_trans_id = fields.Integer(string='Merchant trans id')
    create_at = fields.Integer(string='Create at')
    update_at = fields.Integer(string='Update at')

    # auto chuyen trang thai don hang, phuc vu tam thoi cho case VNPAY
    # @api.onchange('result_code')
    # def _onchange_result_code_change_payment_status(self):
    #     if self.result_code != 1:
    #         return
    #     if not self.order_id or self.order_id < 1:
    #         return
    #
    #     order = self.env['sale.order'].sudo().browse(self.order_id.id)
    #     if not order or order.id < 1 or order.zalo_payment_state == 'paid':
    #         return
    #
    #     if not self.method or not self.payment_order_id or not self.trans_id or not self.app_id or self.extra_data or not self.message or not self.payment_channel or not self.mac or not self.overall_mac:
    #         return
    #
    #     order.write({'zalo_payment_state': 'paid'})






