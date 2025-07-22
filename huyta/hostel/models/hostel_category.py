from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HostelCategory(models.Model):
    _name = 'hostel.category'
    _description = "Hostel Category"
    _parent_store = True
    _parent_name = "parent_id"  # optional if field is 'parent_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Category Name", required=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    hostel_ids = fields.One2many(comodel_name='hostel.hostel', inverse_name='category_id', string="Hostels")
    hostel_count = fields.Integer(string="Hostel Count", compute="_compute_hostel_count")
    parent_id = fields.Many2one(comodel_name='hostel.category', string='Parent Category', ondelete='restrict', index=True)
    child_ids = fields.One2many(comodel_name='hostel.category', inverse_name='parent_id', string='Children Categories')
    parent_path = fields.Char(index=True, unaccent=False)

    @api.depends('hostel_ids')
    def _compute_hostel_count(self):
        for record in self:
            record.hostel_count = len(record.hostel_ids)

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if self._has_cycle():
            raise ValidationError('Error! You cannot create recursive categories.')