from odoo import http, api
from odoo.addons.mountaincode.controllers.test_controller import TestController
from odoo.api import returns


class TestController(TestController):
    @http.route(['/api/test_return', '/api/itest_return'], auth='public', type='http', website=True)
    def test_return(self):
        super(TestController, self).test_return()
        return "Hello world! - Children"

    @http.route('/api/test_args/<int:id>', auth='public', typy='http', wesite='True')
    def test_args(self, id):
        super(TestController, self).test_args(id)
        return "Hello world! %s - Children" % str(id)
