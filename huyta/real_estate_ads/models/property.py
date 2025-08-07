from odoo import models, fields, api
from random import randint

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
    total_area = fields.Integer(string="Total Area")
    state = fields.Selection([
        ('new', "New"),
        ('received', "Received"),
        ('accepted', "Accepted"),
        ('sold', "Sold"),
        ('canceled', "Canceled")
    ], default='new')
    buyer_id = fields.Many2one('res.partner', string="Buyer", domain=[('is_company','=',True)])
    buyer_phone = fields.Char(string="Phone", related="buyer_id.phone")
    seller_id = fields.Many2one('res.users', string="Seller")
    offer_count = fields.Integer(string='Offer Count', compute='_compute_offer_count', store=True)
        
    # Su dung compute field  
    # total_area = fields.Integer(string="Total Area", compute="_compute_total_area")
    # Su dung onchang field
    total_area = fields.Integer(string="Total Area")
    
    #@api.depends('living_area','garden_area')
    #def _compute_total_area(self):
    #   for rec in self:
    #       rec.total_area = rec.living_area + rec.garden_area
    
    @api.depends('property_offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.property_offer_ids)
    
    @api.onchange('living_area','garden_area')
    def _onchange_total_area(self):
        self.total_area = self.living_area + self.garden_area

    def action_receive(self):
        for rec in self:
            rec.state ='received'
            
    def action_accept(self):
        for rec in self:
            rec.state = 'accepted'
    
    def action_sold(self):
        for rec in self:
            rec.state = 'sold'
    
    def action_cancel(self):
        for rec in self:
            rec.state = 'canceled'
            
    def action_property_view_offers(self):
        return{
            'type': 'ir.actions.act_window',
            'name': f"{self.name} - Offers",
            'res_model': 'estate.property.offer',
            'view_mode': 'list,form',
            'domain': [('property_id','=', self.id)]
        }