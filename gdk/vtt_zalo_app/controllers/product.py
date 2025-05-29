# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class ProductAPI(http.Controller):
     # Product category
    @http.route('/api/product_category', type='json', auth="public", methods=['POST'])
    def product_category_list(self):
        model = 'zalo.product.category'
        domain = [
            # ['show_on_zalo', '=', True]
        ]
        limit = 10
        offset = 0
        result = []

        items = request.env[model].sudo().search(domain=domain, order='sequence ASC')

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'sequence': item.sequence,
                'image': '/image/category/' + str(item.id),
            }
            result.append(obj)

        return result

    # List product
    @http.route([
        '/api/product/page/<int:page>',
        '/api/product/page/<int:page>-<int:categ_id>'
    ]
        , type='json', auth="public", methods=['POST'])
    def product_list(self, page=1, categ_id=-1):
        model = 'product.template'

        params = request.httprequest.json
        filter_product_name = ''
        if params:
            filter_product_name = params.get('filter_by_name', '')

        domain = [
            '&',
            ['sale_ok', '=', True],
            ['zalo_categ_ids', '!=', False]
        ]

        if categ_id > 0:
            domain = [
                '&',
                ['sale_ok', '=', True],
                ['zalo_categ_ids', 'in', [categ_id]]
            ]

        if filter_product_name != '':
            if categ_id > 0:
                domain = [
                    '&',
                    ['sale_ok', '=', True],
                    '&',
                    ['zalo_categ_ids', 'in', [categ_id]],
                    ['name', 'ilike', filter_product_name],
                ]
            else:
                domain = [
                    '&',
                    ['sale_ok', '=', True],
                    '&',
                    ['zalo_categ_ids', '!=', False],
                    ['name', 'ilike', filter_product_name],
                ]

        limit = 10
        offset = 0 if page <= 1 else (page - 1) * limit
        result = []

        # fields = ['name', 'list_price', 'categ_id', 'description_sale']
        items = request.env[model].sudo().search(domain=domain, limit=limit, offset=offset)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'list_price': item.list_price,
                'description': '' if item.description_sale == False else item.description_sale,
                'image': '/image/product/' + str(item.id),
                'categ_id': categ_id
            }
            result.append(obj)

        return result

    # List product
    @http.route('/api/product/best_seller', type='json', auth="public", methods=['POST'])
    def product_best_seller(self):
        model = 'product.template'

        domain = [
            '&',
            ['sale_ok', '=', True],
            ['zalo_categ_ids', '!=', False]
        ]

        limit = 5
        offset = 0
        result = []

        items = request.env[model].sudo().search(domain=domain, limit=limit, offset=offset)

        for item in items:
            obj = {
                'id': item.id,
                'name': item.name,
                'list_price': item.list_price,
                'description': '' if item.description_sale == False else item.description_sale,
                'image': '/image/product/' + str(item.id),
                'categ_id': item.categ_id.id
            }
            result.append(obj)

        return result

    # Get Product
    @http.route('/api/product/<int:id>', type='json', auth="public", methods=['POST'])
    def product_get(self, id):
        model = 'product.template'

        if id <= 0:
            return None

        count = request.env[model].sudo().search_count(domain=[['id', '=', id]])
        if count <= 0:
            return None

        obj = request.env[model].sudo().browse(id)
        if obj and obj.id > 0:
            # result = obj.read(fields=fields)[0]
            # r = obj.read()[0]
            # categ_obj = request.env['product.category'].sudo().browse(obj.categ_id.id).read()[0]
            result = {
                'id': obj.id,
                'name': obj.name,
                'description': obj.description_sale,
                'list_price': obj.list_price,
                'categ_id': obj.categ_id.id,
                'image': '/image/product/' + str(obj.id),
                # 'image': obj.image_512

            }

            return result

        return None




