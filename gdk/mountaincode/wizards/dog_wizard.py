from odoo import _, api, fields, models, SUPERUSER_ID


class DogWizard(models.TransientModel):
    _name = 'dog.wizard'
    # _inherits = 'animal'
    _description = 'Dog Wizard'

    name = fields.Char('Name', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    color = fields.Char('Color')
    age = fields.Float('Age')

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

        #
        # dog2 = {
        #     'name': 'dog2222',
        #     'gender': 'Male',
        #     'color': 'Blue',
        #     'age': '12'
        # }
        #
        # values = {'dog_batch': ([dog1, dog2])}
        # env['dog'].create(values)

        # dog3 = {
        #     'name': 'dog3333',
        #     'gender': 'Female',
        #     'color': 'Green',
        #     'age': '6'
        # }


