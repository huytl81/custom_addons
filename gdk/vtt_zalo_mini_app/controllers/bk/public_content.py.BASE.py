# -*- coding: utf-8 -*-
import hashlib
import hmac
import random

import requests

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import json
import datetime
import base64
import xmlrpc.client as xmlrpclib
# import jwt
from datetime import datetime, timedelta

from odoo import api
from odoo.tools import image_guess_size_from_field_name

import logging
_logger = logging.getLogger(__name__)

class PublicContentAPI(http.Controller):
    @http.route(['/vtt/image',
                 '/vtt/image/<string:xmlid>',
                 '/vtt/image/<string:xmlid>/<string:filename>',
                 '/vtt/image/<string:xmlid>/<int:width>x<int:height>',
                 '/vtt/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',

                 '/vtt/image/<string:model>/<int:id>',
                 '/vtt/image/<string:model>/<int:id>/<int:width>x<int:height>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>/<string:filename>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
                 '/vtt/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',

                 '/vtt/image/<int:id>',
                 '/vtt/image/<int:id>/<string:filename>',
                 '/vtt/image/<int:id>/<int:width>x<int:height>',
                 '/vtt/image/<int:id>/<int:width>x<int:height>/<string:filename>',
                 '/vtt/image/<int:id>-<string:unique>',
                 '/vtt/image/<int:id>-<string:unique>/<string:filename>',
                 '/vtt/image/<int:id>-<string:unique>/<int:width>x<int:height>',
                 '/vtt/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'], type='http',
                auth="public")
    def vtt_get_image(self, xmlid=None, model='', id=None, field='raw',
                      filename_field='name', filename=None, mimetype=None, unique=False,
                      download=False, width=0, height=0, crop=False, access_token=None,
                      nocache=False):

        field = 'image_1024'

        odoo_model = 'ir.attachment'
        allowed_models = {
            'news': '',
            'product': 'product.template',
            'user': 'res.partner',
            'company': 'res.company'
        }

        if model not in allowed_models:
            return 'Access denied'

        odoo_model = allowed_models[model]

        return self._content_image(xmlid, odoo_model, id, field, filename_field, filename, mimetype, unique, download,
                                   width, height, crop, access_token, nocache)

    @http.route([
        '/image/<string:model>/<int:id>',
        '/image/<string:model>/<int:id>/<string:field>', ], type='http',
        auth="public")
    def vtt_source_image(self, model='ir.attachment', id=None, field='image_1024'):
        odoo_model = 'ir.attachment'
        allowed_models = {
            'news': 'vtt.zalo.news',
            'product': 'product.template',
            'user': 'res.partner',
            'company': 'res.company',
            'coupon': 'loyalty.program',
            'category': 'zalo.product.category',
            'member_card': 'vtt.loyalty.tier',
        }

        if model not in allowed_models:
            return 'Access denied'

        if model == 'news' and field == 'image_1024':
            field = 'image'
        if model == 'company' and field == 'image_1024':
            field = 'bank_qr'
        if model == 'coupon' and field == 'image_1024':
            field = 'image'
        if model == 'category' and field == 'image_1024':
            field = 'image'
        if model == 'member_card' and field == 'image_1024':
            field = 'icon'

        odoo_model = allowed_models[model]

        return self._content_image(None, odoo_model, id, field)

    # lay image
    def _content_image(self, xmlid=None, model='', id=None, field='raw',
                       filename_field='name', filename=None, mimetype=None, unique=False,
                       download=False, width=0, height=0, crop=False, access_token=None,
                       nocache=False):

        try:
            record = request.env['ir.binary'].sudo()._find_record(xmlid, model, id and int(id), access_token)
            stream = request.env['ir.binary'].sudo()._get_image_stream_from(
                record, field, filename=filename, filename_field=filename_field,
                mimetype=mimetype, width=int(width), height=int(height), crop=crop,
            )
        except UserError as exc:
            if download:
                raise request.not_found() from exc
            # Use the ratio of the requested field_name instead of "raw"
            if (int(width), int(height)) == (0, 0):
                width, height = image_guess_size_from_field_name(field)
            record = request.env.ref('web.image_placeholder').sudo()
            stream = request.env['ir.binary'].sudo()._get_image_stream_from(
                record, 'raw', width=int(width), height=int(height), crop=crop,
            )

        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        res = stream.get_response(**send_file_kwargs)
        res.headers['Content-Security-Policy'] = "default-src 'none'"
        return res

