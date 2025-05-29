from odoo import http


class silkworm_rush_orders(http.Controller):
    @http.route('/orders/rush/', auth='public')
    def index(self, **kw):
        orders = http.request.env['sale.order']
        lstrushorders = orders.search([('rush', '=', True),('state','=','sale')])
        return http.request.render('silkworm.rush_orders_template', {'myrushorders': lstrushorders})
