from odoo import api, fields, models, _


class ResWard(models.Model):
    _inherit = 'res.ward'

    ghn_allowed = fields.Boolean('GHN service allowed', default=False)

    shipping_allowed = fields.Boolean('Shipping allowed', default=False)
    default_shipping_method_price = fields.Float('Default shipping method price')
