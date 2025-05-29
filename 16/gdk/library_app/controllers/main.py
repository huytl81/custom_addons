# -*- coding: utf-8 -*-
from odoo import http


class Books(http.Controller):
    @http.route("/library/books", auth="public", website=True)
    def list(self, **kwargs):
        book = http.request.env["library.book"]
        books = book.search([])
        authors = book.get_author_names(books)
        return http.request.render("library_app.book_list_template", {"books": books, "authors": authors})
        # response = http.request.render("library_app.book_list_template", {"books": books})
        return response
