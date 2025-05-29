# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models
from .product_product import GENDER_LIST, SIZE_UOM


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_color = fields.Char(
        string='Color',
        compute='_compute_feed_color',
        inverse='_inverse_feed_color',
        store=True,
    )
    feed_size = fields.Char(
        string='Size',
        compute='_compute_feed_size',
        inverse='_inverse_feed_size',
        store=True,
    )
    feed_material = fields.Char(
        string='Material',
        compute='_compute_feed_material',
        inverse='_inverse_feed_material',
        store=True,
    )
    feed_pattern = fields.Char(
        string='Pattern',
        compute='_compute_feed_pattern',
        inverse='_inverse_feed_pattern',
        store=True,
    )
    feed_gender = fields.Selection(
        string='Gender',
        selection=GENDER_LIST,
        compute='_compute_feed_gender',
        inverse='_inverse_feed_gender',
        store=True,
    )
    feed_length = fields.Float(
        string='Product Length',
        compute='_compute_feed_length',
        inverse='_inverse_feed_length',
        digits='Product Unit of Measure',
        store=True,
    )
    feed_width = fields.Float(
        string='Product Width',
        compute='_compute_feed_width',
        inverse='_inverse_feed_width',
        digits='Product Unit of Measure',
        store=True,
    )
    feed_height = fields.Float(
        string='Product Height',
        compute='_compute_feed_height',
        inverse='_inverse_feed_height',
        digits='Product Unit of Measure',
        store=True,
    )
    feed_size_uom = fields.Selection(
        string='UOM',
        selection=SIZE_UOM,
        help='Unit of Measure.',
        compute='_compute_feed_size_uom',
        inverse='_inverse_feed_size_uom',
        store=True,
    )
    feed_size_system = fields.Selection(
        selection=[
            ('AU', 'AU'),
            ('BR', 'BR'),
            ('CN', 'CN'),
            ('DE', 'DE'),
            ('EU', 'EU'),
            ('FR', 'FR'),
            ('IT', 'IT'),
            ('JP', 'JP'),
            ('MEX', 'MEX'),
            ('UK', 'UK'),
            ('US', 'US'),
        ],
        string='Size System',
    )
    feed_expiration_date = fields.Date(
        string='Expiration Date',
        compute='_compute_feed_expiration_date',
        inverse='_inverse_feed_expiration_date',
        help="Product expiration. If the product is expired, "
             "it won't be shown in the feed recipient side.",
        store=True,
    )

    @api.depends('product_variant_ids', 'product_variant_ids.feed_gtin')
    def _compute_feed_gtin(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_gtin = template.product_variant_ids.feed_gtin
        for template in (self - unique_variants):
            template.feed_gtin = False

    def _inverse_feed_gtin(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_gtin = template.feed_gtin

    @api.depends('product_variant_ids', 'product_variant_ids.feed_mpn')
    def _compute_feed_mpn(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_mpn = template.product_variant_ids.feed_mpn
        for template in (self - unique_variants):
            template.feed_mpn = False

    def _inverse_feed_mpn(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_mpn = template.feed_mpn

    @api.depends('product_variant_ids', 'product_variant_ids.feed_color')
    def _compute_feed_color(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_color = template.product_variant_ids.feed_color
        for template in (self - unique_variants):
            template.feed_color = False

    def _inverse_feed_color(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_color = template.feed_color

    @api.depends('product_variant_ids', 'product_variant_ids.feed_size')
    def _compute_feed_size(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_size = template.product_variant_ids.feed_size
        for template in (self - unique_variants):
            template.feed_size = False

    def _inverse_feed_size(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_size = template.feed_size

    @api.depends('product_variant_ids', 'product_variant_ids.feed_material')
    def _compute_feed_material(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_material = template.product_variant_ids.feed_material
        for template in (self - unique_variants):
            template.feed_material = False

    def _inverse_feed_material(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_material = template.feed_material

    @api.depends('product_variant_ids', 'product_variant_ids.feed_pattern')
    def _compute_feed_pattern(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_pattern = template.product_variant_ids.feed_pattern
        for template in (self - unique_variants):
            template.feed_pattern = False

    def _inverse_feed_pattern(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_pattern = template.feed_pattern

    @api.depends('product_variant_ids', 'product_variant_ids.feed_gender')
    def _compute_feed_gender(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_gender = template.product_variant_ids.feed_gender
        for template in (self - unique_variants):
            template.feed_gender = False

    def _inverse_feed_gender(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_gender = template.feed_gender

    @api.depends('product_variant_ids', 'product_variant_ids.feed_length')
    def _compute_feed_length(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_length = template.product_variant_ids.feed_length
        for template in (self - unique_variants):
            template.feed_length = False

    def _inverse_feed_length(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_length = template.feed_length
                
    @api.depends('product_variant_ids', 'product_variant_ids.feed_width')
    def _compute_feed_width(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_width = template.product_variant_ids.feed_width
        for template in (self - unique_variants):
            template.feed_width = False

    def _inverse_feed_width(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_width = template.feed_width

    @api.depends('product_variant_ids', 'product_variant_ids.feed_height')
    def _compute_feed_height(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_height = template.product_variant_ids.feed_height
        for template in (self - unique_variants):
            template.feed_height = False

    def _inverse_feed_height(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_height = template.feed_height
                
    @api.depends('product_variant_ids', 'product_variant_ids.feed_size_uom')
    def _compute_feed_size_uom(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_size_uom = template.product_variant_ids.feed_size_uom
        for template in (self - unique_variants):
            template.feed_size_uom = False

    def _inverse_feed_size_uom(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_size_uom = template.feed_size_uom

    @api.depends('product_variant_ids', 'product_variant_ids.feed_expiration_date')
    def _compute_feed_expiration_date(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_expiration_date = \
                template.product_variant_ids.feed_expiration_date
        for template in (self - unique_variants):
            template.feed_expiration_date = False

    def _inverse_feed_expiration_date(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_expiration_date = \
                    template.feed_expiration_date
