from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    bank_qr = fields.Image('Bank QR code', store=True)
    zalo_app_qr = fields.Image('Zalo App QR code', store=True)
    zalo_app_link = fields.Char(string='Zalo App link')

    customer_support_ids = fields.Many2many(
        'res.users', 
        string='Nhân viên CSKH',
        domain=[('share', '=', False)]  # Chỉ chọn người dùng nội bộ
    )

    customer_support_partner_ids = fields.Char(string='Id nhân viên CSKH', help='Danh sách id nhân viên CSKH, cách nhau bởi dấu phẩy', compute='_compute_customer_support_partner_ids', store=True)

    sale_discuss_channel_id = fields.Many2one(
        comodel_name='discuss.channel',
        string='Kênh thông báo - Bán hàng',
        help='Kênh thông báo dành cho các hoạt động bán hàng',                
    )

    @api.depends('customer_support_ids')
    def _compute_customer_support_partner_ids(self):
        for company in self:
            company.customer_support_partner_ids = ','.join(str(user.partner_id.id) for user in company.customer_support_ids)
            self.env['ir.config_parameter'].set_param('vtt_zalo_app.company_customer_support_partner_ids', company.customer_support_partner_ids)
    
    # @api.depends('sale_discuss_channel_id')
    # def _compute_sale_discuss_channel_id(self):
    #     for company in self:
    #         self.env['discuss.channel'].set_default_sale_channel(self.sale_discuss_channel_id.id)

    def write(self, values):
        is_change_sale_discuss_channel_id = False
        channel_id = 0
        if 'sale_discuss_channel_id' in values:
            channel_id = values['sale_discuss_channel_id']
            if channel_id and channel_id > 0 and self.sale_discuss_channel_id.id != channel_id:
                is_change_sale_discuss_channel_id = True

        result = super().write(values)

        if is_change_sale_discuss_channel_id and channel_id > 0:            
            self.env['discuss.channel'].set_default_sale_channel(self.sale_discuss_channel_id)        
        


        return result
    # @api.onchange('sale_discuss_channel_id')
    # def _onchange_sale_discuss_channel_id(self):
    #     self.env['discuss.channel'].set_default_sale_channel(self.sale_discuss_channel_id.id)
    # link?
    # QR - image

    # default_delivery_carrier = fields.Many2one(
    #     comodel_name='delivery.carrier',
    #     string="Default delivery carrier for online order",
    #     # domain=[
    #     #     ('type', '=', 'service'),
    #     # ],
    #     help="Delivery carrier auto apply for online order",
    #     check_company=True,
    # )


    # title = fields.Char(string='Title')
    # description = fields.Html('Content')
    # publish_date = fields.Datetime(string='Publish date')
    # author = fields.Char(string='Author')
    # avatar = fields.Image('Avatar', store=True)
