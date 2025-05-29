# -*- coding: utf-8 -*-

import logging
from odoo import http
from datetime import datetime

# from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response

_logger = logging.getLogger(__name__)


class DocumentController(http.Controller):

    @http.route('/ev/docapi/insert_doc/', type='json', auth='public', methods=['POST'])
    def ev_insert_document(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['params']
            vals = []
            for pr in params:
                pr_vals = {
                    'name': pr.get('name'),
                    'url': pr.get('url'),
                    'description': pr.get('description'),
                    'note': pr.get('note'),
                    'ref_id': pr.get('ref_id')
                }
                if pr.get('tags') and pr.get('tags') != []:
                    tag_lst = pr.get('tags')
                    tag_ids = []
                    for t in tag_lst:
                        r = request.env['ev.document.tag'].sudo().search([('name', '=', t)], limit=1)
                        if r:
                            nr = r
                        else:
                            nr = request.env['ev.document.tag'].sudo().create({'name': t})
                        tag_ids.append(nr.id)
                    tags = [(4, nt) for nt in tag_ids]
                    pr_vals['tag_ids'] = tags
                if pr.get('category_ids') and pr.get('category_ids') != []:
                    categs = [(4, c) for c in pr.get('category_ids')]
                    pr_vals['category_ids'] = categs
                vals.append(pr_vals)


            if vals:
                rds = request.env['ev.document'].sudo().create(vals)
                args['results'] = rds
            args.update({
                'success': True,
                'message': 'Success',
            })
        return args

    @http.route('/ev/docapi/insert_docs/', type='json', auth='public', methods=['POST'])
    def ev_insert_documents(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['paramss']
            rds = []
            for pr in params:
                pr_vals = {
                    'name': pr.get('name'),
                    'url': pr.get('url'),
                    'description': pr.get('description'),
                    'note': pr.get('note'),
                    'html_content': pr.get('html_content'),
                    'ref_id': pr.get('ref_id')
                }
                if pr.get('tags') and pr.get('tags') != []:
                    tag_lst = pr.get('tags')
                    tag_ids = []
                    for t in tag_lst:
                        r = request.env['ev.document.tag'].sudo().search([('name', '=', t)], limit=1)
                        if r:
                            nr = r
                        else:
                            nr = request.env['ev.document.tag'].sudo().create({'name': t})
                        tag_ids.append(nr.id)
                    tags = [(4, nt) for nt in tag_ids]
                    pr_vals['tag_ids'] = tags
                if pr.get('category_ids') and pr.get('category_ids') != []:
                    categs = [(4, c) for c in pr.get('category_ids')]
                    pr_vals['category_ids'] = categs
                rd = request.env['ev.document'].sudo().create(pr_vals)
                if rd:
                    rds.append(rd.id)
                    if pr.get('image'):
                        img = pr.get('image')
                        imgInsert = img[img.index('base64,') + 7:]
                        att_vals = {
                            'name': 'BmAtt %s - %s' % (str(rd.id), datetime.now().strftime('%d-%m-%Y %H:%M:%S')),
                            'datas': imgInsert,
                            'res_model': 'ev.document',
                            'res_id': rd.id,
                            # 'store_fname': 'BmAtt %s - %s' % (str(rd.id), datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
                        }
                        request.env['ir.attachment'].sudo().create(att_vals)

            if rds:
                args['results'] = request.env['ev.document'].sudo().browse(rds)
            args.update({
                'success': True,
                'message': 'Success',
            })
        return args

    @http.route('/ev/docapi/list_doc/', type='json', auth='public', methods=['POST'])
    def ev_list_document(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['params']

            result = request.env['ev.document'].sudo().search_read([
                ('name', 'ilike', params.get('name'))
            ])

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/ev/docapi/list_category/', type='json', auth='public', methods=['POST'])
    def ev_list_category(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['params']

            result = request.env['ev.document.category'].sudo().search_read([
                ('name', 'ilike', params.get('name'))
            ], fields=['id', 'name', 'full_name', 'parent_id', 'ref_id', 'refparent_id'])

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/ev/docapi/list_tag/', type='json', auth='public', methods=['POST'])
    def ev_list_tag(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['params']

            result = request.env['ev.document.tag'].sudo().search_read([
                ('name', 'ilike', params.get('name'))
            ], fields=['id', 'name', 'parent_id', 'ref_id'])

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/ev/docapi/insert_categ/', type='json', auth='public', methods=['POST'])
    def ev_insert_category(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['params']
            vals = {
                'name': params.get('name'),
                'parent_id': params.get('parent_id'),
                'sequence': params.get('sequence')
            }
            result = request.env['ev.document.category'].sudo().create(vals)

            args.update({
                'success': True,
                'message': 'Success',
                'results': result
            })
        return args

    @http.route('/ev/docapi/check_url/', type='json', auth='public', methods=['POST'])
    def ev_check_url(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': False
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['params']
            result = request.env['ev.document'].sudo().search([('url', '=', params.get('url'))], limit=1)
            if result:
                args['results'] = result
        args.update({
            'success': True,
            'message': 'Success'
        })
        return args

    # @http.route('/ev/docapi/getuser/', type='json', auth='public', methods=['GET'])
    # def ev_list_user(self, name=''):
    #     # Need include db in Request Params
    #     args = {
    #         'success': True,
    #         'message': 'success',
    #         'results': []
    #     }
    #
    #     results = http.request.env['ev.document'].sudo().name_search(name)
    #     args['results'] = results
    #
    #     print(args)
    #     return args