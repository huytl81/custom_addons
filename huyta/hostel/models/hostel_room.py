import logging
from odoo import models, fields, api
from odoo.osv.expression import TRUE_LEAF
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class BaseArchive(models.AbstractModel):
    _name = 'base.archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


class HostelRoom(models.Model):
    _name = "hostel.room"
    _description = "Hostel Room"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'base.archive']
    _sql_constraints = [("room_no_unique", "unique(room_number)", "Room number must be unique!")]

    name = fields.Char(string="Room Name", required=True)
    description = fields.Text(string="Description")
    room_number = fields.Char(string="Room Number", required=True)
    floor = fields.Integer(string="Floor")
    room_type = fields.Selection([('single', 'Single'), ('double', 'Double'), ('triple', 'Triple')], string="Room Type")
    image = fields.Binary(string="Image")
    state = fields.Selection([('draft', 'Unavailable'), ('available', 'Available'), ('closed', 'Closed')],string='State', default='draft')
    # active = fields.Boolean(string="Active", default=True)
    hostel_id = fields.Many2one(comodel_name='hostel.hostel', string="Hostel Name", ondelete='restrict')
    currency_id = fields.Many2one(comodel_name="res.currency", string="Currency")
    # hostel_currency = fields.Many2one(comodel_name="res.currency", string="Currency", currency_field='currency_id')
    # optional attribute: currency_field = 'currency_id' incase currency field have another name then 'currency_id'
    rent_amount = fields.Monetary('Rent Amount', help="Enter rent amount per month")
    cost_price = fields.Float('Room Cost', help="Enter room cost per month")
    category_id = fields.Many2one(comodel_name='hostel.room.category', string="Hostel Room Category")
    student_ids = fields.One2many(comodel_name="hostel.student", inverse_name="room_id", string="Students")
    member_ids = fields.Many2many('hostel.room.member', string='Members')
    hostel_amenities_ids = fields.Many2many("hostel.amenities", "hostel_room_amenities_rel", "room_id", "amenity_id",string="Amenities", domain="[('active', '=', True)]", help="Select hostel room amenities")
    occupancy = fields.Integer(string="Occupancy", required=True, store=True, help="Number of students in the room")
    availability = fields.Integer(string="Availability", compute="_compute_check_availability", store=True, help="Room availability in hostel")
    room_rating = fields.Float('Rooms Average Rating', digits='Rating Value')
    remarks = fields.Text('Remarks')
    previous_room_id = fields.Many2one('hostel.room', string='Previous Room')
    allocation_date = fields.Date(string="Allocation Date")

    @api.model_create_multi
    def create(self, values_list):
        # Ensure values is always a list
        # if isinstance(values, dict):
        #     values_list = [values]
        # else:
        #     values_list = values

        if not self.env.user.has_groups('hostel.group_hostel_room_manager'):
            for vals in values_list:
                if vals.get('remarks'):
                    raise UserError(_('You are not allowed to modify remarks'))

        return super().create(values_list)

    def write(self, values):
        if not self.env.user.has_groups('hostel.group_hostel_room_manager'):
            if values.get('remarks'):
                raise UserError('You are not allowed to modify remarks')

        if self.env.context.get('loop_breaker'):
            return
        self.with_context(loop_breaker=True)
        # self.compute_things()  # can cause calls to writes
        return super(HostelRoom, self).write(values)

    @api.model
    def _update_room_rent_amount(self):
        all_rooms = self.search([])
        for room in all_rooms:
            room.rent_amount += 10

    @api.model
    def _update_room_cost_price(self, category_id, amount_to_increase):
        # NOTE: Real cases can be complex but here we just increase cost price by 10
        _logger.info('Method update_room_price called from XML')
        category_rooms = self.search([('category_id', '=', category_id)])
        for room in category_rooms:
            room.cost_price += amount_to_increase

    @api.constrains("rent_amount")
    def _check_rent_amount(self):
        for record in self:
            if record.rent_amount < 0:
                msg = _("Rent Amount Per Month should not be a negative value!")
                raise ValidationError(msg)

    @api.depends("occupancy", "student_ids")
    # @api.depends_context("occupancy", "student_ids")
    def _compute_check_availability(self):
        for record in self:
            record.availability = record.occupancy - len(record.student_ids.ids)

    @api.model
    def _is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'), ('available', 'closed'), ('closed', 'draft')]
        return (old_state, new_state) in allowed

    def _change_state(self, new_state):
        for record in self:
            if record._is_allowed_transition(record.state, new_state):
                record.state = new_state
            else:
                msg = _("Moving from %s to %s is not allowed") % (record.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self._change_state('available')

    def make_closed(self):
        self._change_state('closed')

    def log_all_members(self):
        hostel_members_obj = self.env['hostel.room.member']
        members = hostel_members_obj.search([])
        print("Room Members: ", members)
        return True

    def update_room_no(self):
        self.ensure_one()

        # Option 1: Directly assign the room number
        self.room_number = "R001"

        # Option 2: Use update method
        # self.update({
        #     'room_number': "R001",
        #     'floor': 1
        # })

        # Option 3: Use write method
        # self.write({
        #     'room_number': "R001",
        #     'floor': 3,
        #     'state': 'available'
        # })

    def find_room(self):
        domain = [
            '|',
            '&', ('name', 'ilike', 'A25'),
            ('room_number', 'ilike', '01'),
            '&', ('name', 'ilike', 'Mai'),
            ('room_number', 'ilike', '02')
        ]
        # rooms = self.search(domain, offset=0, limit=1000, order='name', count='False')
        rooms = self.search(domain)
        _logger.info('Rooms found %s', rooms)
        return True

    def filter_rooms(self):
        rooms = self.search([])
        # filtered_rooms = self.room_with_multiple_members(rooms)
        filtered_rooms = rooms.filtered(lambda r: len(r.member_ids) > 1)
        _logger.info('Filtered rooms %s', filtered_rooms)
        return True

    @api.model
    def room_with_multiple_members(self, rooms):
        def predicate(room):
            if len(room.member_ids) > 1:
                return True
            else:
                return False

        return rooms.filtered(predicate)

    # Traversing recordset
    def mapped_rooms(self):
        all_rooms = self.search([])
        room_members = self.get_member_names(all_rooms)

        _logger.info('Rooms Members: %s', room_members)

    @api.model
    def get_member_names(self, rooms):
        return rooms.mapped('member_ids.name')

    # Sorting recordset
    def sort_room(self):
        all_rooms = self.search([])
        # rooms_sorted = self.sort_rooms_by_rating(all_rooms)
        rooms_sorted = all_rooms.sorted(key='room_rating', reverse=True)

        _logger.info('Rooms before sorting: %s', all_rooms)
        _logger.info('Rooms after sorting: %s', rooms_sorted)

    @api.model
    # def sort_rooms_by_rating(self, rooms):
    #     return rooms.sorted(key='room_rating', reverse=True)

    def name_get(self):
        result = []
        for room in self:
            student_name = room.student_ids.mapped('name')
            name = '%s (%s)' % (room.name, ','.join(student_name))
            result.append((room.id, name))
        return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|', '|',
                     ('name', operator, name),
                     ('room_number', operator, name),
                     ('student_ids.name', operator, name)
                     ]
        return super(HostelRoom, self)._name_search(name=name, args=args, operator=operator, limit=limit,name_get_uid=name_get_uid)

    def grouped_data(self):
        grouped_data = self._get_average_cost(self)
        _logger.info('Grouped data %s', grouped_data)

    @api.model
    def _get_average_cost(self):
        grouped_data = self.env['hostel.room'].read_group(
            domain=['cost_price', '!=', 0],
            #fields=['category_id', 'cost_price:avg'],
            fields=['category_id', 'average_price:avg(cost_price)'],
            groupby=['category_id'],
            orderby='cost_price desc')
        return grouped_data


