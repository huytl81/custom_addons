# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _, tools
from datetime import date, time, datetime
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def get_loyalty_balance(self, order):
        today_date = datetime.today().date()
        plus_points = 0.0
        total_loyalty = 0.0
        order.write({'is_from_website': True})

        if self.env.company.promotion_id:
            if self.env.company.from_date <= (order.create_date).date() <= self.env.company.to_date:
                if self.env.company.product_type == 'product':
                    points = []
                    for line in order.order_line:
                        if line.product_id in self.env.company.product_ids:
                            points.append(self.env.company.promotion_points)
                            line.order_id.write({'order_credit_points': sum(points)})
                if self.env.company.product_type == 'product_category':
                    points_categ = []
                    for line in order.order_line:
                        if line.product_id.categ_id in self.env.company.product_category_ids:
                            points_categ.append(self.env.company.promotion_points)
                            line.order_id.write({'order_credit_points': sum(points_categ)})

        loyalty_config = self.env['all.loyalty.setting'].sudo().search(
            [('active', '=', True), ('issue_date', '<=', today_date),
             ('expiry_date', '>=', today_date)])

        path = request.httprequest.full_path
        show_redeem = True

        for config in loyalty_config:
            if config:
                if not order.partner_id.loyalty_deactivate:
                    if config.loyalty_tier.min_range <= order.total_sales <= config.loyalty_tier.max_range:
                        partner_id = order.partner_id
                        plus_points = 0.0

                        company_currency = order.company_id.currency_id
                        web_currency = order.pricelist_id.currency_id

                        if config.loyalty_basis_on == 'amount':
                            if config.loyality_amount > 0:
                                price = sum(order.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
                                if company_currency.id != web_currency.id:
                                    new_rate = (price * company_currency.rate) / web_currency.rate
                                else:
                                    new_rate = price
                                plus_points = int(new_rate / config.loyality_amount)
                                total_loyalty = partner_id.loyalty_pts + plus_points

                        if config.loyalty_basis_on == 'loyalty_category':
                            for line in order.order_line:
                                if not line.is_delivery:
                                    prod_categs = line.product_id.public_categ_ids
                                    for c in prod_categs:
                                        if c.Minimum_amount > 0:
                                            price = sum(order.order_line.filtered(lambda x: not x.is_delivery).mapped('price_total'))
                                            if company_currency.id != web_currency.id:
                                                new_rate = (price * company_currency.rate) / web_currency.rate
                                            else:
                                                new_rate = price
                                            plus_points += int(new_rate / c.Minimum_amount)

                            total_loyalty = partner_id.loyalty_pts + plus_points

                        if "/shop/confirmation" in str(path):
                            total_loyalty = partner_id.loyalty_pts
                            show_redeem = False

                        partner_id.write({'tier_id': config.loyalty_tier.id})

                        total_loyalty -= order.order_redeem_points

        return [plus_points, total_loyalty, show_redeem]
