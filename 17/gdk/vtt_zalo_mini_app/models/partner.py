from odoo import api, fields, models

import requests
import json
import base64

import datetime

import csv
from odoo.tools import file_open

class ResPartner(models.Model):
    _inherit = "res.partner"

    zalo_anonymous_id = fields.Char(string='Zalo anonymous id')             # dung de luu id KH khi KH gui tin nhan den OA, event: user_send_text, anonymous_send_text
    zalo_id_by_oa = fields.Char(string='Zalo id OA')             # user id by oa
    zalo_id = fields.Char(string='Zalo id App')             # user id by app
    zalo_name = fields.Char(string='Zalo name')
    zalo_picture = fields.Char(string='Zalo picture')

    is_default_address = fields.Boolean(default=False, string='Đ/c mặc định')   # dành cho type = delivery
    birth_day = fields.Date(string='Ngày sinh')
    birth_day_month = fields.Integer(string='Tháng sinh', compute='_compute_birth_day', store=True)
    birth_day_day = fields.Integer(string='Ngày sinh trong tháng')
    sex = fields.Selection([('male', 'Nam'), ('female', 'Nữ')], string=u'Giới tính', default='male')

    # follow oa
    followed_oa = fields.Boolean(default=False, string='Đã quan tâm OA')      # tương ứng với field user_is_follower của user zalo oa
    followed_oa_time = fields.Datetime(string='Thời gian quan tâm OA')               # Ghi nhận thời điểm follow, mặc định là None
    unfollowed_oa_time = fields.Datetime(string='Thời gian bỏ quan tâm OA')           # Ghi nhận thời điểm bỏ follow
    first_time_followed_oa = fields.Datetime(string='Thời gian ghi nhận quan tâm OA lần đầu') # Chỉ ghi nhận lần đầu

    last_interacted_time = fields.Datetime(string='Thời gian tương tác cuối cùng') # Ghi nhận thời điểm tương tác cuối cùng

    is_deleted = fields.Boolean(default=False)

    online_order_count = fields.Integer(string="Online Orders", compute='_compute_online_order_count', store=True)

    full_text_address = fields.Char(string='Địa chỉ đầy đủ', compute='_compute_full_address', store=True)

    

    # loyalty
    loyalty_tier_id = fields.Many2one(
        comodel_name='vtt.loyalty.tier',
        string="Hạng thẻ",   
        ondelete='set null'     
        # compute='_compute_tier',
        # store=True, readonly=False, required=True, precompute=True,
        # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]"
    )

    loyalty_points = fields.Float('Điểm tích lũy', default=0) # Tổng điểm tích lũy

    is_zalo_customer = fields.Boolean(string='Khách hàng Zalo', compute='_compute_is_zalo_customer', store=True)

    @api.depends('birth_day')
    def _compute_birth_day(self):
        for partner in self:
            if partner.birth_day:
                partner.birth_day_month = partner.birth_day.month
                partner.birth_day_day = partner.birth_day.day
            a = ''

    @api.depends('zalo_id', 'zalo_id_by_oa', 'zalo_anonymous_id')
    def _compute_is_zalo_customer(self):
        for partner in self:
            partner.is_zalo_customer = bool(partner.zalo_id or partner.zalo_id_by_oa or partner.zalo_anonymous_id)

    def _compute_online_order_count(self):
        for partner in self:
            partner.online_order_count = self.env['sale.order'].search_count([
                ('is_online_order', '=', True), 
                ('partner_id', '=', partner.id),
                # ('state', 'in', ['sale', 'done'])
            ])

    def action_view_online_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Online Orders',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'views': [(self.env.ref('vtt_zalo_mini_app.vtt_zalo_sale_order_tree').id, 'tree'), (False, 'form')],
            'domain': [('is_online_order', '=', True), ('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'default_is_online_order': True,
            },
        }
    

    def load_data(self):
        a = self
        b = 'a'

        # d = self.env['discuss.channel'].search([], limit=1)
        # m = d.message_post(
        #     body='Hello, this is a test message. <a href="https://vnexpress.net">Click here to view</a>',
        #     message_type='comment',
        #     subtype_xmlid='mail.mt_comment',
        #     # author_id=3,
        # )

        # c = ''
        company = self.env.company
        sale_order_id = 15  # The ID of your sale order
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        sale_order_url = f"{base_url}/web#id={sale_order_id}&model=sale.order&view_type=form"

        if company:
            channel = company.sale_discuss_channel_id
            if channel:
                channel_info = channel._channel_info()[0]
                members = channel.channel_partner_ids
                mess = {
                    'title': 'New Sale Order!',
                    'message': f'Click to view Sale Order SO{sale_order_id}',
                    'type': 'info',  # Can be 'info', 'warning', 'danger', 'success'
                    'sticky': True,
                    'links_u': [{
                        'label': f'SO{sale_order_id}',
                        'url': sale_order_url
                    }]
                } 
                notifications = []                
                for p in members:                     
                    notifications.append((
                        p, 'simple_notification_1', mess
                    ))
                if len(notifications) > 0:
                    self.env['bus.bus']._sendmany(notifications)


        # Simulate live data
        # live_data = {'id': 2, 'name': 'Live Data from Backend'}
        # # Send the live data to the frontend using the bus service
        # channel = "your_channel"
        # message = {
        #     "data": live_data,
        #     "channel": channel
        # }    
        # sale_order_id = 15  # The ID of your sale order
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        # sale_order_url = f"{base_url}/web#id={sale_order_id}&model=sale.order&view_type=form"
        # mess = {
        #     'title': 'New Sale Order!',
        #     'message': f'Click to view Sale Order SO{sale_order_id}',
        #     'type': 'info',  # Can be 'info', 'warning', 'danger', 'success'
        #     'sticky': True,
        #     'links_u': [{
        #         'label': f'SO{sale_order_id}',
        #         'url': sale_order_url
        #     }]
        # }    
        # self.env["bus.bus"]._sendone(self.env.user.partner_id, "simple_notification_1", mess)
        # # self.env["bus.bus"]._sendone(self.env.user.partner_id, "simple_notification_1", mess)
        # self.env["bus.bus"]._sendone(self.env['res.partner'].sudo().browse(29), "simple_notification_1", {
        #     'title': 'Live Data',
        #     'message': 'New live data has been received from the server <a href="vnexpress.net">Click here to view</a>',
        #     'sticky': True,
        # })
        return {'result': 'Live data sent successfully'}

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': "Warning head",
        #         'type': 'warning',
        #         'message': "This is the detailed warning",
        #         'sticky': True,
        #     },
        # }

        
        # b = getattr(self, 'name')
        # b = getattr(self, 'zalo_id')
        # c = 'c'

        # # Tạo kênh chat 1-1 với user có id là 8
        # # channel = self.env['mail.channel'].create({
        # #     'channel_partner_ids': [(4, 29), (4, 14)],
        # #     'public': 'private',
        # #     'channel_type': 'chat',
        # #     'name': 'Chat with User 14',
        # # })

        # partners = []
        # partners.append((
        #     0, 0, {
        #         'partner_id': 3,
        #         # 'product_uom_qty': item['qty']
        #     }
        # ))
        # partners.append((
        #     0, 0, {
        #         'partner_id': 29,
        #         # 'product_uom_qty': item['qty']
        #     }
        # ))

        # # channel = self.env['discuss.channel'].sudo().browse(8)
        

        # date = datetime.datetime.now()
        # # channel = self.env['discuss.channel'].sudo().create({'name': 'Name of Channel ' + date.strftime('%Y-%m-%d %H:%M:%S'),
        # # 'channel_type': 'channel',         
        # # # 'email_send': False, 
        # # # The user must join the group
        # # 'channel_partner_ids': [(4, 10)]})

        # cc = self.env['discuss.channel'].sudo().channel_create(name='Test Channel' + date.strftime('%Y-%m-%d %H:%M:%S'), group_id=None)

        # self.env['discuss.channel.member'].sudo().create({
        #     'channel_id': cc.id,
        #     'partner_id': 10,
        #     # 'is_member': True,
        # })

        # # this.pyEnv["bus.bus"]._sendone(partner, "discuss.channel/joined", {
        # #         channel: this._mockDiscussChannelChannelInfo([channel.id])[0],
        # #         invited_by_user_id: this.pyEnv.currentUserId,
        # #     });

        # # ccc = channel._channel_info()
        # # cccc = ccc[0]

        # notifications = []

        # # notifications.append((10, 'discuss.channel/joined', {
        # #     # 'channel': self.env.user.with_context(allowed_company_ids=self.env.user.company_ids.ids)._channel_info()[0],
        # #     channel: ccc,
        # #     'invited_by_user_id': self.env.user.id,
        # #     # 'open_chat_window': False,
        # # }))

        # # self.env['bus.bus']._sendmany(notifications)

        # # Gửi tin nhắn vào kênh chat vừa tạo
        # message = cc.message_post(
        #     body='Hello, this is a test message.',
        #     message_type='comment',
        #     subtype_xmlid='mail.mt_comment',
        #     author_id=10,
        #     from_zalo=True,
        # )

        # # message = self.env['mail.message'].create({
        # #     'model': 'res.users',  # Model liên quan (có thể là model khác nếu cần)
        # #     'res_id': 14,  # ID của người dùng nhận tin nhắn
        # #     'body': 'message_content he',  # Nội dung tin nhắn
        # #     'message_type': 'comment',  # Loại tin nhắn (comment, chat, email, ...)
        # #     'subtype_id': self.env.ref('mail.mt_comment').id,  # Subtype của tin nhắn
        # #     'partner_ids': [(6, 0, [29])], # Gán người nhận vào partner_ids
        # # })

        bb = ''

    def action_abc(self):
        p = self
        b = 'a'
        


        return True

    @api.depends('street', 'ward_id')
    def _compute_full_address(self):
        for partner in self:
            address = partner.street or ''
            if partner.ward_id:
                address = f"{address}, {partner.ward_id.name}, {partner.ward_id.district_id.name}, {partner.ward_id.district_id.state_id.name}"
            partner.full_text_address = address

    @api.onchange('ward_id')
    def _compute_address(self):
        for partner in self:
            if partner.ward_id:
                ward = partner.ward_id
                partner.country_id = ward.country_id
                partner.state_id = ward.state_id
                partner.district_id = ward.district_id                
            # partner.address = partner.ward_id.name

    @api.depends('name', 'phone')
    # @api.depends_context('input_full_display_name')
    def _compute_display_name(self):
        for partner in self:
            context = partner.env.context
            name = partner.name
            if partner.phone:
                name = f"{name} ({partner.phone})"
            partner.display_name = name                
        #     result.append((partner.id, name))
        # return result


    def add_zalo_tag(self):
        ab = self
        abc = 'a'

        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Zalo Tag',
            'res_model': 'partner.add.zalo.tag.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_tags_string': 'b',
                'default_shipping_price': 0,
                'default_partner_ids': self.ids,
                'active_ids': self.ids,
                'active_model': self._name,
            },
        }

    def toggle_extra_columns(self):
        action = self.env.ref('vtt_zalo_mini_app.action_view_partner_tree_with_loyalty_info').read()[0]
        context = self.env.context.copy()
        context['show_extra_columns'] = not context.get('show_extra_columns', False)
        action['context'] = context
        return action
