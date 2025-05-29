# -*- coding: utf-8 -*-

from odoo import api,fields,models

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