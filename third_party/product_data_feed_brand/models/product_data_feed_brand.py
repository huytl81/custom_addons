# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License OPL-1 (https://www.odoo.com/documentation/14.0/legal/licenses.html).

from odoo import fields, models, _


class ProductDataFeedBrand(models.Model):
    _name = "product.data.feed.brand"
    _description = 'Product Brands for Feeds'

    name = fields.Char(translate=True)

    _sql_constraints = [('product_data_feed_brand_uniq',
                         'UNIQUE (name)',
                         'Product Brand Name must be unique.')]
