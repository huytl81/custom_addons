# -*- coding: utf-8 -*-
# from odoo import http


# class Hostel(http.Controller):
#     @http.route('/hostel/hostel', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hostel/hostel/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hostel.listing', {
#             'root': '/hostel/hostel',
#             'objects': http.request.env['hostel.hostel'].search([]),
#         })

#     @http.route('/hostel/hostel/objects/<model("hostel.hostel"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hostel.object', {
#             'object': obj
#         })

