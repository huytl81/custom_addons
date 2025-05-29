# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models
import requests
from .googledrive_exception import GoogleDriveRestApiError,GoogleDriveResyncError
import logging
_logger = logging.getLogger(__name__)

client = None
headers = {'User-agent': 'Googledrive: Python Googledrive Library'}


class CallGoogleDriveApi(models.TransientModel):
    _name = 'call.googledrive.api'
    _description = 'Class Use To Call Googledrive Api Methods'

    @api.model
    def _parse_error(self, content):
        """
        Take the content as string and extracts the Googledrive error
        @param content: Content of the response of google drive
        @return (Googledrive Error Code, Google Drive Error Message)
        """
        message = ''
        error = content.get('error')
        code = False
        if type(error) == dict:
            if error.get('errors',False):
                message=error.get('errors')[0].get('message')
            else:
                message = error.get('message')
            code = error.get('code')
        if 'error_description' in content:
            message = content['error_description']
        if not code:
            code = content.get('error', '')
        return code, message

    @api.model
    def _check_status_code(self, response, method, url):
        """
        Take the status code and throw an exception if the server didn't return 200 or 201 or 302 or 204 code
        @param response: response return by the client request
        @param method: request method
        @param url: request url
        @return: True or raise an exception GoogleDriveRestApiError
        """
        
        message_by_code = {
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            405: 'Method Not Allowed',
            406: 'Not Acceptable',
            409: 'Conflict',
            410: 'Gone',
            411: 'Length Required',
            412: 'Precondition Failed',
            413: 'Request Entity Too Large',
            415: 'Unsupported Media Type',
            416: 'Requested Range Not Satisfiable',
            422: 'Unprocessable Entity',
            429: 'Too Many Requests',
            500: 'Internal Server Error',
            501: 'Not Implemented',
            503: 'Service Unavailable',
            507: 'Insufficient Storage',
            509: 'Bandwidth Limit Exceeded',
        }
        status_code = response.status_code
        content = response.content
        
        if status_code in (200, 201, 302, 204):
            if ('alt=media' in url and method.lower() == 'get'):# (method.lower() == 'get' or method.lower() == 'delete'):
                return content
            else:
                return response.json()
        else:
            content = response.json()
            so_error_code, so_error_message = self._parse_error(content)
            if so_error_code == 401 and so_error_message == 'Invalid Credentials' :
                raise GoogleDriveResyncError(
                    'Resync Required', 401,
                    'The requested resource is no longer available at the server', 401)
            if status_code in message_by_code:
                raise GoogleDriveRestApiError(message_by_code[status_code],status_code, so_error_message, so_error_code)
        return content

    @api.model
    def call_drive_api(self, url, method, data=None, headers={},files=None):
        """
        Execute a request on the Googledrive Rest

        @param url: full url to call
        @param method: GET, POST, PUT,PATCH,DELETE
        @param data: for PUT (edit) and POST (add) only the data sent to Googledrive
        @return: dictionary content and binary data content of the response
        """
        global client
        context = self._context.copy() or {}
        client = requests.Session()
        request_headers = headers.copy()
        request_headers.update(headers)
        resp = client.request(method, url, data=data, headers=request_headers,files=files)
        
        try:
            content = self._check_status_code(resp,method,url)
            return content             ##content is resp.json()
        except GoogleDriveResyncError as e:
            if context.get('call_again', True):
                context['call_again'] = False
                instance_id = context.get('instance_id', False)
                if instance_id:
                    connection = self.env['cloud.odoo.connection']._create_googledrive_connection(
                        instance_id, refresh_token=True)
                    access_token = connection.get('access_token', False)
                    if access_token:
                        headers.update(
                            {'Authorization': 'Bearer {}'.format(access_token)})
                return self.with_context(context).call_drive_api(url, method, data, headers)
            raise GoogleDriveRestApiError(
                'Required Test Connection', 410,
                'The requested refresh token is no longer available at the server so test connection again', 410)
