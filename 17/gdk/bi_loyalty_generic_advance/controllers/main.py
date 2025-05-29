# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json
import odoo.http as http
from odoo.http import request
from datetime import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):

    @http.route(['/get-loyalty-points'], type='http', auth='public', website=True)
    def get_loyalty_points(self, **post):
        so = request.env['sale.order'].sudo().browse(int(post.get('order_id')))
        today_date = datetime.today().date()
        config = request.env['all.loyalty.setting'].sudo().search(
            [('active', '=', True), ('issue_date', '<=', today_date),
             ('expiry_date', '>=', today_date)])
        redeem_value = 0.0
        partner = so.partner_id
        company_currency = request.website.company_id.currency_id
        web_currency = request.website.get_current_pricelist().currency_id
        if so:
            for rule in config.redeem_ids:
                if rule.min_amt <= partner.loyalty_pts and partner.loyalty_pts <= rule.max_amt:
                    redeem_value = rule.reward_amt

            if company_currency.id != web_currency.id:
                new_redeem = (redeem_value * web_currency.rate) / company_currency.rate
                redeem_value = round(new_redeem, 2)

            loyalty_amount = round(redeem_value * partner.loyalty_pts, 2)

            data = {
                'partner': partner.name,
                'points': partner.loyalty_pts,
                'loyalty_amount': loyalty_amount,
                'redeem_value': redeem_value,
                'amount_total': so.amount_total,
                'order_redeem_points': so.order_redeem_points
            }
            return json.dumps(data)

    @http.route(['/redeem-loyalty-points'], type='http', auth='public', website=True)
    def redeem_loyalty_points(self, **post):
        so = request.env['sale.order'].sudo().browse(int(post.get('order_id')))
        today_date = datetime.today().date()
        loyalty_config = request.env['all.loyalty.setting'].sudo().search(
            [('active', '=', True), ('issue_date', '<=', today_date),
             ('expiry_date', '>=', today_date)])
        for config in loyalty_config:
            if config:
                if config.loyalty_tier.min_range <= so.total_sales <= config.loyalty_tier.max_range:
                    res = request.env['sale.order.line'].sudo().create({
                        'product_id': config.product_id.id,
                        'name': config.product_id.name,
                        'price_unit': -int(post.get('entered_points')) * float(post.get('redeem_value')),
                        'order_id': so.id,
                        'product_uom': config.product_id.uom_id.id,
                        'discount_line': True,
                        'redeem_points': int(post.get('entered_points'))
                    })
                    so.sudo().write({
                        'order_redeem_points': int(post.get('entered_points')),
                        'redeem_value': float(post.get('redeem_value')),
                    })

                    return json.dumps(res.id)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order()
        order.write({'is_from_website': True})
        so_line = request.env['sale.order.line'].sudo().browse(line_id)
        if so_line.discount_line and set_qty == 0:
            so_line.order_id.sudo().write({
                'order_redeem_points': 0
            })
        return super(WebsiteSaleInherit, self).cart_update_json(product_id, line_id, add_qty, set_qty, display)


class PortalLoyaltyHistory(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalLoyaltyHistory, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        LoyaltyHistory = request.env['all.loyalty.history'].sudo()
        loyalty_count = LoyaltyHistory.sudo().search_count([
            ('partner_id', '=', partner.id)])
        if loyalty_count:
            values.update({
                'loyalty_count': 1,
            })
            return values

    @http.route(['/my/loyalty/history', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_history(self, report_type=None, category='', search='', access_token=None, download=False, **kwargs):
        partner = request.env.user.partner_id
        LoyaltyHistory = request.env['all.loyalty.history'].sudo().search([('partner_id', '=', partner.id)])

        return http.request.render('bi_loyalty_generic_advance.portal_loyalty_history', {
            'partner': partner.sudo(),
            'force_refresh': True,
            'LoyaltyHistory': LoyaltyHistory
        })
