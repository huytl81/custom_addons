# -*- coding: utf-8 -*-
import json

import requests

from odoo import api,fields,models

class ZaloCronJob(models.Model):
    _name = 'zalo.cron.job'

    def get_new_zalo_token(self):
        config_model = 'ir.config_parameter'

        model = self.env[config_model].sudo()

        current_refresh_token = model.get_param('vtt_zalo_app.zalo_oa_api_refresh_token')
        app_secret_key = model.get_param('vtt_zalo_app.zalo_app_secret_key')
        app_id = model.get_param('vtt_zalo_app.zalo_app_id')   # ko phai mini app id

        if not current_refresh_token or not app_id or not app_secret_key:
            return

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
            if 'access_token' in data.keys():
                access_token = data['access_token']
                refresh_token = data['refresh_token']

                model.set_param('vtt_zalo_app.zalo_oa_api_access_token', access_token)
                model.set_param('vtt_zalo_app.zalo_oa_api_refresh_token', refresh_token)

    def check_ghn_order_status(self):
        # xac dinh order can cap nhat status
        # co ma ghn + status
        orders = self.env['sale.order'].sudo().search(domain=[
            ['ghn_order_code', '!=', None],
            '&',
            ['delivery_state', 'not in', ['done', 'cancel']],
            ['state', '=', 'sale']
        ])

        for order in orders:
            order.check_carrier_delivery_status()








