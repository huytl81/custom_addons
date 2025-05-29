from odoo import api, fields, models, _


class ResDistrict(models.Model):
    _inherit = 'res.district'

    ghn_allowed = fields.Boolean('GHN service allowed', default=False)
