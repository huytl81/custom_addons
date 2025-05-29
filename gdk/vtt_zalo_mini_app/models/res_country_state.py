from odoo import api, fields, models, _


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    # ghn_allowed = fields.Boolean('GHN service allowed', default=False)

    shipping_allowed = fields.Boolean('Shipping allowed', default=False)


    # base
    state_code = fields.Char('Mã tỉnh thành')       # ma theo quy dinh chung
