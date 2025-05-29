from odoo import fields, models


class Cat(models.Model):
    _name = 'cat'
    _description = 'Cat Model'
    _inherit = 'animal'

    description = fields.Html(string='Description', required=False)
    #gender = fields.Selection(selection_add=[('undefined', 'Undefined'),('male',)], ondelete={'undefined': 'set null'})
    player_ids = fields.Many2many(string='Owner', comodel_name='player')

    def _sound(self):
        super(Cat, self)._sound()
        return "Meow meow..."


    def create_cat(self):
        new_cat = {
            'name': self.name,
            'gender': self.gender,
            'color': self.color,
            'age': self.age
        }

        return self.env['cat'].create(new_cat)
