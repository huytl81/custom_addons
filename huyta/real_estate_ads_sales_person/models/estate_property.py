from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    seller_id = fields.Many2one('res.users', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sales_person_property_ids = self.env[self._name].search_count([('seller_id', '=', vals.get('seller_id'))])
            if sales_person_property_ids > 8:
                raise ValidationError(_("You cannot create more than 8 properties per sales person"))
        return super(EstateProperty, self).create(vals_list)
