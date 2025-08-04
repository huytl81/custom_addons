from odoo import models, fields, api


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _inherit = ['mail.thread', 'mail.activity.mixin'] 

    name = fields.Char(string="Property Name", required=True)
    description = fields.Text(string="Description")
    property_type_id = fields.Many2one('estate.property.type', string="Property Type", required=True)
    property_tag_ids = fields.Many2many('estate.property.tag', string="Property Tags")
    property_offer_ids = fields.One2many('estate.property.offer','property_id', string="Property Offers")
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
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area")
    
    
    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
    	for rec in self:
            rec.total_area = rec.living_area + rec.garden_area
