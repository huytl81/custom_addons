from odoo import models, fields, api, _
from random import randint

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
       
    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string='Color', default='_get_default_color', aggregator=False)

    def _get_default_color(self):
        return randint(1, 11)