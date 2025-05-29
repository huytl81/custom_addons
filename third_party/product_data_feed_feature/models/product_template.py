from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    feed_feature_ids = fields.Many2many(
        comodel_name='product.data.feed.feature.value',
        string='Features',
        compute='_compute_feed_feature_ids',
        inverse='_inverse_feed_feature_ids',
        store=True,
    )

    @api.depends('product_variant_ids',
                 'product_variant_ids.feed_feature_ids')
    def _compute_feed_feature_ids(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.feed_feature_ids = template.product_variant_ids.feed_feature_ids
        for template in (self - unique_variants):
            template.feed_feature_ids = False

    def _inverse_feed_feature_ids(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.feed_feature_ids = template.feed_feature_ids
