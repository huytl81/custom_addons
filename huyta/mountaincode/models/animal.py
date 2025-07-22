from odoo import fields, models, api


class Animal(models.AbstractModel):
    _name = 'animal'
    _description = 'Animal Abstract Model'

    name = fields.Char('Name', required=True)
    gender =  fields.Selection([('male', 'Male'),('female', 'Female')], string='Gender')
    color = fields.Char('Color')
    greeting = fields.Char(string='Greeting')
    bod = fields.Integer(string='Birth of Date')
    jdate = fields.Integer(string='Joined Date')
    age = fields.Integer(string='Age', compute='_compute_age', inverse='_reset_greeting')

    def _sound(self):
        return "Scream"

    @api.depends('bod','jdate')
    def _compute_age(self):
        for record in self:
            record.age = record.jdate - record.bod

    def _reset_greeting(self):
        for record in self:
            record.greeting = "Well done!"
