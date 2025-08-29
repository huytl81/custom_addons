from odoo import models, fields, api, _
from random import randint

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    
    name = fields.Char(string="Tag Name", required=True)
    color = fields.Integer(string='Color', default=lambda self: self._get_default_color(), aggregator=False)

    @api.model
    def _get_default_color(self):
        return randint(1, 11)