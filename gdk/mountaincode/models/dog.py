from odoo import fields, models


class Dog(models.Model):
    _name = 'dog'
    _description = 'Dog Model'
    _inherit = 'animal'

    description = fields.Html('Description', required=False)
    image = fields.Image('Image', max_width=512, max_height=512)
    father_cv = fields.Binary(string='Father CV', attachment=True)
    mother_cv = fields.Binary(string='Father CV', attachment=False)
    others = fields.Text(string='Other info')
    gender = fields.Selection(selection_add=[('undefined', 'Undefined'),('male',)], ondelete={'undefined': 'set null'})

    def _sound(self):
        super(Dog, self)._sound()
        return "Gru gru..."


    def create_dog(self):
        return {
            'name': 'Create Dog',
            'res_model': 'dog.wizard',
            'view_mode': 'form',
            'target': 'new',
            'type': 'ir.actions.act_window'
        }
