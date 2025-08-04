from odoo import models, fields, api
from datetime import timedelta


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    price = fields.Float(string='Price')
    validity = fields.Integer(string='Validity (days)')
    created_date = fields.Date(string='Created Date')
    deadline = fields.Date(string='Deadline',compute="_compute_deadline", inverse="_inverse_deadline")
    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
            ('pending', 'Pending'),
        ],
        string='Status',
        default='pending'
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    
    @api.depends('created_date','validity')
    def _compute_deadline(self):
        for record in self:
            if (record.validity and record.created_date):
                record.deadline = record.created_date + timedelta(days=record.validity)
            else:
                record.deadline = False
    	
    	
    def _inverse_deadline(self):
        for record in self:
            record.validity = (record.deadline - record.created_date).days
