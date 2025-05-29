# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models

ENERGY_EFFICIENCY_CLASSES = [
    ('A+++', 'A+++'),
    ('A++', 'A++'),
    ('A+', 'A+'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('G', 'G'),
]


class ProductProduct(models.Model):
    _inherit = "product.product"

    energy_efficiency_class = fields.Selection(
        selection=ENERGY_EFFICIENCY_CLASSES,
        string='Energy Efficiency',
        help='Energy Efficiency Class.',
    )
