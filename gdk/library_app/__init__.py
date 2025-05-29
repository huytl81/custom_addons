# -*- coding: utf-8 -*-

from . import models
from . import wizard
from odoo import api, fields, SUPERUSER_ID


def add_book_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {}, True)
    book_data1 = {'name': 'Book 1', 'published_date': fields.Date.today()}
    book_data2 = {'name': 'Book 2', 'published_date': fields.Date.today()}
    values = {'book_data': ([book_data1, book_data2])}
    env['library.book'].create(values)
