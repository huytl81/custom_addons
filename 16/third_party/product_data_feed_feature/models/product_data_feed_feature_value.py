# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models


class ProductDataFeedFeatureValue(models.Model):
    _name = "product.data.feed.feature.value"
    _description = 'Product Feature Values'

    name = fields.Char(string="Value", required=True, translate=True)
    feature_id = fields.Many2one(
        comodel_name='product.data.feed.feature',
        ondelete='cascade',
        required=True,
    )
    feature_code = fields.Char(
        related='feature_id.name',
    )

    _sql_constraints = [('product_data_feed_feature_value_uniq',
                         'UNIQUE (name, feature_id)',
                         'Product Feature Value must be unique for per feature.')]

    def name_get(self):
        return [(rec.id, "%s: %s" % (rec.feature_id.name, rec.name)) for rec in self]
