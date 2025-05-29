# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from datetime import datetime
from odoo import SUPERUSER_ID
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError


class ReedemptionLoyalty(models.TransientModel):
    _inherit = "loyalty.wizard.reedem"

    def ok_redeem(self):
        active_ids = self._context.get('active_ids')
        redeem_value = 0.0
        today_date = datetime.today().date()
        result = self.env['sale.order'].browse(active_ids)
        partner_id = result.partner_id
        if self.redeem_point <= 0:
            raise ValidationError(_('Please enter valid loyalty points'))
        loyalty_config = self.env['all.loyalty.setting'].sudo().search([('active', '=', True), ('issue_date', '<=', today_date), ('expiry_date', '>=', today_date),('loyalty_tier', '=' , partner_id.tier_id.id)])
        if self.redeem_point > partner_id.loyalty_pts or self.redeem_point < 0:
            raise ValidationError(_('You can not redeem more than loyalty points'))
        is_exist = None
        for config in loyalty_config:
            if config:
                if not partner_id.loyalty_deactivate:
                    if config:
                        point_amt = 0
                        for rule in config.redeem_ids:
                            if rule.min_amt <= partner_id.loyalty_pts and partner_id.loyalty_pts <= rule.max_amt:
                                redeem_value = rule.reward_amt
                                point_amt += int(self.redeem_point) * redeem_value
                        if point_amt > 0:
                            if point_amt > result.amount_total:
                                raise ValidationError(_('You can not redeem more than total amount'))
                            for line in result.order_line:
                                if config.product_id.id == line.product_id.id:
                                    is_exist = line
                                    break
                            if not is_exist:
                                self.env['sale.order.line'].sudo().create({
                                    'product_id': config.product_id.id,
                                    'name': config.product_id.name,
                                    'price_unit': -point_amt,
                                    'order_id': result.id,
                                    'product_uom': config.product_id.uom_id.id,
                                    'discount_line': True,
                                    'redeem_points': int(self.redeem_point)
                                })
                                result.update({
                                    'order_redeem_points': self.redeem_point,
                                    'redeem_value': point_amt,
                                })
                            else:
                                raise ValidationError(_('You can not redeem more than one time'))
        return



