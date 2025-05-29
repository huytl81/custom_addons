# -*- coding: utf-8 -*-

from odoo import api, fields, models
import base64


class AnitaTableSetting(models.TransientModel):
    '''
    awesome user setting
    '''
    _inherit = 'res.config.settings'

    virtual_scroll = fields.Boolean(string="Virtual Scroll", default=True)
    allow_user_config = fields.Boolean(string="Allow User Config", default=True)
    enable_anita_list_by_default = fields.Boolean(string="Enable Anita List", default=True)


    @api.model
    def get_values(self):
        '''
        get the vuales
        :return:
        '''
        res = super(AnitaTableSetting, self).get_values()
        config = self.env['ir.config_parameter'].sudo()

        virtual_scroll = config.get_param('anita_list_free.virtual_scroll')
        allow_user_config = config.get_param('anita_list_free.allow_user_config')
        enable_anita_list_by_default = config.get_param('anita_list_free.enable_anita_list_by_default')

        # get the favicon
        res.update({
            'virtual_scroll': virtual_scroll,
            'allow_user_config': allow_user_config,
            'enable_anita_list_by_default': enable_anita_list_by_default,
        })

        return res

    def set_values(self):
        '''
        set values
        :return:
        '''
        super(AnitaTableSetting, self).set_values()

        ir_config = self.env['ir.config_parameter'].sudo()

        ir_config.set_param("anita_list_free.virtual_scroll", self.virtual_scroll)
        ir_config.set_param("anita_list_free.allow_user_config", self.allow_user_config)
        ir_config.set_param("anita_list_free.enable_anita_list_by_default", self.enable_anita_list_by_default)
