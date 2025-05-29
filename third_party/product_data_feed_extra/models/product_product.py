# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models

GENDER_LIST = [
    ('unisex', 'Unisex'),
    ('female', 'Female'),
    ('male', 'Male'),
]
SIZE_UOM = [
    ('cm', 'cm'),
    ('in', 'in'),
]


class ProductProduct(models.Model):
    _inherit = "product.product"

    feed_color = fields.Char(string='Color')
    feed_size = fields.Char(string='Size')
    feed_material = fields.Char(string='Material')
    feed_pattern = fields.Char(string='Pattern')
    feed_gender = fields.Selection(
        selection=GENDER_LIST,
        string='Gender',
    )
    feed_length = fields.Float(
        string='Product Length',
        digits='Product Unit of Measure',
    )
    feed_width = fields.Float(
        string='Product Width',
        digits='Product Unit of Measure',
    )
    feed_height = fields.Float(
        string='Product Height',
        digits='Product Unit of Measure',
    )
    feed_size_uom = fields.Selection(
        selection=SIZE_UOM,
        string='UOM',
        help='Unit of Measure.',
    )
    feed_expiration_date = fields.Date(
        string='Expiration Date',
        help="Product expiration. If the product is expired, "
             "it won't be shown in the feed recipient side.",
    )
