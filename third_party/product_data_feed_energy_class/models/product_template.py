# Copyright © 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models
from .product_product import ENERGY_EFFICIENCY_CLASSES


class ProductTemplate(models.Model):
    _inherit = "product.template"

    energy_efficiency_class = fields.Selection(
        selection=ENERGY_EFFICIENCY_CLASSES,
        string='Energy Efficiency',
        compute='_compute_energy_efficiency_class',
        inverse='_inverse_energy_efficiency_class',
        help='Energy Efficiency Class.',
        store=True,
    )

    # flake8: noqa: E501
    @api.depends('product_variant_ids', 'product_variant_ids.energy_efficiency_class')
    def _compute_energy_efficiency_class(self):
        unique_variants = self.filtered(lambda tmpl: len(tmpl.product_variant_ids) == 1)
        for template in unique_variants:
            template.energy_efficiency_class = template.product_variant_ids.energy_efficiency_class
        for template in (self - unique_variants):
            template.energy_efficiency_class = False

    def _inverse_energy_efficiency_class(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.energy_efficiency_class = template.energy_efficiency_class
