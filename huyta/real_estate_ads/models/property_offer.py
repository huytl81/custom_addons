from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'

    price = fields.Float(string='Price')
    validity = fields.Integer(string='Validity (days)')
#    created_date = fields.Date(string='Created Date', default='_set_created_date')
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
    
#    _sql_constraints = [('check_validity', 'check(validity > 0)', 'Validity cannot be negative')]
    
    @api.depends('created_date','validity')
    @api.depends_context('uid')
    def _compute_deadline(self):
        #print(self.env.context)
        #print(self._context)
        for record in self:
            if (record.validity and record.created_date):
                record.deadline = record.created_date + timedelta(days=record.validity)
            else:
                record.deadline = False
    	
    	
    def _inverse_deadline(self):
        for record in self:
            if (record.deadline and record.created_date):
                record.validity = (record.deadline - record.created_date).days
            else:
                record.validity = False
                
#    @api.autovauum
#        def _clean_offers(self):
#            self.search([('statu', '=', 'refused')]).unlink()
            
#    @api.model
#    def _set_created_date(self):
#        return fields.Date.today() 

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if not vals.get('created_date'):
                vals['created_date'] = fields.Date.today()
        return super(PropertyOffer, self).create(vals_list)
        
    @api.constrains('validity')
    def _check_validity(self):
        for record in self:
            if (record.deadline <= record.created_date):
                raise ValidationError("Created date cannot be greater than or equal Deadline")
    

    
    
    
    
    
    
    
    
    
    
    
        
