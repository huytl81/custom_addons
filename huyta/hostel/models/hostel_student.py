from datetime import timedelta
from odoo import fields, models, api


class HostelStudent(models.Model):
    _name = "hostel.student"
    _description = "Hostel Student"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'partner_id'}
    
    name = fields.Char("Student Name")
    gender = fields.Selection([("male", "Male"),("female", "Female"), ("other", "Other")], string="Gender", help="Student gender")
    active = fields.Boolean("Active", default=True, help="Activate/Deactivate hostel record")
    room_id = fields.Many2one("hostel.room", "Room", help="Select hostel room", ondelete='restrict')
    hostel_id = fields.Many2one("hostel.hostel", string="Hostel Name", related="room_id.hostel_id")
    admission_date = fields.Date('Admission Date', help='Enter student admission date', default=fields.Datetime.today)
    discharge_date = fields.Date('Discharge Date', help='Enter student discharge date')
    duration = fields.Integer('Duration', help='Enter student duration of living in hostel', compute='_compute_check_duration', inverse='_inverse_duration')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    # delegate inherit 
    #partner_id = fields.Many2one(comodel_name='res.partner', delegate=True, ondelete='cascade')

    @api.depends('admission_date', 'discharge_date')
    def _compute_check_duration(self):
        for record in self:
            if record.admission_date and record.discharge_date:
                record.duration = (record.discharge_date - record.admission_date).days

    def _inverse_duration(self):
        for record in self:
            if record.admission_date and record.discharge_date:
                duration = (record.discharge_date - record.admission_date).days
                if duration != record.duration:
                    record.discharge_date = record.admission_date + timedelta(record.duration)
