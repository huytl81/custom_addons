# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    # delivery_type = fields.Selection(selection_add=[('ghn_shipping', 'GHN Shipping')],
    #                                  ondelete={'ghn_shipping': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    # service = fields.Selection([
    #     ('1', 'Express'),
    #     ('2', 'Standard'),
    #     ('4', 'Bulky and Heavy'),
    # ], 'GHN Service', required=False, default='2',
    #     help="Choose your GHN shipping plan (Express, Standard or Bulky and Heavy)")

    is_default_for_online_order = fields.Boolean('Áp dụng mặc định cho đơn hàng online', default=False)
    apply_default_shipping_fee = fields.Boolean('Áp dụng phí ship mặc định', default=False)


