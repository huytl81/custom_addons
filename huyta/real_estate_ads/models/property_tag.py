from odoo import models, fields, api, _


class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'

    name = fields.Char(string="Tag Name", required=True)