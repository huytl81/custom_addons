from odoo import api, fields, models
from datetime import datetime, timedelta

class ZaloMessageLog(models.Model):
    _name = 'zalo.message.log'
    _description = 'Zalo Message Log'

    message_title = fields.Char(string='Message Title')
    template_id = fields.Many2one('zalo.message.template', string='Message Template')
    recipient_id = fields.Many2one('res.partner', string='Recipient')
    campaign_id = fields.Many2one('zalo.message.campaign', string='Campaign')
    status = fields.Selection([
        ('sent', 'Sent'),
        ('error', 'Error')
    ], string='Status', required=True)
    message_type = fields.Selection([
        ('normal', 'Tư vấn'),
        ('promotion', 'Truyền thông'),
        ('transaction', 'Giao dịch'),
    ], string='Message Type', required=True)
    error_code = fields.Char(string='Error Code')
    error_message = fields.Text(string='Error Message')
    phone = fields.Char(string='Phone')

    message_id = fields.Char(string='Message id') # message_id from Zalo API when Success



    def count_today_success_message(self, campaign_id):
        current_time = datetime.now()
        today = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        domain = [
            ('status', '=', 'sent'),
            ('create_date', '>=', today),
            ('create_date', '<', tomorrow)
        ]
        if campaign_id:
            domain.append(('campaign_id', '=', campaign_id))

        count = self.search_count(domain)        
        return count