from datetime import timedelta

from odoo import models, api, fields
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

class HostelRoom(models.Model):
    _inherit = 'hostel.room'

    category_id = fields.Many2one("hostel.room.category", string="Category")
    date_terminate = fields.Date('Date of Termination', help='Enter date of termination')

    def make_closed(self):
        day_to_allocate = self.category_id.max_allow_days or 10
        self.date_terminate = fields.Date.today() + timedelta(days=day_to_allocate)
        return super(HostelRoom,self).make_closed()

    def make_available(self):
        self.date_terminate = False
        return super(HostelRoom,self).make_available()