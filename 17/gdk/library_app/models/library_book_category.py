from odoo import models, fields, api


class BookCategory(models.Model):
    _name = "library.book.category"
    _description = "Book Category"
    _parent_store = True
    _parent_name = 'parent_id'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(translate=True, required=True)
    description = fields.Html(translate=True, required=False)
    # Hierarchy fields
    parent_id = fields.Many2one("library.book.category", "Parent Category", ondelete="set null")
    parent_path = fields.Char(index=True)
    # Optional, but nice to have:
    child_ids = fields.One2many(comodel_name="library.book.category",inverse_name="parent_id",string="Sub Categories")
    books_ids = fields.Many2many(comodel_name="library.book", relation="library_book_library_book_category_rel", column1="library_book_category_id", column2="library_book_id", string="Books")
    highlighted_id = fields.Reference([("library.book", "Book"), ("res.partner", "Author")], "Category Highlight")

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')

    def create_categories(self):
        cat1 = {
            'name': 'Child category 1',
            'description': 'Description for child 1'
        }
        cat2 = {
            'name': 'Child category 2',
            'description': 'Description for child 2'
        }

        # self.env['library.book.category'].create([cat1, cat2])
        #
        # parent_category_val = {
        #     'name': 'Parent category',
        #     'description': 'Description for parent category',
        #     'child_ids': [
        #         (6, 0, [46,47])
        #     ]
        # }
        # self.env['library.book.category'].create(parent_category_val)

        parent_category_val = {
            'name': 'Parent category',
            'description': 'Description for parent category',
            'child_ids': [
                (0, 0, cat1),
                (0, 0, cat2)
            ]
        }
        self.create(parent_category_val)