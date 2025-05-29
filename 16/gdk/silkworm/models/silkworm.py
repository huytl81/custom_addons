from odoo import fields, models


class silkworm_sale_order(models.Model):
    _inherit = 'sale.order'

    daterequired = fields.Date('Date Required', required=True)
    rush = fields.Boolean('Rush Order')
