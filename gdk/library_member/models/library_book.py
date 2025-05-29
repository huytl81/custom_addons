# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Book(models.Model):
    _inherit = "library.book"

    is_available = fields.Boolean("Is Available?")
    isbn = fields.Char(help="Use a valid ISBN - 13 or ISBN - 10.")
    publisher_id = fields.Many2one(index=True)

    def _check_isbn(self):
        self.ensure_one()
        digits = [int(x) for x in self.isbn if x.isdigit()]
        if len(digits) == 10:
            ponderators = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            terms = [a * b for a, b in zip(digits[:9], ponderators)]
            total = sum(terms)
            remains = total % 11
            return digits[-1] == remains
        else:
            return super()._check_isbn()

    def log_all_library_members(self):
        # This is an empty recordset of model library member
        library_member_model = self.env['library.member']
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True