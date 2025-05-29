# -*- coding: utf-8 -*-

from odoo import api, fields, models
import requests

class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    oa_customer_id = fields.Many2one('res.partner', string='OA customer', ondelete='set null')     # luu khi KH gui nhan tin tu OA

    is_sale_channel = fields.Boolean('Is sale channel', default=False)

    def set_default_sale_channel(self, channel):
        channel.is_sale_channel = True
        channels = self.env['discuss.channel'].search([('id', '!=', channel.id)])
        for c in channels:
            c.is_sale_channel = False
        # company = self.env.company
        # company.sale_discuss_channel_id = channel_id

    # ghe de gui tin nhan cho KH OA
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, body=None, subject=None, message_type='notification', subtype_id=False, **kwargs):        

        from_zalo = False
        author_id = -1
        product_id = -1
        product_name = 'Ảnh sản phẩm'



        # xác định trên api
        if message_type == 'comment':
            b = ''
            product_id = kwargs.get('product_id', -1)
            from_zalo = kwargs.get('from_zalo', False)
            author_id = kwargs.get('author_id', -1)
            if author_id <= 0 and product_id > 0:
                user = self.env.user
                author_id = user.partner_id.id

            # gan KH cho kenh
            if not self.oa_customer_id and from_zalo and author_id > 0:
                author = self.env['res.partner'].sudo().search([('id', '=', author_id)], limit=1)
                if author:
                    self.oa_customer_id = author.id
            
        product = self.env['product.template'].sudo().search([('id', '=', 157)], limit=1)

        if 'attachment_ids' in kwargs:
            attachment_ids = kwargs['attachment_ids']

            if attachment_ids and len(attachment_ids):
                attachment = self.env['ir.attachment'].sudo().search([('id', '=', attachment_ids[0])], limit=1)

                cccs = ''        

        image_url = None

        if product_id > 0:
            body = '[ Đã gửi ảnh SP: ' + kwargs.get('product_name', 'Ảnh sản phẩm ' + str(product_id)) + ']'         
            product_name = kwargs.get('product_name', 'Ảnh sản phẩm ' + str(product_id))
            image_url = kwargs.get('product_url', None)            

        kwargs.pop('product_id', None)
        kwargs.pop('product_url', None)
        kwargs.pop('product_name', None)

        if kwargs.get('author_id', -1) <= 0 and author_id > 0:
            kwargs['author_id'] = author_id
            # author_id = kwargs.get('author_id', -1)

        res = super(DiscussChannel, self).message_post(body=body, subject=subject, message_type=message_type, subtype_id=subtype_id, **kwargs)

        # code gửi tin tư vấn tới KH
        # gui tin tu van

        recipient = self.env['res.partner'].sudo().search([('id', '=', 7)], limit=1)

        # self._send_oa_normal_message(recipient, body)             


        if self.oa_customer_id and self.oa_customer_id.id != author_id:

            if self.oa_customer_id.zalo_id_by_oa or self.oa_customer_id.zalo_anonymous_id:
                # recipient = self.oa_customer_id.zalo_id_by_oa or self.oa_customer_id.zalo_anonymous_id
                mess_to_oa = body
                if image_url:
                    mess_to_oa = product_name
                
                if recipient:
                    self._send_oa_normal_message(recipient, mess_to_oa, image_url)


                # gui tin nhan
                # luu vao message log
                a = ''
            # check xem co oa id ko
            # check xem last interact la khi nao
            # gui tin nhan va luu vao message log
            a = ''


        b = ''        

        return res
    
    def _send_oa_normal_message(self, recipient, message, image_url=None):
        # gui tin nhan

        oa_access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')

        # product
        # product = self.env['product.template'].search([('id', '=', 202)], limit=1)
        # attachment = product.image_1920
        # file_data = base64.b64decode(attachment)
        # file_name = attachment.name

        image = 'http://singchiak.saletop.vn/image/product/202'
        if image_url:
            image = image_url

        if 'localhost:8084' in image:
            image = image.replace('localhost:8084', 'http://singchiak.saletop.vn')

        # files = {
        #     'file': (product.id, file_data, 'application/octet-stream')  # Hoặc content-type phù hợp
        # }

        # headers = {
        #     'access_token': oa_access_token,
        #     # 'Content-Type': 'application/json',
        # }

        # response_f = requests.post('https://openapi.zalo.me/v2.0/oa/upload/file', headers=headers, files=files)        

        # if response_f.status_code == 200:
        #     error_code = response_f.json().get('error', 0)            
        #     if error_code != 0:
        #         error_message = response_f.json().get('message', '')
        #     else:
        #         status = 'sent'
        #         message_id = response_f.json().get('message_id', None)                                                                
                
        # else:
        #     error_code = response_f.json().get('error', 0)
        #     error_message = response_f.json().get('message', '')
        
        headers = {
            'access_token': oa_access_token,
            'Content-Type': 'application/json',
        }

        id = recipient.zalo_id_by_oa or recipient.zalo_anonymous_id
        # id = '2306852411774416859'

        if '<br>' in message:
            message = str(message)

        message = message.replace('<br>', '\n')
        # message = message.replace('b', 'z')
        # message = 'Tin tu van: \n Hello'

        message_data = {
            "text": message,
        }

        if image_url:
            message_data['attachment'] = {
                "type": "template",
                "payload": {
                    "template_type": "media",
                    "elements": [{
                        "media_type": "image",
                        "url": image
                    }]
                }
            }

        json_data = { 
            "recipient":{
                "user_id": id
            },
            "message": message_data
        }
        

        response = requests.post('https://openapi.zalo.me/v3.0/oa/message/cs', headers=headers, json=json_data)        

        error_code = 0
        error_message = ''
        # template_id = self.id
        partner_id = recipient.id
        status = 'error'
        message_id = None  
        data = None

        if response.status_code == 200:
            error_code = response.json().get('error', 0)            
            if error_code != 0:
                error_message = response.json().get('message', '')
            else:
                status = 'sent'
                message_id = response.json().get('message_id',None)        
                data = response.json().get('data', None)
                if data:
                    message_id = data.get('message_id',None)                                   
                
        else:
            error_code = response.json().get('error', 0)
            error_message = response.json().get('message', '')

        log_vals = {
            'message_title': 'Tin nhắn tư vấn',
            # 'template_id': template_id,
            'recipient_id': partner_id,            
            # 'campaign_id': campaign_id,
            'status': status,
            'error_code': error_code,
            'error_message': error_message,
            'message_type': 'normal',
            # 'message_id': message_id
        }
            

        if message_id:
            log_vals['message_id'] = message_id

        self.env['zalo.message.log'].sudo().create(log_vals)