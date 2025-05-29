# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.library_portal.controllers.main import Books


class BookExtended(Books):
    @http.route()
    def all_books(self, **kwargs):
        response = super().all_books(**kwargs)
        if kwargs.get("available"):
            all_books = response.qcontext["books"]
            available_books = all_books.filtered("is_available")
            response.qcontext["books"] = available_books
        return response
