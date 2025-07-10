from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

class HostelRoomCategory(models.Model):
    _inherit='hostel.room.category'

    max_allow_days = fields.Integer(string='Maximum Allowed Days', help='For how many days the room can be borrowed', default=10)
