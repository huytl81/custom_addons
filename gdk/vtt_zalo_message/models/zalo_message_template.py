import requests
from odoo import api, fields, models
from odoo.http import request
from datetime import date, datetime

class ZaloMessageTemplate(models.Model):
    _name = 'zalo.message.template'
    _description = 'Zalo Message Template'

    name = fields.Char(string='Name', required=True) # ten noi bo
    title = fields.Char(string='Title') # tieu de tin nhan
    content = fields.Text(string='Message Content')
    parameter_ids = fields.One2many('zalo.message.parameter', 'template_id', string='Parameters')
    table_vals = fields.One2many('zalo.message.table.vals', 'template_id', string='Table Values')
    image = fields.Binary(string='Image')
    button_ids = fields.One2many('zalo.message.button', 'template_id', string='Buttons')
    loyalty_program_id = fields.Many2one('loyalty.program', string='Voucher', domain=[('program_type', '=', 'coupons')])
    type = fields.Selection([
        # ('normal', 'Tin tư vấn OA'),
        ('oa_promotion', 'Tin truyền thông OA'),
        ('zns_transaction', 'Tin giao dịch ZNS')
    ], default='oa_promotion', string='Type', required=True)
    order_event = fields.Selection([
        ('customer_confirmed', 'Khách hàng đặt hàng'),
        ('order_paid', 'Khi khách hàng thanh toán'),
        ('order_confirmed', 'Khi xác nhận đơn hàng'),
        ('order_delivering', 'Khi bấm nút đang giao hàng'),
        ('order_done', 'Khi hoàn thành đơn hàng'),
        ('order_cancel', 'Khi đơn hàng bị hủy'),
    ], string='Gửi khi', default='order_confirmed')
    zns_template_id = fields.Char(string='ZNS Template ID')
    enable = fields.Boolean(string='Kích hoạt', default=False)
    # state = fields.Selection([
    #     ('chua_gui', 'Chưa gửi'),
    #     ('da_gui', 'Đã gửi')
    # ], string='Trạng thái', default='chua_gui', required=True)    


    def send_zns_transaction_message(self, order, event):
        # self.ensure_one()

        template = self.sudo().search([('type', '=', 'zns_transaction'), ('order_event', '=', event), ('enable', '=', True)], limit=1)

        if not template or not template.zns_template_id:
            return
        
        zns_template_id = template.zns_template_id
        
        if not order or not order.partner_id or not event:
            return
        
        partner = order.partner_id

        if not partner.phone:
            return

        # zns
        # zns_template_id = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zns_tmpl_payment_id')
        oa_access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')

        if not oa_access_token:
            return

        # order = self

                
        p_name = partner.name
        p_phone = partner.phone

        data = {}

        if p_phone:
            for param in template.parameter_ids:
                key = param.key
                p_name = param.value
                if param.data_model == 'partner':
                    value = getattr(partner, p_name)
                if param.data_model == 'order':
                    value = getattr(order, p_name)

                if value == False and p_name == 'date_order':
                    value = '---'

                if not type(value) == str:
                    if isinstance(value, datetime):
                        value = value.strftime('%H:%M:%S %d/%m/%Y')
                    elif isinstance(value, date):
                        value = value.strftime('%d/%m/%Y')
                    else:
                        value = str(value)
                if value == '':
                        value = '---'
                data[key] = value
            
            headers = {
                'access_token': oa_access_token,
                'Content-Type': 'application/json',
            }

            json_data = {
                'mode': 'development',
                'phone': p_phone,
                'template_id': zns_template_id,
                'template_data': data
            }

            response = requests.post('https://business.openapi.zalo.me/message/template', headers=headers, json=json_data) 
            error_code = 0
            error_message = ''
            template_id = self.id
            partner_id = partner.id
            status = 'error'
            message_id = None     

            if response.status_code == 200:
                error_code = response.json().get('error', 0)            
                if error_code != 0:
                    error_message = response.json().get('message', '')
                else:
                    status = 'sent'
                    message_id = response.json().get('message_id', None)                                                                
                    
            else:
                error_code = response.json().get('error', 0)
                error_message = response.json().get('message', '')

            template_id = template.id

            log_vals = {
                'message_title': self.name,
                'template_id': template_id,
                'recipient_id': partner_id,
                'phone': p_phone,
                # 'campaign_id': campaign_id,
                'status': status,
                'error_code': error_code,
                'error_message': error_message,
                'message_type': 'transaction',
                # 'message_id': message_id
            }
                

            if message_id:
                log_vals['message_id'] = message_id

            self.env['zalo.message.log'].sudo().create(log_vals)
            b = 'ccc'
            
            
            if status == 'sent':
                return {
                    'status': 'sent',
                    'message_id': message_id,
                    'error_code': error_code,
                    'error_message': error_message
                }   
            return {
                'status': 'error',
                'error_code': error_code,
                'error_message': error_message
            }   

                

    def send_oa_promotion_message(self, recipient, campaign_id=-1):
        error = {'status': 'error', 'template_id': self.id}
        if campaign_id > 0:
            error['campaign_id'] = campaign_id        
        if not recipient or not recipient.zalo_id:
            error['error_code'] = 100001
            error['error_message'] = 'Recipient does not have Zalo ID'
            return error
        
        zalo_id = recipient.zalo_id

        # chuyen doi ra template message
        title = self.title
        content = self.content

        # Lấy URL của website hiện tại
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if 'localhost' in base_url:
            image_url = "https://singchiak.saletop.vn/web/binary/company_logo"
        else:
            image_url = f"{base_url}/web/image/zalo.message.template/{self.id}/image"

        card = None

        if self.loyalty_program_id:
            vals = {
                'program_id': self.loyalty_program_id.id,
                'points': self.loyalty_program_id.init_points,  # lay tu chuong trinh
                # 'expiration_date': '',  # lay tu program
                'partner_id': recipient.id,
            }
            card = self.env['loyalty.card'].create(vals)
            if not card:
                error['error_code'] = 100002
                error['error_message'] = 'Tạo voucher thất bại'
                return error            
          
        # lay du lieu tuong ung
        params = []
        for param in self.parameter_ids:
            key = param.key
            value = param.value            
            if param.data_model == 'partner':
                if param.value == 'loyalty_tier_id':
                    value = getattr(recipient.loyalty_tier_id, 'name')
                    if value == False:
                        value = '---'
                else:
                    value = getattr(recipient, param.value)                
            if param.data_model == 'loyalty':                
                value = getattr(self.loyalty_program_id, param.value)            
            if param.data_model == 'voucher':                                                    
                if not card:
                    error['error_code'] = 100003
                    error['error_message'] = 'Không tìm thấy voucher'
                    return error
                value = getattr(card, param.value)                
            
            if value == False and param.value == 'expiration_date':
                value = '---'            

            if not type(value) == str:
                if isinstance(value, datetime):
                    value = value.strftime('%d/%m/%Y %H:%M:%S')
                elif isinstance(value, date):
                    value = value.strftime('%d/%m/%Y')
                else:
                    value = str(value)
            if value == '':
                    value = '---'
            
            content = content.replace(key, value)
            title = title.replace(key, value)            

            

        # table_vals
        table_vals = []
        for val in self.table_vals:
            label = val.key
            value = val.value
            for param in self.parameter_ids:
                p_key = param.key
                p_val = param.value
                if param.data_model == 'partner':
                    if param.value == 'loyalty_tier_id':
                        p_val = getattr(recipient.loyalty_tier_id, 'name')
                        if p_val == False:
                            p_val = '---'
                    else:
                        p_val = getattr(recipient, param.value)
                if param.data_model == 'loyalty':                
                    p_val = getattr(self.loyalty_program_id, param.value)    
                if param.data_model == 'voucher':                                                                        
                    if not card:
                        error['error_code'] = 100003
                        error['error_message'] = 'Không tìm thấy voucher'
                        return error
                    p_val = getattr(card, param.value)   
                
                if p_val == False and param.value == 'expiration_date':
                    p_val = '---'

                # checktype va convert
                if not type(p_val) == str:
                    if isinstance(p_val, datetime):
                        p_val = '' if p_val == False else p_val.strftime('%d/%m/%Y %H:%M:%S')
                    elif isinstance(p_val, date):
                        p_val = '' if p_val == False else p_val.strftime('%d/%m/%Y')
                    else:
                        p_val = str(p_val)    
                if p_val == '':
                    p_val = '---'
                value = value.replace(p_key, p_val)
            table_vals.append({
                'key': label,
                'value': value
            })

        
        # button
        buttons = []
        for button in self.button_ids:
            payload = button.action_value
            if button.action_type == 'oa.open.url':
                payload = {
                    'url': button.action_value
                }
            if button.action_type == 'oa.open.sms':
                payload = {
                    'content': 'Xin chào',
                    'phone_code': button.action_value
                }
            if button.action_type == 'oa.open.phone':
                payload = {                    
                    'phone_code': button.action_value
                }
            buttons.append({
                'title': button.name,
                'type': button.action_type,
                'payload': payload
            })



        access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')        
        # access_token = 'N_UNJbTBpmXQzv50KKhD1rdubKvHKivjDBsBIqHWhquKjvrm7GQXKN33yMqfDUnwQlNZQWSbltCEcBv5VdZk1N29tpibMliX9ekd1tGskXyUmQTUT3FwQHVT_obhDADk2T-eN7aQYG07sAWUU6IXC1g_e1XlOviu6ugG0N1vja41aBHsM52NO36XoN124lOi8FFoR2esh31evAzr6mAATdN3bt1yThHUDuE9Ipe-ZLzjzvLY6nkuHMJ8fcmC9VTNL_UoS5ivb4inrivEOJN3KsF0xXK_3BKMIyMh53ukYGPS-wyV93UN2YVSiKWlDf5CKT-LOWeAn7fHryavNHhA9rx1sX4x8_ObPTIcOJSrYNn5_9H29n-vTad4ebqBAhvqHEMlTZWabLXcxyeR31l39NwevNanQjnFEeHeSL5Tp0a'
        url = 'https://openapi.zalo.me/v3.0/oa/message/promotion'
        headers = {
            'access_token': access_token,
            'Content-Type': 'application/json'
        }
        data = {
            'recipient': {'user_id': zalo_id},
            'message': {
            'attachment': {
            "type": "template",
            # tach phan nay
            "payload": {
                "template_type": "promotion",
                # tach phan nay
                "elements": [
                    #  link co dinh
                    {
                        "image_url": image_url,
                        "type": "banner"
                    },
                    # su dung phan nay
                    {
                        "type": "header",
                        "content": title
                    },
                    # su dung phan nay
                    {
                        "type": "text",
                        "align": "left",
                        "content": content
                    },
                    # de du lieu fix cung
                    # from table_vals
                    # chuyen doi thanh dang string het
                    {
                        "type": "table",
                        "content": table_vals
                        # "content": [
                        #     {
                        #         "value": "VC09279222",
                        #         "key": "Voucher"
                        #     },
                        #     {
                        #         "value": "30/12/2023",
                        #         "key": "Hạn sử dụng"
                        #     }
                        # ]
                    },
                    # de du lieu fix cung
                    {
                        "type": "text",
                        "align": "center",
                        "content": "Áp dụng tất cả cửa hàng trên toàn quốc"
                    }
                ],
                # tach phan na
                "buttons": buttons
                # "buttons": [
                #     {
                #         "title": "Tham khảo chương trình",
                #         "image_icon": "",
                #         "type": "oa.open.url", 
                #         "payload": { 
                #            "url": "https://oa.zalo.me/home" 
                #         }
                #     },
                #     # {
                #     #     "title": "Liên hệ chăm sóc viên",
                #     #     # "image_icon": "aeqg9SYn3nIUYYeWohGI1fYRF3V9f0GHceig8Ckq4WQVcpmWb-9SL8JLPt-6gX0QbTCfSuQv40UEst1imAm53CwFPsQ1jq9MsOnlQe6rIrZOYcrlWBTAKy_UQsV9vnfGozCuOvFfIbN5rcXddFKM4sSYVM0D50I9eWy3",
                #     #     "type": "oa.query.hide",
                #     #     "payload": "#tuvan"
                #     # }
                # ]
            }
            }
            }
        }

        # return 'acb'

        response = requests.post(url, headers=headers, json=data)
        error_code = 0
        error_message = ''
        template_id = self.id
        recipient_id = recipient.id
        status = 'error'
        message_id = None                

        if response.status_code == 200:
            error_code = response.json().get('error', 0)            
            if error_code != 0:
                error_message = response.json().get('message', '')
            else:
                status = 'sent'
                message_id = response.json().get('message_id', None)                                                                
                
        else:
            error_code = response.json().get('error', 0)
            error_message = response.json().get('message', '')

        log_vals = {
            'message_title': self.name,
            'template_id': template_id,
            'recipient_id': recipient_id,
            # 'campaign_id': campaign_id,
            'status': status,
            'error_code': error_code,
            'error_message': error_message,
            'message_type': 'promotion',
            # 'message_id': message_id
        }
            

        if message_id:
            log_vals['message_id'] = message_id

        if campaign_id > 0:
            log_vals['campaign_id'] = campaign_id

        self.env['zalo.message.log'].sudo().create(log_vals)
        b = 'ccc'
        json = response.json()
        # return response.json()
        if status == 'sent':
            return {
                'status': 'sent',
                'message_id': message_id,
                'error_code': error_code,
                'error_message': error_message
            }
        return {
            'status': 'error',
            'error_code': error_code,
            'error_message': error_message
        }

    def action_activate(self):
        # Search for all templates with type = 'zns_transaction' and order_event = self.order_event
        templates = self.search([('type', '=', 'zns_transaction'), ('order_event', '=', self.order_event)])
        # Set enable to False for all found templates
        templates.write({'enable': False})
        # Activate the current template
        self.write({'enable': True})

    def action_deactivate(self):
        self.write({'enable': False})