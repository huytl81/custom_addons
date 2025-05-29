# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import requests
import json

class ChooseDeliveryCarrier(models.TransientModel):
    # _name = 'choose.delivery.carrier.inherit'
    _inherit = 'choose.delivery.carrier'


    @api.onchange('carrier_id')
    def onchange_carrier_id_change_delivery_default_price(self):
        if self.carrier_id and self.order_id:
            if self.carrier_id.apply_default_shipping_fee:
                self.delivery_price = 0
                self.display_price = 0
                
                order = self.order_id                
                if order.partner_shipping_id and order.partner_shipping_id.ward_id and order.partner_shipping_id.ward_id.shipping_allowed:
                    to_ward = order.partner_shipping_id.ward_id                
                    self.delivery_price = to_ward.default_shipping_method_price
                    self.display_price = to_ward.default_shipping_method_price                            
    

    # def product_sale_ok_amount_total(self):
    #     amount_total = 0
    #     # for line in self.order_id.order_line:
    #     #     if line.product_id.product_tmpl_id.sale_ok:
    #     #         amount_total = amount_total + line.price_subtotal
    #     return amount_total

    # @api.onchange('weight', 'length', 'width', 'height', 'carrier_id')
    # def onchange_weight(self):
    #     if self.weight <= 0:
    #         raise UserError(_('Package weight must be greater than 0.'))
    #     # self.convert_volume = (self.height * self.width * self.length) / 5
    #     # if self.carrier_id.service:
    #     #     self.convert_volume = (self.height * self.width * self.length) / 5
    #     #     available_service = self.ghn_available_service()
    #     #     match_service = False
    #     #     if 'data' in available_service:
    #     #         for data in available_service['data']:
    #     #             if data['service_type_id'] == int(self.carrier_id.service):
    #     #                 match_service = True
    #     #     if match_service:
    #     #         calculate_fee = self.ghn_calculate_fee()
    #     #         if 'data' in calculate_fee:
    #     #             if 'total' in calculate_fee['data']:
    #     #                 ghn_fee = calculate_fee['data']['total']
    #     #                 if ghn_fee:
    #     #                     amount_total = self.product_sale_ok_amount_total()
    #     #                     if amount_total > PHI_KHAI_GIA:
    #     #                         self.display_price = ghn_fee + (amount_total/100)*0.5
    #     #                     else:
    #     #                         self.display_price = ghn_fee
    #     #                 else:
    #     #                     self.display_price = ghn_fee
    #     #     else:
    #     #         raise UserError(_('This shipping method currently not supported for the recipient location, please choose other method.'))
    #     #     self.order_id.write({
    #     #         'weight': self.weight,
    #     #         'length': self.length,
    #     #         'width': self.width,
    #     #         'height': self.height,
    #     #         'convert_volume': self.convert_volume,
    #     #     })

    # def button_confirm(self):
    #     if self.weight <= 0:
    #         raise UserError(_('Package weight must be greater than 0.'))
    #     # if self.weight and self.height and self.length and self.width:
    #     #     if not self.height and not self.length and not self.width:
    #     #         raise UserError(_('Please provide weight or size of delivery package.'))
    #     #     if self.carrier_id.service:
    #     #         calculate_fee = self.ghn_calculate_fee()
    #     #         ghn_fee = calculate_fee['data']['total']
    #     #         if ghn_fee:
    #     #             # if 'insurance_fee' in calculate_fee['data']:
    #     #             #     if calculate_fee['data']['insurance_fee'] > 0:
    #     #             #         # service_fee = self.order_service_fee()
    #     #             #         # reward_amount = self.order_reward_amount()
    #     #             #         # amount_total = self.order_id.amount_total - service_fee + abs(reward_amount)
    #     #             #         amount_total = self.calculate_final_amount_total()
    #     #             amount_total = self.product_sale_ok_amount_total()
    #     #             if amount_total > PHI_KHAI_GIA:
    #     #                 ghn_fee = ghn_fee + (amount_total / 100) * 0.5
    #     #             self.order_id.set_delivery_line(self.carrier_id, ghn_fee)
    #     #             self.order_id.write({
    #     #                 'recompute_delivery_price': False,
    #     #                 'delivery_message': self.delivery_message,
    #     #                 'required_note': self.required_note,
    #     #                 'payment_type': self.payment_type
    #     #             })
    #     #     else:
    #     #         self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
    #     #         self.order_id.write({
    #     #             'recompute_delivery_price': False,
    #     #             'delivery_message': self.delivery_message,
    #     #         })
    #     # else:
    #     #     self.order_id.set_delivery_line(self.carrier_id, self.delivery_price)
    #     #     self.order_id.write({
    #     #         'recompute_delivery_price': False,
    #     #         'delivery_message': self.delivery_message,
    #     #     })


    # def ghn_calculate_fee(self):
    #     # request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee"
    #     request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/fee"
    #     ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
    #     if ghn_token:
    #         headers = {
    #             'Content-type': 'application/json',
    #             'Token': ghn_token,
    #         }
    #     else:
    #         raise UserError(_('Please recheck GHN Token.'))
    #     if not self.height and not self.length and not self.width:
    #         raise UserError(_('Please provide weight or size of delivery package.'))

    #     from_district_id = self.order_id.warehouse_id.partner_id.district_id.ghn_district_id
    #     from_ward_id = self.order_id.warehouse_id.partner_id.ward_id.ghn_ward_id
    #     if not from_district_id and not from_ward_id:
    #         raise UserError(_('Please recheck store address (district/ ward).'))

    #     service_type_id = int(self.carrier_id.service)
    #     if not service_type_id:
    #         raise UserError(_('Please choose service type.'))

    #     to_district_id = self.order_id.partner_shipping_id.district_id.ghn_district_id
    #     to_ward_code = self.order_id.partner_shipping_id.ward_id.ghn_ward_id
    #     if not to_district_id and not to_ward_code:
    #         raise UserError(_('Please recheck address information (district/ ward) of recipient.'))
    #     if not self.required_note:
    #         raise UserError(_('The Delivery Note is required.'))
    #     if not self.payment_type:
    #         raise UserError(_('The Payment Note is required.'))

    #     amount_total = self.product_sale_ok_amount_total() # is total price of product's sale_ok

    #     if amount_total > GHN_MAX_INSURANCE_FEE:
    #         raise UserError(_('The GHN Shipping method is only available for order under or equal 10.000.000 VND, by GNH policy.'))

    #     data = {
    #         "from_district_id": from_district_id,
    #         "from_ward_id": from_ward_id,
    #         "service_type_id": service_type_id,
    #         "to_district_id": to_district_id,
    #         "to_ward_code": to_ward_code,
    #         "height": self.height,
    #         "length": self.length,
    #         "weight": self.weight,
    #         "width": self.width,
    #         "insurance_fee": int(amount_total),
    #         "coupon": None
    #     }
    #     req = requests.post(request_url, data=json.dumps(data), headers=headers)
    #     req.raise_for_status()
    #     content = req.json()
    #     if 'insurance_fee' in data:
    #         content['data']['insurance_fee'] = data['insurance_fee']
    #     return content


