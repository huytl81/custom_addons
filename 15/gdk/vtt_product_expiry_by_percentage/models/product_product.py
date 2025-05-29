# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vtt_use_time_percentage = fields.Float('Best Before Time',
                                           help='% of Product Life Time the goods can continue on-sale.'
                                                ' It will be computed on the lot/serial number.')
    vtt_removal_time_percentage = fields.Float('Removal Time',
                                               help='% of Product Life Time after which the goods should be removed'
                                                    ' from stock. It will be computed on the lot/serial number.')
    vtt_alert_time_percentage = fields.Float('Alert Time',
                                             help='% of Product Life Time after which an alert should be raised.'
                                                  ' It will be computed on the lot/serial number.')

    vtt_show_expiration_percentage = fields.Boolean('Use Expiration Percentage')

    vtt_use_production_date = fields.Boolean('Use Dynamic Production Date')

    @api.onchange('vtt_show_expiration_percentage')
    def onchange_show_expiration_percentage(self):
        use_invert = self.env['ir.config_parameter'].sudo().get_param(
            'vtt_product_expiry_by_percentage.expiration_percentage_warn_invert',
            False
        )
        if self.expiration_time:
            if self.vtt_show_expiration_percentage:
                self.vtt_use_time_percentage = self.use_time / self.expiration_time * 100
                if use_invert:
                    # Warning time use invert
                    self.vtt_removal_time_percentage = (self.expiration_time - self.removal_time) / self.expiration_time * 100
                    self.vtt_alert_time_percentage = (self.expiration_time - self.alert_time) / self.expiration_time * 100
                else:
                    self.vtt_removal_time_percentage = self.removal_time / self.expiration_time * 100
                    self.vtt_alert_time_percentage = self.alert_time / self.expiration_time * 100

            else:
                self.use_time = int(self.expiration_time * self.vtt_use_time_percentage / 100)
                if use_invert:
                    # Warning time use invert
                    self.removal_time = int(self.expiration_time * (100 - self.vtt_removal_time_percentage) / 100)
                    self.alert_time = int(self.expiration_time * (100 - self.vtt_alert_time_percentage) / 100)
                else:
                    self.removal_time = int(self.expiration_time * self.vtt_removal_time_percentage / 100)
                    self.alert_time = int(self.expiration_time * self.vtt_alert_time_percentage / 100)

    def update_product_expiration_time(self):
        use_invert = self.env['ir.config_parameter'].sudo().get_param(
            'vtt_product_expiry_by_percentage.expiration_percentage_warn_invert',
            False
        )
        if self.expiration_time:
            if self.vtt_show_expiration_percentage:
                self.use_time = int(self.expiration_time * self.vtt_use_time_percentage / 100)
                if use_invert:
                    # Warning time use invert
                    self.removal_time = int(self.expiration_time * (100 - self.vtt_removal_time_percentage) / 100)
                    self.alert_time = int(self.expiration_time * (100 - self.vtt_alert_time_percentage) / 100)
                else:
                    self.removal_time = int(self.expiration_time * self.vtt_removal_time_percentage / 100)
                    self.alert_time = int(self.expiration_time * self.vtt_alert_time_percentage / 100)
            else:
                self.vtt_use_time_percentage = self.use_time / self.expiration_time * 100
                if use_invert:
                    # Warning time use invert
                    self.vtt_removal_time_percentage = (self.expiration_time - self.removal_time) / self.expiration_time * 100
                    self.vtt_alert_time_percentage = (self.expiration_time - self.alert_time) / self.expiration_time * 100
                else:
                    self.vtt_removal_time_percentage = self.removal_time / self.expiration_time * 100
                    self.vtt_alert_time_percentage = self.alert_time / self.expiration_time * 100
