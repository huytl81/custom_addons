# -*- coding: utf-8 -*-

import functools

from odoo.http import request

def validate_token(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        # for local test - always true
        # *** phai bo sung them check local de tranh tinh trang dua nham len server
        # request.update_env(user=6)
        # return func(self, *args, **kwargs)


        access_token = request.httprequest.headers.get("X-Openerp-Session-Id")
        if not access_token:
            return {
                'success': False,
                'message': 'missing access token in request header'
            }
        access_token = 'access_token_' + access_token
        access_token_data = request.env["vtt.api.access.token"].sudo().search([("token", "=", access_token)], order="id DESC", limit=1)

        if access_token_data.find_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return {
                'success': False,
                'message': 'access token invalid or expired'
            }
        request.update_env(user=access_token_data.user_id)
        u = request.env.user
        # request.session.uid = access_token_data.user_id.id
        # request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)

    return wrap