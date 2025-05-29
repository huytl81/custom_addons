# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class WebSettingConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    promotion_id = fields.Boolean(string='Promotion', related="company_id.promotion_id", readonly=False)
    from_date = fields.Date(default=fields.date.today(), string='From Date', related="company_id.from_date",
                            readonly=False)
    to_date = fields.Date(default=fields.date.today(), string='To Date', related="company_id.to_date", readonly=False)

    product_type = fields.Selection([('product', 'Product'), ('product_category', 'Product Category')], 'Type',
                                    related="company_id.product_type", readonly=False)
    product_ids = fields.Many2many('product.product', string='Products', related='company_id.product_ids',
                                   readonly=False)
    promotion_points = fields.Integer('Promotion Points', related="company_id.promotion_points", readonly=False)
    product_category_ids = fields.Many2many('product.category', string='Product Category',
                                            related="company_id.product_category_ids", readonly=False)
    sign_up_bonus = fields.Float(string='Sign-up Bonus', related="company_id.sign_up_bonus", readonly=False)


class Company(models.Model):
    _inherit = 'res.company'

    promotion_id = fields.Boolean(string='Promotion')
    from_date = fields.Date(default=fields.date.today(), string='From Date')
    to_date = fields.Date(default=fields.date.today(), string='To Date')

    product_type = fields.Selection([('product', 'Product'), ('product_category', 'Product Category')], 'Type')
    product_ids = fields.Many2many('product.product', string='Products')
    promotion_points = fields.Integer('Promotion Points')
    product_category_ids = fields.Many2many('product.category', string='Product Category')
    sign_up_bonus = fields.Float(string='Sign-up Bonus')
