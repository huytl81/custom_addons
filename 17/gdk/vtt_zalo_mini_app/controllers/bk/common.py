# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request



class CommonAPI(http.Controller):
    # Get Company info
    @http.route('/api/company/info', type='json', auth="public", methods=['POST'])
    def company_info(self):
        model = 'res.company'

        com = request.env[model].sudo().search(domain=[
            ['id', '=', 1]
        ], limit=1)

        if com:
            return {
                'company_name': com.name,
                'phone': '' if com.phone == False else com.phone,
                'address': '' if com.street == False else com.street,
                'app_qr': '/image/company/1/zalo_app_qr',
                'bank_qr': '/image/company/1/bank_qr',
                'link': '' if com.zalo_app_link == False else com.zalo_app_link,
                'logo_url': '/image/company/1/image_1024/logo'
            }
        return {
            'success': False,
            'message': 'Không có thông tin công ty'
        }


