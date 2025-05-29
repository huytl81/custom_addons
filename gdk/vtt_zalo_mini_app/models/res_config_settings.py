# -*- coding: utf-8 -*-
import requests

from odoo import api,fields,models
from odoo.tools import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    odoo_account_api_key = fields.Char('Username of account has key')
    odoo_auth_api_key = fields.Char('Odoo Auth API key')

    # zalo
    zalo_oa_id = fields.Char('Zalo OA id')
    zalo_oa_secret_key = fields.Char('Zalo OA secret key')
    zalo_app_id = fields.Char('Zalo App Id')
    zalo_app_secret_key = fields.Char('Zalo app secret key')                            # su dung cho phan auth
    zalo_mini_app_id = fields.Char('Zalo Mini App Id')
    zalo_mini_app_checkout_private_key = fields.Char('Zalo Mini App checkout private key')
    zalo_oa_api_access_token = fields.Char('Zalo OA API access token')
    zalo_oa_api_refresh_token = fields.Char('Zalo OA API refresh token')

    # zns
    zns_tmpl_payment_id = fields.Char('Payment template')

    def set_values(self):
        super().set_values()
        # odoo
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.odoo_account_api_key', self['odoo_account_api_key'])
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.odoo_auth_api_key', self['odoo_auth_api_key'])

        # zalo oa
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_id', self['zalo_oa_id'])
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_secret_key', self['zalo_oa_secret_key'])
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_api_access_token',self['zalo_oa_api_access_token'])
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_api_refresh_token',self['zalo_oa_api_refresh_token'])

        # zalo app (super app)
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_app_id', self['zalo_app_id'])
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_app_secret_key', self['zalo_app_secret_key'])

        # zalo mini app
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_mini_app_id', self['zalo_mini_app_id'])
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_mini_app_checkout_private_key', self['zalo_mini_app_checkout_private_key'])

        # zns
        self.env['ir.config_parameter'].set_param('vtt_zalo_app.zns_tmpl_payment_id', self['zns_tmpl_payment_id'])


    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # odoo
        res['odoo_account_api_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_account_api_key')
        res['odoo_auth_api_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_auth_api_key')

        # zalo oa
        res['zalo_oa_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_id')
        res['zalo_oa_secret_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_secret_key')
        res['zalo_oa_api_access_token'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')
        res['zalo_oa_api_refresh_token'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_refresh_token')

        res['zalo_app_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_id')
        res['zalo_app_secret_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_secret_key')
        res['zalo_mini_app_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_id')
        res['zalo_mini_app_checkout_private_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_checkout_private_key')

        # zns
        res['zns_tmpl_payment_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zns_tmpl_payment_id')

        return res

    def action_sync_zalo_oa_tags(self):        
        access_token = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')
        if not access_token:
            return []
        
        url = 'https://openapi.zalo.me/v2.0/oa/tag/gettagsofoa'
        headers = {'access_token': access_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:            
            data = response.json().get('data', [])
            if len(data) > 0:
                tags = self.env['vtt.zalo.oa.tag'].search([])
                tags.unlink()
                for tag in data:
                    self.env['vtt.zalo.oa.tag'].sudo().create({
                        'name': tag,                        
                    })

    def action_get_new_zalo_token(self):
        return self.env['zalo.cron.job'].sudo().get_new_zalo_token()

    def action_check_zalo_oa_token(self):

        config_model = 'ir.config_parameter'

        model = self.env[config_model].sudo()

        # current_refresh_token = model.get_param('vtt_zalo_app.zalo_oa_api_refresh_token')
        # app_secret_key = model.get_param('vtt_zalo_app.zalo_app_secret_key')
        # app_id = model.get_param('vtt_zalo_app.zalo_app_id')  # ko phai mini app id
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

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Zalo Token Status',
                'message': message,
                'type': 'success' if success else 'danger',
                'sticky': False,
            }
        }