from odoo import models, fields, api, _


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
    name = fields.Char(string="Property Type", required=True)