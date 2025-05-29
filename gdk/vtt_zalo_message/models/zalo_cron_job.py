# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json

import requests

from odoo import api,fields,models

class ZaloCronJob(models.Model):
    _inherit = 'zalo.cron.job'

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

