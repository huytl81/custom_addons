import werkzeug

from odoo import http, api
from odoo.http import request
import json

from odoo.http import Response

class Controller(http.Controller):
    @http.route(['/api/test_return', '/api/itest_return'], auth='public', type='http', website=True)
    def test_return(self):
        return "Hello world! - abstract!"

    @http.route('/api/test_args/<int:id>/<string:name>/<string:age>', auth='public', type='http', website=True)
    def test_args(self, **kwargs):
        try:
            id = kwargs['id']
            name = kwargs['name']
            age = kwargs['age']
            age_val = float(age)
        except ValueError:
            return "Age must be a number!"

        data = {
            'id': id,
            'name': name,
            'age': age_val,
            'message': 'Modified in abstract class!'
        }

        return Response(json.dumps(data), content_type='application/json;charset=utf-8')

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
        telegram = {
            'name': 'Mr Telegram'
        }
        zalo = {
            'name': 'Ms Zalo'
        }
        values = [telegram, zalo]

        request.env['res.partner'].sudo().create(values)

        return "Some new partners has been created!"