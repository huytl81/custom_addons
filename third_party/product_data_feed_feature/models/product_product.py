from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    feed_feature_ids = fields.Many2many(
        comodel_name='product.data.feed.feature.value',
        string='Features',
    )
