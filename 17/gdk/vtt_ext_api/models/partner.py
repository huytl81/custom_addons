from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = "res.partner"

    zalo_id = fields.Char(string='Zalo id')
    zalo_name = fields.Char(string='Zalo name')
    zalo_picture = fields.Char(string='Zalo picture')

    is_default_address = fields.Boolean(default=False, string='Is default address')
    birth_day = fields.Date(string='Birth day')
    sex = fields.Selection([('male', 'Nam'), ('female', 'Nữ')], default='male')

    is_deleted = fields.Boolean(default=False)
