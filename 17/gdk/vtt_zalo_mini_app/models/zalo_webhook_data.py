from odoo import api, fields, models

# model chỉ phục vụ chứa dữ liệu từ webhook của zalo
class ZaloWebhookData(models.Model):
    _name = "zalo.webhook.data"

    signature = fields.Char(string='X-ZEvent-Signature')
    data = fields.Char(string="Hot news")
    
