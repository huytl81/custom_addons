from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    # payment method
    # selection
    # payment_method = fields.Selection([('cod', 'Thanh toán khi nhận hàng'), ('bank_transfer', 'Chuyển khoản')], default='cod')
    # shipping_method = fields.Selection([('delivery', 'Giao tận nơi'), ('go_to_shop', 'Tự đến lấy')], default='delivery')

    bank_qr = fields.Image('Bank QR code', store=True)
    zalo_app_qr = fields.Image('Zalo App QR code', store=True)
    zalo_app_link = fields.Char(string='Zalo App link')
    # link?
    # QR - image


    # title = fields.Char(string='Title')
    # description = fields.Html('Content')
    # publish_date = fields.Datetime(string='Publish date')
    # author = fields.Char(string='Author')
    # avatar = fields.Image('Avatar', store=True)
