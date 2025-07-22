import werkzeug

from odoo import http
from odoo.http import request
import json


class TestController(http.Controller):
    @http.route(['/api/test_return', '/api/itest_return'], auth='public', type='http', website=True)
    def test_return(self):
        return "Hello world! - Parrent"

    @http.route('/api/test_args/<int:id>', auth='public', type='http', website=True)
    def test_args(self, id):
        return "Hello world! %s - Parrent!" % str(id)

    @http.route('/api/test_redirect', type='http', auth='public', website=True)
    def test_redirect(self):
        return werkzeug.utils.redirect('https://vnexpress.net')

    @http.route('/api/test_render', type='http', auth='public', website=True)
    def test_render(self, **kw):
        return request.render('web.login')

    @http.route('/api/test_json', type='http', auth="public", website=True)
    def test_json(self, **kwargs):
        return json.dumps({'iMessage': 'iPhone 17 prm is coming up...'})

    @http.route('/api/test_create', type='http', auth='public', website=True)
    def test_create(self, **kwargs):
        partner = request.env['res.partner'].sudo().create({
            'name': 'Mr. Jira'
        })

        return "A new partner %s has been created" % partner.name
