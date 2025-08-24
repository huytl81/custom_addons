from odoo import http
from odoo.http import request


class PropertyController(http.Controller):
        @http.route(['/properties'], type='http', website=True, auth='public')
        def show_properties(self):
            properties =  request.env['estate.property'].sudo().search([])
            print(properties)
            return request.render('real_estate_ads.properties_list', {'properties': properties})