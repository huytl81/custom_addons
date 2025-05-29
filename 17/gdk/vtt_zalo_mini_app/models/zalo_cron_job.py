# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json

import requests


from odoo import api,fields,models

class ZaloCronJob(models.Model):
    _name = 'zalo.cron.job'

    def send_campaign_message(self):
        # Lấy thời gian hiện tại và cộng thêm 7 giờ
        current_time = datetime.now() + timedelta(hours=7)
        
        # Trích xuất giờ theo khung 24h
        current_hour = current_time.strftime('%H')        
        
        campaigns = self.env['zalo.message.campaign'].sudo().search([
            ['enable', '=', True],
            ['start_time', '<', current_time],
            ['end_time', '>', current_time],
            ['daily_send_time', '=', current_hour]
        ])

        for campaign in campaigns:
            campaign.action_send_zalo_messages(is_cron_job_execution=True)

        
        # xu ly reset so lan chay
        current_day = current_time.day
        campaigns = self.env['zalo.message.campaign'].sudo().search([
            ['enable', '!=', False],            
        ])
        for campaign in campaigns:
            if campaign.last_execute_time and campaign.last_execute_time.day != current_day:
                campaign.write({'today_execute_time': 0})
                campaign.write({'today_success_message_count': 0})

    def get_new_zalo_token(self):
        config_model = 'ir.config_parameter'

        model = self.env[config_model].sudo()

        current_refresh_token = model.get_param('vtt_zalo_app.zalo_oa_api_refresh_token')
        app_secret_key = model.get_param('vtt_zalo_app.zalo_app_secret_key')
        app_id = model.get_param('vtt_zalo_app.zalo_app_id')   # ko phai mini app id

        success = False
        message = 'Failed'

        if not current_refresh_token or not app_id or not app_secret_key:
            message = 'Không có Refresh token hoặc App app (super app) hoặc App secret key'
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Get new Zalo OA Token Status',
                    'message': message,
                    'type': 'success' if success else 'danger',
                    'sticky': False,
                }
            }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'secret_key': app_secret_key,
        }

        data = {
            'refresh_token': current_refresh_token,
            'app_id': app_id,
            'grant_type': 'refresh_token',
        }

        # call zalo api to get new token
        response = requests.post('https://oauth.zaloapp.com/v4/oa/access_token', headers=headers, data=data)

        # save token
        if response.status_code == 200:
            data = json.loads(response.text)
            if 'error' in data.keys() and data['error'] != 0:
                success = False
                message = json.dumps(data)

            if 'access_token' in data.keys():
                access_token = data['access_token']
                refresh_token = data['refresh_token']

                model.set_param('vtt_zalo_app.zalo_oa_api_access_token', access_token)
                model.set_param('vtt_zalo_app.zalo_oa_api_refresh_token', refresh_token)

                success = True
                message = 'Success'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Get new Zalo OA Token Status',
                'message': message,
                'type': 'success' if success else 'danger',
                'sticky': False,
            }
        }

        ###GHN-OK
    # def check_ghn_order_status(self):
    #     # xac dinh order can cap nhat status
    #     # co ma ghn + status
    #     orders = self.env['sale.order'].sudo().search(domain=[
    #         ['ghn_order_code', '!=', None],
    #         '&',
    #         ['delivery_state', 'not in', ['done', 'cancel']],
    #         ['state', '=', 'sale']
    #     ])

    #     for order in orders:
    #         order.check_carrier_delivery_status()








