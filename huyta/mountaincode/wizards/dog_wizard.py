from odoo import _, api, fields, models, SUPERUSER_ID


class DogWizard(models.TransientModel):
    _name = 'dog.wizard'
    _description = 'Dog Wizard'

    name = fields.Char('Name', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    color = fields.Char('Color')
    age = fields.Float('Age', store=True)
    bod = fields.Integer(string='Birth of Date')

    def create_dog(self):
        # for d in self:
        #     self.env['dog'].create({'name': d.name})
        #env = api.Environment(cr, SUPERUSER_ID, {}, True)

        self.ensure_one()
        new_dog = {
            'name': self.name,
            'gender': self.gender,
            'color': self.color,
            'age': self.age
        }

        return self.env['dog'].create(new_dog)

        # dog1 = {
        #     'name': 'dog3333',
        #     'gender': 'female',
        #     'color': 'Green',
        #     'age': '6'
        # }
        #
        #
        # dog2 = {
        #     'name': 'dog2222',
        #     'gender': 'male',
        #     'color': 'Blue',
        #     'age': '12'
        # }
        #
        # values = [dog1, dog2]
        # return self.env['dog'].create(values)




