# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import json
import datetime
import base64


class EvAPI(http.Controller):
    # ******************************************** ----- BASE ----- ***************************************************
    # search
    def _base_search(self, request):
        print('base search')
        print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params.get('model')
            domain = params.get('domain', [])
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])
            limit = params.get('limit', None)
            offset = params.get('offset', 0)
            order = params.get('order', None)
            search_count = params.get('search_count', False)

            count = request.env[model].search_count(domain)
            if search_count == False:
                result = request.env[model].with_context(lang='vi_VN').search_read(domain=domain, fields=fields, limit=limit, offset=offset, order=order)
                # remove all field with false value following ignore_false_fields parameter
                if ignore_false_fields:
                    result_str = json.dumps(result, default=str)
                    for field in ignore_false_fields:
                        r = ', "' + field + '": false'
                        result_str = result_str.replace(r, '')
                    result = json.loads(result_str)
                args['result']['items'] = result
            else:
                args['result']['total_items'] = count

            args['success'] = True
            args['message'] = 'success'
            print(args)
        return args

    # Create
    def _base_create(self, request):
        args = {
            'success': False,
            'message': 'Create failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            model = params.get('model')
            input = params['input']

            if input:
                obj = request.env[model].create(input)
                record = obj.read()
                if record and record[0]['id'] > 0:
                    args.update({
                        'success': True,
                        'message': 'Success',
                        'result': {
                            'id': record[0]['id']
                        }
                    })
            print(args)
        return args

    # Update
    def _base_edit(self, request):
        args = {
            'success': False,
            'message': 'Edit failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params.get('model')
            input = params.get('input')
            id = input.get('id', -1)
            if input and id > 0:
                obj = request.env[model].browse(id)

                if input and obj:
                    record = obj.write(input)
                    args.update({
                        'success': True,
                        'message': 'Success',
                        'result': {
                            'id': id
                        }
                    })
        return args

    # ******************************************** ----- END BASE ----- ***********************************************

    # ******************************************** ----- API ----- ****************************************************
    # -------- Authenticate API ------------
    @http.route('/vtt/api/authenticate', type='json', auth="none", methods=['POST'])
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        # abc = request.env['ir.http'].session_info()
        # bbb = ''
        return request.env['ir.http'].session_info()

    @http.route('/vtt/session/logout', type='http', auth="none")
    def logout(self, redirect='/web'):
        request.session.logout(keep_db=True)
        return werkzeug.utils.redirect(redirect, 303)
    # -------------------------------------

    # search base
    @http.route('/vtt/api/vttbase/search', type='json', auth='user', methods=['POST'])
    def base_search(self, request):
        return self._base_search(request)

    # get base
    @http.route('/vtt/api/vttbase/get', type='json', auth='user', methods=['POST'])
    def base_get(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params.get('model')
            id = params.get('id')
            fields = params.get('fields', [])
            ignore_false_fields = params.get('ignore_false_fields', [])

            obj = request.env[model].with_context(lang='vi_VN').browse(id)

            if obj:
                result = obj.read(fields)
                # remove all field with false value following ignore_false_fields parameter
                if ignore_false_fields:
                    result_str = json.dumps(result)
                    for field in ignore_false_fields:
                        r = ', "' + field + '": false'
                        result_str = result_str.replace(r, '')
                    result = json.loads(result_str)

                args = {
                    'success': True,
                    'message': 'Success',
                    'result': {
                        'item': result[0]
                    }
                }
        return args

    # base save (create | update)
    @http.route('/vtt/api/vttbase/save', type='json', auth='user', methods=['POST'])
    def base_save(self, request):
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            print(params)
            input = params.get('input')
            id = input.get('id', -1)
            if id and id > 0:
                return self._base_edit(request)
            return self._base_create(request)

    # user remove device id
    @http.route('/vtt/api/user/registry_device', type='json', auth='user', methods=['POST'])
    def user_registry_device(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'result': {}
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            token = params.get('fcm_token')
            uid = params.get('id')
            result = request.env['vtt.user.app.device'].search([['fcm_token', '=', token]])
            if not result:
                request.env['vtt.user.app.device'].create({
                    'user_id': uid,
                    'fcm_token': token
                })
                args = {
                    'success': True,
                    'message': 'Success'
                }
        return args

    # user remove device id
    @http.route('/vtt/api/user/remove_device', type='json', auth='user', methods=['POST'])
    def user_remove_device(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            print(params)
            token = params.get('fcm_token')
            if token:
                result = request.env['vtt.user.app.device'].search([['fcm_token', '=', token]])
                if result:
                    result.unlink()
                    args = {
                        'success': True,
                        'message': 'Success'
                    }
        return args

    @http.route('/vtt/api/mailactivity/doneactivity', type='json', auth='user', methods=['POST'])
    def mail_actvity_done(self, request):
        print('test base')
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            print(params)
            message = params.get('message', '')  # ...
            input = params['input']
            if input:
                id = input.get('id', -1)

                activity = request.env['mail.activity'].browse(id)
                if message != '':
                    result = activity.action_feedback(feedback=message)
                else:
                    activity.action_done()
                args['success'] = True
                args['message'] = 'success'

        return args

    @http.route('/vtt/api/testbase/doneactivity', type='json', auth='user', methods=['POST'])
    def test_doneactivity(self, request):
        print('test base')
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            message = params.get('message', '') #...
            id = params.get('id', -1)


            activity = request.env['mail.activity'].browse(id)
            if message != '':
                result = activity.action_feedback(feedback=message)
            else:
                activity.action_done()
        return ''

    @http.route('/vtt/api/testbase/uploadattachment', type='json', auth='user', methods=['POST'])
    def test_upload_attachment(self, request):
        print('test base')
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            base64_datas = params['datas']  # ...
            datas = base64_datas[base64_datas.index('base64,') + 7:]

            Model = request.env['ir.attachment']
            attachment = Model.create({
                'name': 'blomm.jpg',
                'datas': datas,
                    'res_model': 'project.task',
                    'res_id': 20
            })


        return ''











    #  OLD API - se ko su dung nua
    @http.route('/vtt/api/testbase/', type='json', auth='user', methods=['POST'])
    def test_base(self, request):
        print('test base')
        return self._base_search(request)

    @http.route('/vtt/api/demolist/', type='json', auth='user')
    def get_demo_list(self, **rec):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            print('rec:', rec)
            if rec:
                model = rec['model']
                result = request.env[model].sudo().search_read([], limit=15)
                args = {
                    'success': True,
                    'message': 'Success',
                    'results': result
                }
        return args

    @http.route('/vtt/api/demolistpost/', type='json', auth='user', methods=['POST'])
    def get_demo_listpost(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params['model']

            result = request.env[model].sudo().search_read([], fields=['id', 'name', 'email', 'phone', 'mobile', 'company_id', 'parent_id', 'user_ids'], limit=15)
            args = {
                'success': True,
                'message': 'Success',
                'results': result
                }
        return args

    @http.route('/vtt/api/demolistpostnoauthen/', type='json', auth='public', methods=['POST'])
    def get_demo_listpost_noauthen(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            model = params['model']

            result = request.env[model].sudo().search_read([], fields=['id', 'name', 'email', 'phone', 'mobile',
                                                                       'company_id', 'parent_id', 'user_ids'], limit=15)
            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }
        return args

    @http.route('/vtt/api/posturl/', type='json', auth='public', methods=['POST'])
    def posturl(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            print('param')
            print(params)
            # model = params['model'] or ''

            args = {
                'success': True,
                'message': 'Success',
                'results': params['url']
            }
        print('accc')
        print(args)
        return args

    @http.route('/vtt/api/getdemolistpostnoauthen/', auth='public')
    def get_demo_listpost_getnoauthenn(self):
        return 'ba ma no'

    @http.route('/vtt/api/VttTest/GetUsers', type='json', auth='user', methods=['POST'])
    def get_users(self, request):
        print(request.jsonrequest)

        return {
            'name': 'ba ma no',
            'result': {
                'acb': 123,
                'ccc': 'acccccccc'
            }

        }

    @http.route('/vtt/api/vtttest/gettasks', type='json', auth='user', methods=['POST'])
    def get_tasks(self, request):
        print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'result': {

            }
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['project.task'].search_read([], fields=['id', 'name'])

            args = {
                'success': True,
                'message': 'Success',
                'result': {
                    'items': result
                }
            }

        return args

    @http.route('/vtt/api/VttTest/GetProjects', type='json', auth='user', methods=['POST'])
    def get_projects(self, request):
        print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['project.project'].search_read([], fields=['id', 'name', 'user_id', 'task_count'], limit=15)

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/ProjectTask/GetPicture', type='json', auth='user', methods=['POST'])
    def project_task_get_projects(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['res.partner'].search_read([], fields=['id', 'name', 'image_1920'], limit=15)

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

            print(result)

        return args

    @http.route('/vtt/api/ProjectTask/GetProjects', type='json', auth='user', methods=['POST'])
    def project_task_get_projects(self, request):
        print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        print(http.request.env['ir.config_parameter'].get_param('web.base.url'))

        print(http.request.httprequest)

        print(http.request.httprequest.full_path)

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['project.project'].search_read([], fields=['id', 'name', 'user_id', 'task_count', 'partner_id'], limit=15)
            if result:
                for r in result:
                    if not r.get('user_id'):
                        r['user_id'] = []
                    if not r.get('partner_id'):
                        r['partner_id'] = []

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/ProjectTask/GetProject', type='json', auth='user', methods=['POST'])
    def project_task_get_project_by_id(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        print('------------')

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            id = params.get('id')

            result = request.env['project.project'].search_read([['id', '=', id]],
                                                                fields=['id', 'name', 'description', 'user_id',
                                                                        'task_count',
                                                                        'partner_id', 'partner_phone', 'partner_email',
                                                                        'allowed_portal_user_ids'], limit=1)
            if result:
                for r in result:
                    if not r.get('user_id'):
                        r['user_id'] = []
                    if not r.get('partner_id'):
                        r['partner_id'] = []

            print('daaaaaaaaaaaaaa')
            print(result)

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/User/GetUsers', type='json', auth='user', methods=['POST'])
    def user_get_users(self, request):
        print(request.jsonrequest)
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['res.users'].search_read([], fields=['id', 'name'], limit=15)
            print(result)
            if result:
                for r in result:
                    print (str(r['id']) + 'abc')
                    # r['avatar'] = base_url + '/web/image/res.users/' + str(r['id']) + '/image_128'
                    r['avatar'] = 'https://thuthuat.taimienphi.vn/cf/Images/ci/2019/1/24/demo-nghia-la-gi.jpg'
                    # r['avatar'] = 'http://192.168.1.7:8069/web/image/res.users/2/image_128'
            print(result)
            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/Partner/GetPartners', type='json', auth='user', methods=['POST'])
    def partner_get_partner(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['res.partner'].search_read([], fields=['id', 'name', 'display_name'])
            if result:
                for r in result:
                    r['avatar'] = base_url + '/web/image/res.users/' + str(r['id']) + '/image_128'
            print(result)
            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/ProjectTask/CreateProject/', type='json', methods=['POST'])
    def create_proj(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            print(params)
            params['privacy_visibility']='employees'

            proj_vals = {
                'name': params.get('name', 'New'),
                'user_id': params.get('user_id'),
                'partner_id': params.get('partner_id'),
                'privacy_visibility': params.get('privacy_visibility', 'employees')
            }
            if proj_vals:
                proj = request.env['project.project'].create(proj_vals)
                args['results'] = proj.read()
            args.update({
                'success': True,
                'message': 'Success'
            })
            print(args)
        return args

    @http.route('/vtt/api/ProjectTask/EditProject/', type='json', methods=['POST'])
    def edit_proj(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            id = params.get('id', [])
            if id:
                projs = request.env['project.project'].browse(id)

                proj_vals = {
                    'name': params.get('name', 'New'),
                    'user_id': params.get('user_id'),
                    'partner_id': params.get('partner_id'),
                    'privacy_visibility': params.get('privacy_visibility', 'employees')
                }
                proj_vals['privacy_visibility'] = 'employees'
                if proj_vals and projs:
                    results = projs.write(proj_vals)
                    args['results'] = results
            args.update({
                'success': True,
                'message': 'Success'
            })
        return args

    @http.route('/vtt/api/ProjectTask/UnlinkProject/', type='json', methods=['POST'])
    def unlink_proj(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            ids = params.get('ids', [])
            if ids:
                projs = request.env['project.project'].browse(ids)
                if projs:
                    results = projs.unlink()
                    args['results'] = results
            args.update({
                'success': True,
                'message': 'Success'
            })
        return args


    @http.route('/vtt/api/ProjectTask/GetTasks', type='json', auth='user', methods=['POST'])
    def project_task_get_tasks(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            print (datetime.datetime.now())
            result = request.env['project.task'].search_read([], fields=['id', 'name', 'user_id', 'project_id',
                                                                         'partner_id', 'stage_id',
                                                                         'tag_ids', 'date_deadline'])
            print(datetime.datetime.now())
            rree = request.env['project.task'].search_count([])
            print(datetime.datetime.now())

            if result:
                for r in result:
                    # r['avatar'] = 'https://pickaface.net/gallery/avatar/unr_sample_170130_2257_9qgawp.png'
                    if not r.get('user_id'):
                        r['user_id'] = []
                    else:
                        # r['avatar'] = 'https://pickaface.net/gallery/avatar/unr_sample_170130_2257_9qgawp.png'
                        r['avatar'] = 'http://192.168.1.7:8069' + '/web/image?model=res.users&id=' + str(
                            r['user_id'][0]) + '&field=image_128'
                    if not r.get('partner_id'):
                        r['partner_id'] = []
                    if not r.get('project_id'):
                        r['project_id'] = []
                    if not r.get('stage_id'):
                        r['stage_id'] = []
                    if not r.get('date_deadline'):
                        r['date_deadline'] = ''

            print(datetime.datetime.now())
            print ('count: ' + str(rree))
            print (result)

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/ProjectTask/GetTask', type='json', auth='user', methods=['POST'])
    def project_task_get_task_by_id(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            id = params.get('id')

            result = request.env['project.task'].search_read([['id', '=', id]],
                                                                fields=['id', 'name', 'description', 'user_id',
                                                                        'partner_id'], limit=1)
            if result:
                for r in result:
                    if not r.get('user_id'):
                        r['user_id'] = []
                    if not r.get('partner_id'):
                        r['partner_id'] = []

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/ProjectTask/CreateTask/', type='json', methods=['POST'])
    def create_task(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            print(params)

            proj_vals = {
                'name': params.get('name', 'New'),
                'user_id': params.get('user_id'),
                'partner_id': params.get('partner_id'),
            }
            if proj_vals:
                proj = request.env['project.task'].create(proj_vals)
                args['results'] = proj.read()
            args.update({
                'success': True,
                'message': 'Success'
            })
            print(args)
        return args

    @http.route('/vtt/api/ProjectTask/EditTask/', type='json', methods=['POST'])
    def edit_task(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            id = params.get('id', [])
            if id:
                projs = request.env['project.task'].browse(id)

                proj_vals = {
                    'name': params.get('name', 'New'),
                    'user_id': params.get('user_id'),
                    'partner_id': params.get('partner_id'),
                }
                if proj_vals and projs:
                    results = projs.write(proj_vals)
                    args['results'] = results
            args.update({
                'success': True,
                'message': 'Success'
            })
        return args

    @http.route('/vtt/api/ProjectTask/UnlinkTask/', type='json', methods=['POST'])
    def unlink_task(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']
            ids = params.get('ids', [])
            if ids:
                projs = request.env['project.task'].browse(ids)
                if projs:
                    results = projs.unlink()
                    args['results'] = results
            args.update({
                'success': True,
                'message': 'Success'
            })
        return args

    @http.route('/vtt/api/ProjectTask/GetTags', type='json', auth='user', methods=['POST'])
    def project_task_get_tags(self, request):
        args = {
            'success': False,
            'message': 'Failed',
            'results': []
        }

        base_url = http.request.env['ir.config_parameter'].get_param('web.base.url')

        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            result = request.env['project.tags'].search_read([])

            print(result)

            args = {
                'success': True,
                'message': 'Success',
                'results': result
            }

        return args

    @http.route('/vtt/api/projecttask/getactivity', type='json', auth='user', methods=['POST'])
    def test_get_activity(self, request):
        if request.jsonrequest:
            data = request.jsonrequest
            params = data['parameters']

            model = params['model']
        result = request.env[model].search_read([])

        print(result)

        return result
    # ******************************************** ----- END API ----- ************************************************