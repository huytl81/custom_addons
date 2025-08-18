import logging
from odoo import models, fields, api
from random import randint

_logger = logging.getLogger(__name__)


class Property(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'website.published.mixin','website.seo.metadata']

    name = fields.Char(string="Property Name", required=True)
    description = fields.Text(string="Description")
    type_id = fields.Many2one('estate.property.type', string="Property Type", required=True)
    tag_ids = fields.Many2many('estate.property.tag', string="Property Tags")
    offer_ids = fields.One2many('estate.property.offer','property_id', string="Property Offers")
    postcode = fields.Integer(string="Postcode")
    date_availability = fields.Date(string="Available From")
    expected_price = fields.Float(string="Expected Price", tracking=True)
    best_offer = fields.Float(string="Best Offer", compute="_compute_best_offer")
    selling_price = fields.Float(string="Selling Price", readonly=True)
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
    
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids)
    
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
            
    def action_view_offers(self):
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.name} - Offers",
            'res_model': 'estate.property.offer',
            'view_mode': 'list,form',
            'domain': [('property_id','=', self.id)]
        }

    def action_client_action(self):
        return {
            'type': 'ir.actions.client',
            'name': f"Client Action",
            'tag': 'display_notification',
            'params': {
                'title': 'Client Action',
                'message': f"Client Action for {self.name}",
                'sticky': False,
                'type': 'success'
            }
        }

    def action_url_action(self):
        return{
            'type': 'ir.actions.act_url',
            'url': 'https://www.odoo.com',
            'target': 'new'
        }

    def _compute_best_offer(self):
        if self.offer_ids:
            # self.best_offer = max(self.offer_ids, key=lambda x: x.price).price
            # self.best_offer = max(self.offer_ids.mapped('price'))
            max_offer = max(self.offer_ids, key=lambda x: x.price)
            self.best_offer =  max_offer.price

    def _get_report_base_filename(self):
        self.ensure_one()
        return "Estate Property - %s" % self.name

    def _compute_website_url(self):
        for rec in self:
            # rec.website_url = f"/property/%s" % rec.id
            rec.website_url = f"/property/{rec.id}"

    def action_send_email(self):
        mail_template = self.env.ref('real_estate_ads.offer_mail_template')
        if mail_template:
            mail_template.send_mail(self.id, force_send=True)

    # Collect all partner emails from offer_ids and return as CSV string
    def _get_emails(self):
        
        # Lấy email từ offer_ids
        emails = self.offer_ids.mapped('partner_email')
        # Duyệt toàn bộ emails.
        # Bỏ qua email rỗng hoặc None.
        # Cắt khoảng trắng thừa.
        # Cho vào set để loại bỏ trùng lặp.
        # Ép về list để join thành chuỗi sau này.
        clean_emails = list({e.strip() for e in emails if e and e.strip()})

        # Ghép thành string
        email_str = ','.join(clean_emails)
        _logger.info("Emails for template: %s", email_str)
        return email_str
