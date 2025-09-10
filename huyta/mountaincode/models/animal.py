from odoo import fields, models, api
from datetime import timedelta

class Animal(models.AbstractModel):
    _name = 'animal'
    _description = 'Animal Abstract Model'

    name = fields.Char('Name', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender', ondelete={'male': 'set null', 'female': 'set null'})
    color = fields.Char('Color')
    greeting = fields.Char(string='Greeting')
    bod = fields.Integer(string='Birth of Date')
    joined_date = fields.Date(string='Joined Date')
    age = fields.Integer(string='Age', compute='_compute_age', inverse='_inverse_age', store=True, default=0)

    def sound(self):
        return "Scream"

    @api.depends('bod','joined_date')
    def _compute_age(self):
        for record in self:
            record.age = record.joined_date.year - record.bod

    def _inverse_age(self):
        for record in self:
            record.joined_date = (
                fields.Date.to_date(f"{record.bod + record.age}-01-01")
                if record.bod is not None and record.age is not None
                else False
            )