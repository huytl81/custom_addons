# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models, SUPERUSER_ID, _


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    vtt_create_expiration_percentage = fields.Float('Received % Expiration')
    vtt_current_expiration_percentage = fields.Float('Current % Expiration',
                                                     compute='_compute_expiration_percentage')
    vtt_production_date = fields.Date('Production Date')

    def _compute_expiration_percentage(self):
        date = datetime.datetime.now()
        for spl in self:
            cur_perc = 100
            if spl.expiration_date:
                if not spl.product_id.vtt_use_production_date:
                    product_expiration_time = spl.product_id.expiration_time
                elif spl.product_id.vtt_use_production_date and spl.vtt_production_date:
                    production_date = fields.Datetime.to_datetime(spl.vtt_production_date)
                    product_expiration_time = (spl.expiration_date - production_date).days
                else:
                    product_expiration_time = (spl.expiration_date - spl.create_date).days

                date_diff = (spl.expiration_date - date).days

                if product_expiration_time:
                    date_diff_percentage = date_diff / product_expiration_time * 100
                    cur_perc = date_diff_percentage

            spl.vtt_current_expiration_percentage = cur_perc

    # @api.model_create_multi
    # def create(self, vals_list):
    #     lots = super().create(vals_list)
    #     for lot in lots:
    #         if lot.product_id.vtt_use_production_date:
    #             production_date = fields.Datetime.to_datetime(lot.vtt_production_date)
    #             product_expiration_time = (lot.expiration_date - production_date).days
    #             lot.product_id.expiration_time = product_expiration_time
    #     return lots

    def _get_dates(self, product_id=None):
        res = super()._get_dates(product_id)
        product = self.env['product.product'].browse(product_id) or self.product_id
        use_invert = self.env['ir.config_parameter'].sudo().get_param(
            'vtt_product_expiry_by_percentage.expiration_percentage_warn_invert',
            False
        )

        if self.vtt_production_date:
            dt = self.vtt_production_date
        else:
            dt = fields.Datetime.now()

        if product and product.vtt_show_expiration_percentage:
            use_date_duration = int(product.expiration_time * product.vtt_use_time_percentage / 100)
            if use_invert:
                removal_date_duration = int(product.expiration_time * (100 - product.vtt_removal_time_percentage) / 100)
                alert_date_duration = int(product.expiration_time * (100 - product.vtt_alert_time_percentage) / 100)
            else:
                removal_date_duration = int(product.expiration_time * product.vtt_removal_time_percentage / 100)
                alert_date_duration = int(product.expiration_time * product.vtt_alert_time_percentage / 100)
            if use_date_duration:
                res['use_date'] = fields.Datetime.to_string(dt + datetime.timedelta(days=use_date_duration))
            if removal_date_duration:
                res['removal_date'] = fields.Datetime.to_string(dt + datetime.timedelta(days=removal_date_duration))
            if alert_date_duration:
                res['alert_date'] = fields.Datetime.to_string(dt + datetime.timedelta(days=alert_date_duration))
        res['vtt_production_date'] = fields.Datetime.to_string(dt)
        return res

    def _get_date_values(self, time_delta, new_date=False):
        res = super()._get_date_values(time_delta, new_date)
        product = self.product_id
        use_invert = self.env['ir.config_parameter'].sudo().get_param(
            'vtt_product_expiry_by_percentage.expiration_percentage_warn_invert',
            False
        )
        if product and (self.expiration_date or new_date):
            expiration_date = new_date or self.expiration_date
            if product.expiration_time:
                expiration_time = product.expiration_time
            elif self.vtt_production_date:
                expiration_time = (expiration_date - fields.Datetime.to_datetime(self.vtt_production_date)).days
            else:
                expiration_time = (expiration_date - datetime.datetime.now()).days
            use_date_duration = 0
            removal_date_duration = 0
            alert_date_duration = 0

            if product.vtt_show_expiration_percentage:
                if product.vtt_use_time_percentage:
                    use_date_duration = int(expiration_time * (100 - product.vtt_use_time_percentage) / 100)
                if product.vtt_removal_time_percentage:
                    if use_invert:
                        removal_date_duration = int(expiration_time * product.vtt_removal_time_percentage / 100)
                    else:
                        removal_date_duration = int(expiration_time * (100 - product.vtt_removal_time_percentage) / 100)
                if product.vtt_alert_time_percentage:
                    if use_invert:
                        alert_date_duration = int(expiration_time * product.vtt_alert_time_percentage / 100)
                    else:
                        alert_date_duration = int(expiration_time * (100 - product.vtt_alert_time_percentage) / 100)

            else:
                if product.use_time:
                    use_date_duration = product.expiration_time - product.use_time
                if product.removal_time:
                    removal_date_duration = product.expiration_time - product.removal_time
                if product.alert_time:
                    alert_date_duration = product.expiration_time - product.alert_time

            res['use_date'] = expiration_date - datetime.timedelta(days=use_date_duration)
            res['removal_date'] = expiration_date - datetime.timedelta(days=removal_date_duration)
            res['alert_date'] = expiration_date - datetime.timedelta(days=alert_date_duration)
            res['vtt_production_date'] = expiration_date - datetime.timedelta(days=expiration_time)
        return res