# -*- coding: utf-8 -*-
# from odoo import http


# class SilkwormApi(http.Controller):
#     @http.route('/silkworm_api/silkworm_api', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/silkworm_api/silkworm_api/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('silkworm_api.listing', {
#             'root': '/silkworm_api/silkworm_api',
#             'objects': http.request.env['silkworm_api.silkworm_api'].search([]),
#         })

#     @http.route('/silkworm_api/silkworm_api/objects/<model("silkworm_api.silkworm_api"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('silkworm_api.object', {
#             'object': obj
#         })

