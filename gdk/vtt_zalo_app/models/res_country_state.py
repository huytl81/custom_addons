from odoo import api, fields, models, _


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    ghn_allowed = fields.Boolean('GHN service allowed', default=False)
