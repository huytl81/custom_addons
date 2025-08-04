from odoo import models, fields, api, _


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'

    name = fields.Char(string="Property Type", required=True)