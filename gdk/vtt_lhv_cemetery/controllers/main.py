# -*- coding: utf-8 -*-

import json

from odoo import http, _
from odoo.http import request


class LHVController(http.Controller):

    @http.route('/vtt/api/event_registration_status', type='json', auth='user', methods=['POST'])
    def search_event_registration(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            # model = params.get('model')
            user_id = params.get('user_id')
            # fields = params.get('fields', [])
            # ignore_false_fields = params.get('ignore_false_fields', [])
            # model = params.get('model')
            domain = params.get('domain', [])
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])
            limit = params.get('limit', None)
            offset = params.get('offset', 0)
            order = params.get('order', None)

            user = request.env['res.users'].browse(user_id)
            partner_id = user.partner_id
            events = request.env['event.event'].with_context(lang='vi_VN').sudo().search_read(domain=domain,
                                                                                              fields=fields,
                                                                                              limit=limit,
                                                                                              offset=offset,
                                                                                              order=order)
            event_registrations = request.env['event.registration'].sudo().search([
                ('partner_id', '=', partner_id.id),
                ('state', 'in', ['open', 'done'])
            ])
            event_registration_ids = event_registrations.event_id.ids

            for e in events:
                if e['id'] in event_registration_ids:
                    e['registration_status'] = True
                else:
                    e['registration_status'] = False

            if events:
                result = events
                args['result']['items'] = result
                args['success'] = True
                args['message'] = 'success'
        return args