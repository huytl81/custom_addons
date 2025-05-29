from odoo import api, fields, models
import logging
from datetime import datetime, timedelta
import requests
import json

_logger = logging.getLogger(__name__)

class ZaloMessageCampaign(models.Model):
    _name = 'zalo.message.campaign'
    _description = 'Zalo Message Campaign'

    name = fields.Char(string='Campaign Name', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time')
    daily_send_time = fields.Selection(
        [(str(i), f'{i}:00') for i in range(24)],
        string='Daily Send Time',
        help='Time frame for daily message sending in hours', default='8'
    )
    # next_send_time = fields.Datetime(string='Next Send Time')    
    recipient_ids = fields.Many2many(
        'res.partner', 
        'zalo_message_campaign_recipient_rel', 
        'campaign_id', 
        'partner_id', 
        string='Recipients'
    )
    excluded_recipient_ids = fields.Many2many(
        'res.partner', 
        'zalo_message_campaign_excluded_recipient_rel', 
        'campaign_id', 
        'partner_id', 
        string='Excluded Recipients'
    )
    successful_recipients_count = fields.Integer(string='Successful Recipients', compute='_compute_successful_recipients')
    template_id = fields.Many2one('zalo.message.template', string='Template', domain="[('type', '=', 'oa_promotion')]", required=True)
    enable = fields.Boolean(string='Enable', default=False)
    recipient_condition = fields.Char(string='Recipient Condition', default='["&", ("followed_oa", "=", True), ("zalo_id_by_oa", "!=", False)]', help='Domain condition to filter recipients')
    campaign_type = fields.Selection([
        ('normal', 'Thông thường'),
        ('is_daily_birthday_campaign', 'Gửi tin sinh nhật hàng ngày')
    ], default='normal', string='Kiểu', required=True)

    today_execute_time = fields.Integer(string='Số lần chạy hôm nay', default=0)
    last_execute_time = fields.Datetime(string='Thời gian chạy cuối cùng')
    today_success_message_count = fields.Integer(string='Số tin nhắn thành công hôm nay', default=0)

    @api.depends('recipient_ids')
    def _compute_successful_recipients(self):
        for campaign in self:
            campaign.successful_recipients_count = len(campaign.excluded_recipient_ids)
    
    @api.onchange('recipient_condition')
    def _onchange_recipient_condition(self):
        if self.recipient_condition:
            condition_list = eval(self.recipient_condition)
            key_exists = any(item[0] == 'zalo_id_by_oa' for item in condition_list if isinstance(item, tuple))
            if not key_exists:
                condition_list.append(('zalo_id_by_oa', '!=', False))
                self.recipient_condition = str(condition_list)

    def _check_zalo_oa_token(self):
        oa_access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')

        headers = {
            'access_token': oa_access_token,
        }

        # call zalo api to get new token
        response = requests.post('https://openapi.zalo.me/v3.0/oa/user/getlist?data={"offset":0,"count":15,"last_interaction_period":"TODAY","is_follower":"true"}', headers=headers)

        success = True
        message = 'Access token valid'

        # save token
        if response.status_code == 200:
            data = json.loads(response.text)
            if 'error' in data.keys() and data['error'] != 0:
                success = False
                message = data['message']
        
        return success, message
    
    def _check_before_send(self, campaign_id=-1):
        check_access_token = self._check_zalo_oa_token()
        # check access_token
        if not check_access_token[0] or check_access_token[0] == False:
            log_vals = {
                'status': 'error',
                'error_message': check_access_token[1],
            }

            if campaign_id > 0:
                log_vals['campaign_id'] = campaign_id
        
            self.env['zalo.message.log'].sudo().create(log_vals)
            return False
        return True

    def action_send_zalo_messages(self, is_cron_job_execution=False):
        # lam dieu kien
        # check han muc (cho len dau tien)
        # check cac dieu kien de gui co ok ko: access_token, template_id, recipient_id
        # loai bo field recipient_id
        # bo sung field ngay ket thuc (khi nao den ngay se ko gui nua) -- Ok
        # Mỗi lần chạy sẽ check hạn mức, nếu hết hạn mức thì dừng lại -- Zalo ko cung cấp API để check hạn mức tin truyền thông
        # Bổ sung 

        
        # ...

        current_time = datetime.now()

        for campaign in self:
            # lam cron job de reset lai so lan chay va so tin nhan thanh cong
            # dua vao cron job chay 1 tiếng 1 lần
            if campaign.last_execute_time and campaign.last_execute_time.day != current_time.day:
                campaign.write({'today_execute_time': 0})
                campaign.write({'today_success_message_count': 0})
            
            if not campaign.template_id: continue            
            if is_cron_job_execution:
                # if campaign.enable == False: continue # da check o cron job roi
                if campaign.start_time < current_time: continue
                if campaign.end_time and current_time > campaign.end_time:                
                # if not campaign.template_id or campaign.enable == False or campaign.start_time < current_time or (campaign.end_time and current_time > campaign.end_time):
                    continue
            
            # check việc gửi đồng thời tạo log
            check = self._check_before_send(campaign.id)
            if not check:
                continue

            domain_string = campaign.recipient_condition or '[]'            
            domain = eval(domain_string)
            # can bo sung dk mac dinh OA id + followed OA
            # loai bo tat ca cac dieu kien lien quan den zalo_id_by_oa, followed_oa
            domain = [item for item in domain if not (isinstance(item, tuple) and (item[0] == 'zalo_id_by_oa') or item[0] == 'followed_oa')]            

            # add lai dk mac dinh
            domain.append(('zalo_id_by_oa', '!=', False))
            domain.append(('followed_oa', '!=', False))

            if campaign.campaign_type == 'is_daily_birthday_campaign':
                day = current_time.day
                month = current_time.month
                domain = [item for item in domain if not (isinstance(item, tuple) and (item[0] == 'birth_day_day') or item[0] == 'birth_day_month')] 
                domain.append(('birth_day_day', '=', day))
                domain.append(('birth_day_month', '=', month))                

            # check da va loai bo cac recipient da gui
            # if campaign.excluded_recipient_ids and len(campaign.excluded_recipient_ids.ids) > 0:
            #     ex_recipient_domain = ('id', 'not in', campaign.excluded_recipient_ids.ids)
            #     domain.append(ex_recipient_domain)                                        

            recipients_to_send = self.env['res.partner'].sudo().search(domain)

            for recipient in recipients_to_send:                
                result = campaign.template_id.send_oa_promotion_message(recipient, campaign.id) # phải bổ sung trả ra để xác định đã hết hạn mức chưa, nếu hết thì break vòng lặp luôn

                if result:
                    if result.get('status', '') == 'sent':
                        campaign.write({'excluded_recipient_ids': [(4, recipient.id)]})
                    else:
                        # nếu rơi vào error code của zalo thì break vòng lặp
                        # code -32: rate limit
                        # code -211: out of quota
                        # code -218: out of quota receive
                        if result.get('error_code', 0) in [-32, -211, -218]:
                            break

            campaign.write({'today_execute_time': campaign.today_execute_time + 1})
            campaign.write({'last_execute_time': current_time})
            count = self.env['zalo.message.log'].sudo().count_today_success_message(campaign.id)
            campaign.write({'today_success_message_count': count})


    def action_view_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Zalo Message Logs',
            'view_mode': 'tree',
            'res_model': 'zalo.message.log',
            'domain': [('campaign_id', '=', self.id)],
            'context': dict(self.env.context, create=False)
        }
    
    def action_activate(self):
        self.write({'enable': True})
        domain = [('id', 'in', self.recipient_ids.ids)]
        r = self.env['res.partner'].sudo().search(domain)
        bb = 'cc'


    def action_deactivate(self):
        self.write({'enable': False})

    # def action_view_recipients(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Zalo Message Logs',
    #         'view_mode': 'tree',
    #         'res_model': 'res.partner',
    #         'domain': [('campaign_id', '=', self.id)],
    #         'context': dict(self.env.context, create=False)
    #     }