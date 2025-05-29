# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    vtt_date_order = fields.Datetime('Date Ordered')

    def write(self, vals):
        if 'vtt_date_order' in vals and vals.get('vtt_date_order'):
            vals.update({
                'date_order': vals.get('vtt_date_order')
            })
        return super(SaleOrder, self).write(vals)

    def _prepare_confirmation_values(self):
        res = super(SaleOrder, self)._prepare_confirmation_values()
        res.update({'vtt_date_order': res.get('date_order')})
        return res