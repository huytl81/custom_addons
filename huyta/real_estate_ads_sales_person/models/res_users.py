from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many('estate.property', 'seller_id', string='Properties')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Property Offers")