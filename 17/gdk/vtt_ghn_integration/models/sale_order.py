from odoo import api, fields, models, _
import requests
import json
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ghn_order_code = fields.Char('GHN Order Code', store=True)

    weight = fields.Integer('Weight(gram)', default=1, help='Products total weight')
    length = fields.Integer('Length(cm)', default=1, help='Length calculated by formula (DxRxC/5000)')
    width = fields.Integer('Width(cm)', default=1, help='Width calculated by formula (DxRxC/5000)')
    height = fields.Integer('Height(cm)', default=1, help='Height calculated by formula (DxRxC/5000)')
    required_note = fields.Selection([
        ('KHONGCHOXEMHANG', 'Preview Not Allowed'),
        ('CHOXEMHANGKHONGTHU', 'Preview Allowed'),
        ('CHOTHUHANG', 'Testing Allowed')
    ], string="Delivery Note", default="KHONGCHOXEMHANG", readonly=True)
    payment_type = fields.Selection([
        ('1', 'Sender pays the fee'),
        ('2', 'Recipient pays fee'),
    ], string="Payment Option", default="2", required=True)
    convert_volume = fields.Integer('Converted Volume(gram)', required=True, default=0,
                                    help='Volume calculated by formula (DxRxC/5000)')

    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        is_delivery = False
        for line in self.order_line:
            if line.is_delivery:
                is_delivery = True
        if is_delivery:
            if self.carrier_id.service:
                if not self.height and not self.length and not self.width:
                    raise UserError(_('Please provide weight or size of delivery package.'))
                ghn_order = self.create_ghn_order()
                if 'data' in ghn_order:
                    if 'order_code' in ghn_order['data']:
                        order_code = ghn_order['data']['order_code']
                        if order_code:
                            self.update({'ghn_order_code':order_code})
        return True

    def action_open_delivery_wizard(self):
        view_id = self.env.ref('delivery.choose_delivery_carrier_view_form').id
        if self.env.context.get('carrier_recompute'):
            name = _('Update shipping cost')
            carrier = self.carrier_id
        else:
            name = _('Add a shipping method')
            carrier = self.partner_id.property_delivery_carrier_id
        if self.weight or self.width or self.height or self.length:
            return {
                'name': name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'choose.delivery.carrier',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context': {
                    'default_order_id': self.id,
                    'default_carrier_id': carrier.id,
                    'default_weight': self.weight,
                    'default_length': self.length,
                    'default_width': self.width,
                    'default_height': self.height,
                    'default_required_note': self.required_note,
                    'default_payment_type': self.payment_type,
                    'default_convert_volume': self.convert_volume,
                }
            }
        else:
            return {
                'name': name,
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'choose.delivery.carrier',
                'view_id': view_id,
                'views': [(view_id, 'form')],
                'target': 'new',
                'context': {
                    'default_order_id': self.id,
                    'default_carrier_id': carrier.id,
                }
            }

    def create_ghn_order(self):
        self.ensure_one()
        # request_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create"
        request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/create"
        ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
        ghn_shop_id = self.warehouse_id.ghn_shop_id
        if ghn_shop_id and ghn_token:
            headers = {
                'Content-type': 'application/json',
                'Token': ghn_token,
                'shop_id': ghn_shop_id
            }
        else:
            raise UserError(_('The GHN Token or shop_id is not valid.'))

        if not self.required_note:
            raise UserError(_('Delivery Note is required.'))
        if not self.payment_type:
            raise UserError(_('Payment Option is required.'))
        note = ''
        service_fee = 0.0
        is_reward_discount = False
        is_reward_free_ship = False
        for line in self.order_line:
            if line.display_type:
                note = note + line.name +'\n'
            if line.is_delivery:
                service_fee = service_fee + line.price_subtotal
            """
            if line.is_reward_line:
                applied_programs = self._get_applied_programs_with_rewards_on_current_order()
                if applied_programs:
                    for applied_program in applied_programs:
                        if applied_program.reward_type == 'free_shipping':
                            self.write({'payment_type': '1'})  # seller pay
                            is_reward_free_ship = True
                        else:
                            # self.write({'payment_type': '2'})    # buyer pay
                            is_reward_discount = True
            """

        if (not is_reward_free_ship and not is_reward_discount) or (not is_reward_free_ship and is_reward_discount):
            cod_amount = self.amount_total - service_fee
        else:
            cod_amount = self.amount_total

        insurance_value = 0.0
        for line in self.order_line:
            if line.product_id.product_tmpl_id.sale_ok:
                insurance_value = insurance_value + line.price_subtotal

        return_phone = ''
        company_phone = self.env.user.company_id.partner_id.phone
        if company_phone:
            return_phone = ''.join(filter(lambda i: i.isdigit(), company_phone.replace('+84', '0')))
        to_phone = ''
        partner_shipping_phone = self.partner_shipping_id.phone
        if partner_shipping_phone:
            to_phone = ''.join(filter(lambda i: i.isdigit(), partner_shipping_phone.replace('+84', '0')))
        else:
            if self.partner_id.phone:
                to_phone = ''.join(filter(lambda i: i.isdigit(), self.partner_id.phone.replace('+84', '0')))
            else:
                raise UserError(_('Please provide recipient contact phone/ mobile.'))

        data = {
            "payment_type_id": int(self.payment_type),    # who pay the ship, free ship = 1 (seller pay)
            "note": note,
            "required_note": self.required_note,
            "return_phone": return_phone,         # only 10 numbers
            "return_address": self.warehouse_id.partner_id.street,
            "return_district_id": self.warehouse_id.partner_id.district_id.ghn_district_id,
            "return_ward_code": self.warehouse_id.partner_id.ward_id.ghn_ward_id,
            "client_order_code": "",
            "to_name": self.partner_id.name,
            "to_phone": to_phone,
            "to_address": self.partner_shipping_id.street,
            "to_ward_code": self.partner_shipping_id.ward_id.ghn_ward_id,
            "to_district_id": self.partner_shipping_id.district_id.ghn_district_id,
            "cod_amount": int(cod_amount),
            "content": self.name,
            "weight": self.weight,
            "height": self.height,
            "length": self.length,
            "width": self.width,
            "pick_station_id": 0,
            "insurance_value": int(insurance_value),
            "service_id": 0,
            "service_type_id": int(self.carrier_id.service)     # Input value 1: Express , 2: Standard or 3: Saving (if not input service_id) => But only Standard
        }
        req = requests.post(request_url, data=json.dumps(data), headers=headers)
        req.raise_for_status()
        content = req.json()
        return content

    # GHN khong update tien_thu_ho_COD va ben_tra_phi
    # def write(self, values):
    #     res = super(SaleOrder, self).write(values)
    #     if self.ghn_order_code:
    #         for picking_id in self.picking_ids:
    #             if picking_id.state not in ['done','cancel','draft']:
    #                 if not picking_id.ghn_order_status:
    #                     picking_id.check_single_ghn_order_status()
    #                 if picking_id.ghn_order_status == 'ready_to_pick':
    #                     self.ghn_update_order()
    #                 # else:
    #                 #     raise UserError(_('Hàng đang được giao, Vui lòng tạo đơn hàng khác.'))
    #     return res

    # def ghn_update_order(self):
    #     self.ensure_one()
    #     request_url = "https://dev-online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/update"
    #     ghn_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token')
    #     ghn_shop_id = self.warehouse_id.ghn_shop_id
    #     if ghn_shop_id and ghn_token:
    #         headers = {
    #             'Content-type': 'application/json',
    #             'Token': ghn_token,
    #             'shop_id': ghn_shop_id
    #         }
    #     else:
    #         raise UserError(_('Giá trị token hoặc shop_id không chính xác.'))
    #
    #     if not self.required_note:
    #         raise UserError(_('Thông tin Lưu ý giao hàng là yêu cầu bắt buộc'))
    #     if not self.payment_type:
    #         raise UserError(_('Tùy chọn thanh toán là thông tin bắt buộc'))
    #     note = ''
    #     service_fee = 0.0
    #     for line in self.order_line:
    #         if line.display_type:
    #             note = note + line.name + '\n'
    #         if line.is_delivery:
    #             service_fee = service_fee + line.price_subtotal
    #     return_phone = ''.join(filter(lambda i: i.isdigit(), self.env.user.company_id.partner_id.phone.replace('+84', '0')))
    #     to_phone = ''.join(filter(lambda i: i.isdigit(), self.partner_id.phone.replace('+84', '0')))
    #     data = {
    #         "order_code": self.ghn_order_code,
    #         # "payment_type_id": int(self.payment_type),  # who pay the ship
    #         # "note": note,
    #         # "required_note": self.required_note,
    #         # "return_phone": return_phone,  # only 10 numbers
    #         # "return_address": self.warehouse_id.partner_id.street,
    #         # "return_district_id": self.warehouse_id.partner_id.district_id.ghn_district_id,
    #         # "return_ward_code": self.warehouse_id.partner_id.ward_id.ghn_ward_id,
    #         # "client_order_code": "",
    #         # "to_name": self.partner_id.name,
    #         # "to_phone": to_phone,
    #         # "to_address": self.partner_id.street,
    #         # "to_ward_code": self.partner_id.ward_id.ghn_ward_id,
    #         # "to_district_id": self.partner_id.district_id.ghn_district_id,
    #         "cod_amount": int(self.amount_total - service_fee),
    #         # "content": self.name,
    #         # "weight": self.weight,
    #         # "height": self.height,
    #         # "length": self.length,
    #         # "width": self.width,
    #         # "pick_station_id": 0,
    #         # "insurance_value": int(self.amount_total - service_fee),
    #         # "service_id": 0,
    #         # "service_type_id": int(self.carrier_id.service)
    #         # Input value 1: Express , 2: Standard or 3: Saving (if not input service_id) => But only Standard
    #     }
    #
    #     req = requests.post(request_url, data=json.dumps(data), headers=headers)
    #     req.raise_for_status()
    #     content = req.json()
    #     return content