from odoo import models, fields, api


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    
    name = fields.Char(string="Property Name", required=True)
    description = fields.Text(string="Description")
    property_type = fields.Selection([('apartment', 'Apartment'), ('office', 'Office'), ('homestay', 'Homestay'), ('house', 'House'), ('villa', 'Villa'), ('flat', 'Flat')], string="Property Type")
    postcode = fields.Integer(string="Postcode")
    date_availability = fields.Date(string="Available From")
    expected_price = fields.Float(string="Expected Price")
    best_offer = fields.Float(string="Best Offer")
    selling_price = fields.Float(string="Selling Price")
    bedrooms = fields.Integer(string="Bedrooms")
    living_area = fields.Integer(string="Living Area")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area")
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], string="Garden Orientation")
    # state = fields.Selection([('new', 'New'), ('offer_received', 'Offer Received'), ('sold', 'Sold'), ('canceled', 'Canceled')], string="State")
    # buyer_id = fields.Many2one('res.partner', string="Buyer")
    # seller_id = fields.Many2one('res.users', string="Seller")
