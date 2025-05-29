# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import http
from odoo.http import request


class NewsAPI(http.Controller):
    @http.route('/api/news/page/<int:page>', type='json', auth="public", methods=['POST'])
    def news_list(self, page=1):
        model = 'vtt.zalo.news'
        domain = []
        limit = 10
        offset = 0 if page <= 1 else (page - 1) * limit
        result = []

        params = request.httprequest.json
        filter_by_name = ''
        if params:
            filter_by_name = params.get('filter_by_name', '')
            is_hot_news = params.get('is_hot_news', False)

        if filter_by_name != '':
            if is_hot_news:
                domain = [
                    '&',
                    ['title', 'ilike', filter_by_name],
                    ['is_hot_news', '=', True],
                ]
            else:
                domain = [
                    ['title', 'ilike', filter_by_name]
                ]
        else:
            if is_hot_news:
                domain = [
                    ['is_hot_news', '=', True]
                ]

        items = request.env[model].sudo().search(domain=domain, limit=limit,
                                                 offset=offset, order='publish_date desc')

        for item in items:
            p_date = '' if item.publish_date == False else item.publish_date
            if p_date != '':
                p_date = p_date + timedelta(hours=7)
            obj = {
                'id': item.id,
                'name': '' if item.title == False else item.title,
                'description': '' if item.description == False else item.description,
                'public_link': '' if item.public_link == False else item.public_link,
                'publish_date': p_date ,
                'is_hot_news': item.is_hot_news,
                'author': '' if item.author == False else item.author,
                'image': '/image/news/' + str(item.id),
            }
            result.append(obj)

        return result

    #
    @http.route('/api/news/<int:id>', type='json', auth="public", methods=['POST'])
    def news_get(self, id, **kwargs):
        model = 'vtt.zalo.news'

        if id <= 0:
            return None
        count = request.env[model].sudo().search_count(domain=[['id', '=', id]])
        if count <= 0:
            return None

        obj = request.env[model].sudo().browse(id)
        if obj and obj.id > 0:
            p_date = '' if obj.publish_date == False else obj.publish_date
            if p_date != '':
                p_date = p_date + timedelta(hours=7)
            result = {
                'id': obj.id,
                'name': '' if obj.title == False else obj.title,
                'description': '' if obj.description == False else obj.description,
                'public_link': '' if obj.public_link == False else obj.public_link,
                'publish_date': p_date,
                'is_hot_news': obj.is_hot_news,
                'author': '' if obj.author == False else obj.author,
                'image': '/image/news/' + str(obj.id),
                # 'image': obj.image_512

            }
            return result

        return None
