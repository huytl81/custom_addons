from odoo import http, api
from .controller import Controller
import json

from odoo.http import Response


class ControllerInherited(Controller):
    @http.route(['/api/test_return', '/api/itest_return'], auth='public', type='http', website=True)
    def test_return(self):
        super(ControllerInherited, self).test_return()
        return "Hello world! - inherited"

    @http.route('/api/test_args/<int:id>/<string:name>/<string:age>', auth='public', type='http', website=True)
    def test_args(self, **kwargs):
        result = super(ControllerInherited, self).test_args(**kwargs)
        # If you need to modify the parent's response, you can do it here
        # For example, to modify the response data:
        if isinstance(result, Response):
            data = json.loads(result.data)
            data['message'] = 'Modified in inherited class'
            return Response(json.dumps(data), content_type='application/json;charset=utf-8')
        return result
