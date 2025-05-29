# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta

from odoo.tests import Form

_logger = logging.getLogger(__name__)


class Book(models.Model):
    _name = "library.book"
    _description = "Book"
    _order = "name,date_published desc"
    # _log_access = False: This can be used to prevent audit tracking fields from being automatically created;
    # that is, create_uid, create_date, write_uid, and write_date.
    _log_access = True
    # _auto = False: This prevents the underlying database table from being automatically created.\
    # In this case, we should use the init() method to provide our specific logic for creating the supporting database object,
    # a table, or a view.This is usually used for views that support read-only reports.
    _auto = True
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin","base.archive"]

    @api.constrains("isbn")
    def _constrain_isbn_valid(self):
        for book in self:
            if book.isbn and not book._check_isbn():
                raise models.ValidationError("%s is an invalid ISBN" % book.isbn)

    @api.constrains("date_published")
    def _constraint_date_published(self):
        for book in self:
            if book and book.date_published:
                if book.date_published > fields.Date.today():
                    raise models.ValidationError("Publication date must not be in the future.")
            else:
                raise models.ValidationError("Please enter Issued date!")

    name = fields.Char("Book Title", default=None, help="Book cover title.", readonly=False, required=True, index=True, copy=False, deprecated=True, groups="base.group_user")
    short_name = fields.Char('Short Title', translate=True, index=True)
    isbn = fields.Char("ISBN")
    book_type = fields.Selection(
        [("paper", "Paperback"),
         ("hard", "Hardcover"),
         ("electronic", "Electronic"),
         ("other", "Other")], string="Type")
    notes = fields.Text("Internal Notes")
    state = fields.Selection(
        [('draft', 'UnAvailable'),
         ('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],string='State', default="draft")
    description = fields.Html('Description', sanitize=True, strip_style=False)

    # price helper
    currency_id = fields.Many2one("res.currency", string='Currency')

    # Numeric fields:
    copies = fields.Integer(default=1)
    out_of_print = fields.Boolean()
    pages = fields.Integer('Number of Pages', groups='base.group_user', states={'lost': [('readonly', True)]}, help='Total book page count', company_dependent=False)
    reader_rating = fields.Float("Reader Average Rating", (14, 4))
    cost_price = fields.Float('Book cost', digits='Product Price')
    retail_price = fields.Monetary("Retail Price", currency_field='currency_id')
    # category_id = fields.Many2one('library.book.category', 'Category')
    category_ids = fields.Many2many(comodel_name="library.book.category", relation="library_book_library_book_category_rel", column1="library_book_id", column2="library_book_category_id", string="Book Categories")

    # Date and time fields:
    date_published = fields.Date("Date Issued")
    date_updated = fields.Datetime('Last Updated')

    # last_borrow_date = fields.Datetime("Last Borrowed On", default=lambda self: fields.Datetime.now())
    # last_borrow_date = fields.Datetime("Last Borrowed On", default="_default_last_borrow_date")
    def _default_last_borrow_date(self):
        return fields.Datetime.now()

    last_borrow_date = fields.Datetime("Last Borrowed On", default=_default_last_borrow_date)

    # Other fields:
    active = fields.Boolean("Active?", default=True)
    image = fields.Binary("Cover")

    # Relational Fields
    publisher_id = fields.Many2one("res.partner", string="Publisher", ondelete='set null', context={}, domain=[])
    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)
    author_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="library_book_res_partner_rel",
        column1="library_book_id",
        column2="res_partner_id",
        string="Authors")

    # publisher_country_id = fields.Many2one(
    #     "res.country",
    #     string="Publisher Country",
    #     related="publisher_id.country_id",
    #     readonly=False,
    # )

    publisher_country_id = fields.Many2one("res.country", string="Publisher Country", compute="_compute_publisher_country", inverse="_inverse_publisher_country", search="_search_publisher_country", readonly=False)

    age_days = fields.Float(string="Days Since Release", compute="_compute_age", inverse="_inverse_age", search="_search_age", store=False, compute_sudo=True)

    is_public = fields.Boolean(groups='library_app.library_group_manager')
    private_notes = fields.Text(groups='library_app.library_group_manager')

    @api.model
    def _referencable_models(self):
        _models = self.env['ir.model'].sudo().search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in _models]

    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    manager_remarks = fields.Text('Manager Remarks')
    old_edition = fields.Many2one('library.book', string='Old Edition', search="_name_search")

    _sql_constraints = [("library_book_name_uq", "UNIQUE (name)", "Title must be unique."),
                        ("library_book_positive_page", "CHECK (pages > 0)", "No of pages must be positive.")]

    @api.depends("publisher_id.country_id")
    def _compute_publisher_country(self):
        for book in self:
            book.publisher_country_id = book.publisher_id.country_id

    def _inverse_publisher_country(self):
        for book in self:
            book.publisher_id.country_id = book.publisher_country_id

    def _search_publisher_country(self, operator, value):
        return [("publisher_id.country_id", operator, value)]

    @api.depends("date_published")
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_published:
                delta = today - book.date_published
                book.age_days = delta.days
            else:
                book.age_days = 0

    def _inverse_age(self):
        today = fields.Date.today()
        books = self.filtered("date_published")
        for book in books:
            if book.age_days:
                delta = today - timedelta(book.age_days)
                book.date_published = delta
            else:
                book.date_published = today

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {
            '>': '<', '>=': '<=',
            '<': '>', '<=': '>=',
        }
        new_op = operator_map.get(operator, operator)
        return [('date_published', new_op, value_date)]

    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 13:
            ponderations = [1, 3] * 6
            terms = [a * b for a, b in zip(digits[:12], ponderations)]
            remain = sum(terms) % 10
            check = 10 - remain if remain != 0 else 0
            return digits[-1] == check

    def button_check_isbn(self):
        for book in self:
            if not book.isbn:
                raise ValidationError("Please provide an ISBN for % s" % book.name)
            if book.isbn and not book._check_isbn():
                raise ValidationError("%s ISBN is invalid" % book.isbn)
            else:
                raise ValidationError("%s ISBN is valid" % book.isbn)
        return True

    # def init(self):
    #     tools.drop_view_if_exists(self.env.cr, self._table)
    #     self.env.cr.execute("CREATE or REPLACE VIEW %s as (%s)" % (self._table, self._query()))

    def name_get(self):
        result = []
        for record in self:
            authors = record.author_ids.mapped('name')
            rec_name = "%s - (%s)" % (record.name, ' & '.join(authors))
            result.append((record.id, rec_name))
        return result

    @api.model
    def _name_search(self, name='', domain=None, operator='ilike', limit=300, order=None):
        domain = [] if domain is None else domain.copy()
        if not (name == '' and operator == 'ilike'):
            domain += ['|', '|', ('name', operator, name), ('isbn', operator, name), ('author_ids.name', operator, name)]
        return super(Book, self)._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group([('cost_price', "!=", False)], fields=['publisher_id', 'average_cost:avg(cost_price)'], groupby=['publisher_id'])
        return grouped_result

    def grouped_data(self):
        data = self._get_average_cost()
        _logger.info("Groupped Data %s" % data)
        print("Groupped Data %s" % data)

    @api.model
    def _is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                    ('available', 'borrowed'),
                    ('borrowed', 'available'),
                    ('available', 'lost'),
                    ('borrowed', 'lost'),
                    ('lost', 'available')]
        return (old_state, new_state) in allowed

    def _change_state(self, new_state):
        for record in self:
            if record._is_allowed_transition(record.state, new_state):
                record.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (record.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self._change_state('available')

    def make_borrowed(self):
        self._change_state('borrowed')

    def make_lost(self):
        # self._change_state('lost')
        self.ensure_one()
        self.state = 'lost'
        if not self.env.context.get('avoid_deactivate'):
            self.active = False

    # update option 1
    def update_release_date(self):
        self.ensure_one()
        self.update({
            'date_published': fields.Datetime.now(),
            # 'another_field': 'value'
        })

    # update option 2
    # def update_release_date(self):
    #     self.ensure_one()
    #     self.date_published = fields.Date.today()

    # update option 3
    # def update_release_date(self):
    #     for record in self:
    #         book_val = {'date_published': [(1, record.id, fields.Datetime.now())]}
    #     self.write(book_val)

    def find_book(self):
        domain = [
            '|',
            '&', ('name', 'ilike', 'Book Name'), ('category_id.name', 'ilike', 'Category Name'),
            '&', ('name', 'ilike', 'Book Name 2'), ('category_id.name', 'ilike', 'Category Name 2')
        ]
        books = self.search(domain,offset=0,limit=None,order="name",count=False)
        return books

    def books_count(self):
        domain = [
            '|',
            '&', ('name', 'ilike', 'Book Name'), ('category_id.name', 'ilike', 'Category Name'),
            '&', ('name', 'ilike', 'Book Name 2'), ('category_id.name', 'ilike', 'Category Name 2')
        ]
        books_count = self.search_count(domain,offset=0,limit=None,order="name")
        return books_count

    def find_partner(self):
        partner_obj = self.env['res.partner']
        domain = ['&', ('name', 'ilike', 'Parth Gajjar'), ('company_id.name', '=', 'Odoo')]
        partners = partner_obj.search(domain)
        return partners

    # filter option 1
    # @api.model
    # def books_with_multiple_authors(self, all_books):
    #     def predicate(book):
    #         if len(book.author_ids) > 1:
    #             return True
    #         return False
    #     return all_books.filter(predicate)

    # filter option 2
    @api.model
    def books_with_multiple_authors(self, all_books):
        return all_books.filter(lambda b: len(b.author_ids) > 1)

    @api.model
    def get_author_names(self, books):
        list_author_names = books.mapped('author_ids.name')
        str_author_names = str(list_author_names)
        result = str_author_names.strip("[]").replace("'", "")
        return result

    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='date_published')

    @api.model
    def create(self, values):
        if not self.user_has_groups('library_app.library_group_manager'):
            if 'manager_remarks' in values:
                raise UserError('You are not allowed to create '
                                'manager_remarks')
                # del values['manager_remarks']
        return super(Book, self).create(values)

    def write(self, values):
        if not self.user_has_groups('library_app.library_group_manager'):
            if 'manager_remarks' in values:
                # raise UserError('You are not allowed to modify manager_remarks')
                del values['manager_remarks']
                sup = super(Book, self).write(values)
                if self.env.context.get('flag'):
                    return
                self = self.with_context(flag=True)
                # self.compute_things() # can cause calls to writes
                return sup
        return super(Book, self).write(values)

    @api.model
    def _update_book_price(self):
        all_books = self.search([])
        for book in all_books:
            book.cost_price += 10

    @api.model
    def update_book_price(self, category, amount_to_increase):
        category_books = self.search([('category_ids', '=', category.id)])
        for book in category_books:
            book.cost_price += amount_to_increase

    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({
            'book_id': self.id,
            'borrower_id': self.env.user.partner_id.id,
        })
        # public_user = self.env.ref('base.public_user')
        # public_book = self.env['library.book'].with_user(public_user)
        # public_book.search([('name', 'ilike', 'cookbook')])

    def average_book_occupation(self):
        self.env.flush_all()
        sql_query = """
            SELECT lb.name, avg((EXTRACT(epoch from age(return_date, rent_date)) / 86400))::int
            FROM library_book_rent AS lbr
            JOIN library_book as lb ON lb.id = lbr.book_id
            WHERE lbr.state = 'returned'
            GROUP BY lb.name;
            """
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        _logger.info("Average book occupation: %s", result)

    # def return_all_books(self):
    #     self.ensure_one()
    #     wizard = self.env['library.return.wizard']
    #     with Form(wizard) as return_form:
    #         return_form.borrower_id = self.env.user.partner_id.id
    #         record = return_form.save()
    #         record.books_returns()

    def return_all_books(self):
        self.ensure_one()
        wizard = self.env['library.return.wizard']
        record = wizard.create({'borrower_id': self.env.user.partner_id.id})
        record.books_returns()