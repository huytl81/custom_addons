from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_hostel_rector = fields.Boolean("Hostel Rector", help="Activate if the following person is hostel rector")
    assign_room_ids = fields.Many2many('hostel.room', string='Assigned Rooms')
    count_assign_room = fields.Integer( 'Number of Assigned Rooms', compute="_compute_count_room", store=True)

    @api.depends('assign_room_ids')
    def _compute_count_room(self):
        for record in self:
            record.count_assign_room = len(record.assign_room_ids)