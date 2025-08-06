from odoo import models, fields, api, _


class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
    name = fields.Char(string="Tag Name", required=True)
    color = fields.Char(string='Color', widget="color", help="Color for the tag")