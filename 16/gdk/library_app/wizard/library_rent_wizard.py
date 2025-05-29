from odoo import models, fields


class LibraryRentWizard(models.TransientModel):
    _name = 'library.rent.wizard'

    borrower_id = fields.Many2one('res.partner', string='Borrower')
    book_ids = fields.Many2many('library.book', string='Books')

    def add_book_rents(self):
        # rent_model = self.env['library.book.rent']
        # for rec in self:
        #     for book in rec.book_ids:
        #         rent_model.create({
        #             'borrower_id': self.borrower_id.id,
        #             'book_id': book.id
        #         })
        self.ensure_one()
        rent_model = self.env['library.book.rent']
        for book in self.book_ids:
            rent_model.create({
                'borrower_id': self.borrower_id.id,
                'book_id': book.id
            })

        borrowers = self.mapped('borrower_id')
        action = borrowers.get_formview_action()
        if len(borrowers.ids) > 1:
            action['domain'] = [('id', 'in', tuple(borrowers.ids))]
            action['view_mode'] = 'tree,form'
        return action
