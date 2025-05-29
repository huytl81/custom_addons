# # -*- coding: utf-8 -*-
# from werkzeug.exceptions import BadRequest
# from odoo import models
# from odoo.http import request
#
#
# import ast
# import datetime
# import json
# import logging
#
# import werkzeug.wrappers
#
# _logger = logging.getLogger(__name__)
#
#
# def default(o):
#     if isinstance(o, (datetime.date, datetime.datetime)):
#         return o.isoformat()
#     if isinstance(o, bytes):
#         return str(o)
#
#
# def valid_response(data, status=200):
#     """Valid Response
#     This will be return when the http request was successfully processed."""
#     data = {"count": len(data) if not isinstance(data, str) else 1, "data": data}
#     return werkzeug.wrappers.Response(
#         status=status, content_type="application/json; charset=utf-8", response=json.dumps(data, default=default),
#     )
#
#
# def invalid_response(typ, message=None, status=401):
#     """Invalid Response
#     This will be the return value whenever the server runs into an error
#     either from the client or the server."""
#     # return json.dumps({})
#     return werkzeug.wrappers.Response(
#         status=status,
#         content_type="application/json; charset=utf-8",
#         response=json.dumps(
#             {"type": typ, "message": str(message) if str(message) else "wrong arguments (missing validation)",},
#             default=datetime.datetime.isoformat,
#         ),
#     )
#
#
# def extract_arguments(limit="80", offset=0, order="id", domain="", fields=[]):
#     """Parse additional data  sent along request."""
#     limit = int(limit)
#     expresions = []
#     if domain:
#         expresions = [tuple(preg.replace(":", ",").split(",")) for preg in domain.split(",")]
#         expresions = json.dumps(expresions)
#         expresions = json.loads(expresions, parse_int=True)
#     if fields:
#         fields = fields.split(",")
#
#     if offset:
#         offset = int(offset)
#     return [expresions, fields, offset, limit, order]
#
#
# class VttIrHttp(models.AbstractModel):
#     _inherit = 'ir.http'
#
#     @classmethod
#     def _auth_method_custom_auth(cls):
#         abc = ''
#         # access_token = request.httprequest.headers.get("access_token")
#         # if not access_token:
#         #     return invalid_response("access_token_not_found", "missing access token in request header", 401)
#         # access_token_data = request.env["vtt.api.access.token"].sudo().search([("token", "=", access_token)],
#         #                                                                       order="id DESC", limit=1)
#         #
#         # if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
#         #     return invalid_response("access_token", "token seems to have expired or invalid", 401)
#         # request.update_env(user=access_token_data.user_id)
#         # u = request.env.user
#         cc = ''
#
