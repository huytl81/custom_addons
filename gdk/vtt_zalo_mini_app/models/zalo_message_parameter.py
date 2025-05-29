from odoo import api, fields, models

class ZaloMessageParameter(models.Model):
    _name = 'zalo.message.parameter'
    _description = 'Zalo Message Parameter'

    key = fields.Char(string='Key', required=True)
    value = fields.Char(string='Value', compute='_compute_value_and_data_model', store=True)
    type = fields.Selection([
        # ('normal', 'Tin tư vấn OA'),
        ('oa_promotion', 'Tin truyền thông OA'),
        ('zns_transaction', 'Tin giao dịch ZNS')
    ], default='oa_promotion', string='Type')
    # customer_selected_field = fields.Selection([
    #     ('partner-name', '[Khách hàng] Tên khách hàng'),
    #     ('partner-loyalty_tier_id', '[Khách hàng] Hạng thẻ'),
    #     ('partner-loyalty_points', '[Khách hàng] Điểm tích lũy'),
    #     ('partner-phone', '[Khách hàng] Số điện thoại'),
    # ], default=None, string='Trường thông tin khách hàng')
    # order_selected_field = fields.Selection([
    #     ('order-name', '[Đơn hàng] Mã đơn hàng'),
    #     ('order-date_order', '[Đơn hàng] Ngày đặt hàng'),
    #     ('order-amount_total', '[Đơn hàng] Tổng tiền'),
    #     ('order-online_order_state', '[Đơn hàng] Trạng thái'),
    #     ('order-redeem_points', '[Đơn hàng] Điểm tích lũy'),
    #     ('order-delivery_fee', '[Đơn hàng] Phí vận chuyển'),
    #     ('order-full_text_delivery_address', '[Đơn hàng] Địa chỉ giao hàng'),
    # ], default=None, string='Trường thông tin đơn hàng')
    data_from = fields.Selection([
        ('partner-name', '[Khách hàng] Tên khách hàng'),
        ('partner-loyalty_tier_id', '[Khách hàng] Hạng thẻ'),
        ('partner-loyalty_points', '[Khách hàng] Điểm tích lũy'),
        ('partner-phone', '[Khách hàng] Số điện thoại'),
        # ('loyalty-name', '[Voucher] Tên chương trình'),
        # ('loyalty-description', '[Voucher] Mô tả'),
        # ('voucher-code', '[Voucher] Mã voucher'),
        # ('voucher-expiration_date', '[Voucher] Ngày hết hạn'),
        ('order-name', '[Đơn hàng] Mã đơn hàng'),
        ('order-date_order', '[Đơn hàng] Ngày đặt hàng'),
        ('order-amount_total', '[Đơn hàng] Tổng tiền'),
        ('order-online_order_state', '[Đơn hàng] Trạng thái'),
        ('order-redeem_points', '[Đơn hàng] Điểm tích lũy'),
        ('order-delivery_fee', '[Đơn hàng] Phí vận chuyển'),
        ('order-full_text_delivery_address', '[Đơn hàng] Địa chỉ giao hàng'),
    ], default='partner-name', string='Trường thông tin', required=True)
    data_model = fields.Selection([
        ('none', 'None'),
        ('partner', 'Partner'),
        # ('loyalty', 'Loyalty'),
        # ('voucher', 'Voucher'),
        ('order', 'Order'),
    ], string='Data model', compute='_compute_value_and_data_model', store=True, default='none')
    template_id = fields.Many2one('zalo.message.template', string='Template', ondelete='cascade')

    def write(self, values):
                
        # if 'customer_selected_field' in values:
        #     values['data_from'] = values['customer_selected_field']
        #     values['order_selected_field'] = None
        # elif 'order_selected_field' in values:
        #     values['data_from'] = values['order_selected_field']     
        #     values['customer_selected_field'] = None       

        result = super().write(values)    
        


        return result
        

    @api.depends('data_from')
    def _compute_value_and_data_model(self):
        for record in self:
            if record.data_from:
                parts = record.data_from.split('-')
                if len(parts) == 2:
                    record.data_model = parts[0]
                    record.value = parts[1]
                else:
                    record.data_model = 'none'
                    record.value = ''
            else:
                record.data_model = 'none'
                record.value = ''

    @api.model
    def create(self, values):
        # if 'customer_selected_field' in values:
        #     values['data_from'] = values['customer_selected_field']
        #     values['order_selected_field'] = None
        # elif 'order_selected_field' in values:
        #     values['data_from'] = values['order_selected_field']     
        #     values['customer_selected_field'] = None   

        if 'template_id' not in values and self.env.context.get('default_template_id'):
            values['template_id'] = self.env.context['default_template_id']
        return super(ZaloMessageParameter, self).create(values)