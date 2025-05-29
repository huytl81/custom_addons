# -*- coding: utf-8 -*-
import requests

from odoo import api,fields,models
from odoo.tools import json


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    # zns
    zns_tmpl_payment_id = fields.Char('Payment template')

    def set_values(self):
        super().set_values()
        # odoo
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.odoo_account_api_key', self['odoo_account_api_key'])
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.odoo_auth_api_key', self['odoo_auth_api_key'])

        # # zalo oa
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_id', self['zalo_oa_id'])
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_secret_key', self['zalo_oa_secret_key'])
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_api_access_token',self['zalo_oa_api_access_token'])
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_oa_api_refresh_token',self['zalo_oa_api_refresh_token'])

        # # zalo app (super app)
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_app_id', self['zalo_app_id'])
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_app_secret_key', self['zalo_app_secret_key'])

        # # zalo mini app
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_mini_app_id', self['zalo_mini_app_id'])
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zalo_mini_app_checkout_private_key', self['zalo_mini_app_checkout_private_key'])

        # # zns
        # self.env['ir.config_parameter'].set_param('vtt_zalo_app.zns_tmpl_payment_id', self['zns_tmpl_payment_id'])


    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # odoo
        res['odoo_account_api_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_account_api_key')
        # res['odoo_auth_api_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.odoo_auth_api_key')

        # # zalo oa
        # res['zalo_oa_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_id')
        # res['zalo_oa_secret_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_secret_key')
        # res['zalo_oa_api_access_token'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_access_token')
        # res['zalo_oa_api_refresh_token'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_oa_api_refresh_token')

        # res['zalo_app_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_id')
        # res['zalo_app_secret_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_app_secret_key')
        # res['zalo_mini_app_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_id')
        # res['zalo_mini_app_checkout_private_key'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zalo_mini_app_checkout_private_key')

        # # zns
        # res['zns_tmpl_payment_id'] = self.env['ir.config_parameter'].sudo().get_param('vtt_zalo_app.zns_tmpl_payment_id')

        return res
    