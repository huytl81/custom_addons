# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models


class ProductDataFeedFeature(models.Model):
    _name = "product.data.feed.feature"
    _description = 'Product Features'
    _order = 'sequence, name'
    _rec_name = 'description'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Code', required=True, translate=True)
    description = fields.Char(required=True)

    _sql_constraints = [('product_data_feed_feature_uniq',
                         'UNIQUE (name)',
                         'Product Feature Name must be unique.')]
