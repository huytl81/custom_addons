from odoo import fields, models


class Cat(models.Model):
    _name = 'cat'
    _description = 'Cat Model'
    _inherit = 'animal'

    description = fields.Html(string='Description', required=False, sanitize_tags=False)
    gender = fields.Selection(selection_add=[('undefined', 'Undefined'), ('unknown', 'UnKnown')], default='male', ondelete={'undefined': 'cascade'})
    player_ids = fields.Many2many(string='Owner', comodel_name='player')

    def sound(self):
        super(Cat, self).sound()
        return "Meow meow..."

    def create_cat(self):
        new_cat = {
            'name': self.name,
            'gender': self.gender,
            'color': self.color,
            'age': self.age
        }

        return self.env['cat'].create(new_cat)
