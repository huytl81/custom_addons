# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import base64
from datetime import datetime


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def RepresentsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class EduAdmissionForm(http.Controller):

    @http.route(['/edu/admission/profile_apply'], type='http', auth='public', website=True)
    def edu_admission_profile_apply(self, **kwargs):
        # type_rec = [{'name': _('Đã có bằng tốt nghiệp'), 'value': 1}, {'name': _('Chưa có bằng tốt nghiệp'), 'value': 2}]
        category_rec = request.env['op.category'].sudo().search([])
        return request.render('vtt_edu_admission_form.vtt_tmp_admission_profile_apply', {
            # 'type_rec': type_rec,
            'category_rec': category_rec,
        })

    @http.route(['/edu/admission/form'], type='http', auth='public', website=True, csrf=False)
    def edu_admission_form(self, **kwargs):
        data = kwargs
        category_id = data.get('category_id')
        institute_cert = data.get('type_rec')
        course_rec = request.env['op.course'].sudo().search([('category_id', '=', int(category_id))])
        category_rec = request.env['op.category'].sudo().search([('id', '=', int(category_id))])
        state_rec = request.env['res.country.state'].sudo().search([('country_id.code', '=', 'VN')])
        return request.render('vtt_edu_admission_form.vtt_tmp_admission_form', {
            'course_rec': course_rec,
            'state_rec': state_rec,
            'category_rec': category_rec,
            'institute_cert': institute_cert
        })

    @http.route(['/edu/admission/form/submit/<string:res_model>'], type='http', auth='public', website=True, csrf=False)
    def edu_admission_form_submit(self, res_model, **kwargs):
        data = kwargs
        COUNTRY_STATE = request.env['res.country.state'].sudo()
        COURSE = request.env['op.course'].sudo()
        IR_ATTACHMENT = request.env['ir.attachment'].sudo()
        CATEGORY = request.env['op.category'].sudo()
        STUDENT = request.env['op.student'].sudo()
        BATCH = request.env['op.batch'].sudo()
        # STUDENT_COURSE = request.env['op.student.course'].sudo()

        student_datas = {}
        # try:
        #     dob = self._xmlrpc(service)
        # except Exception as error:
        #     response = wsgi_server.xmlrpc_handle_exception_string(error)

        institute_cert_lst = {'1': 'has_cert', '2': 'no_cert'}

        vals = {
            # 'first_name': data.get('first_name', ''),
            # 'middle_name': data.get('middle_name', ''),
            # 'last_name': data.get('last_name', ''),
            'gender': data.get('gender'),
            'birth_date': datetime.strptime(data.get('birth_date'), '%d/%m/%Y'),
            'mobile': data.get('mobile', ''),
            'email': data.get('email', ''),
            'identify_id': data.get('identify_id', ''),
            'prev_institute_id': data.get('prev_institute_id', ''),
            'prev_result': data.get('prev_result', ''),
            'street': data.get('street', ''),
            'institute_cert': institute_cert_lst.get(data.get('institute_cert')),
            # 'course': data.get('course_id'),
            # 'state_id': data.get('state_id'),
        }

        course_id = COURSE.browse(int(data.get('course_id')) if data.get('course_id') else False)
        if course_id:
            batch_id = BATCH.search([('course_id', '=', course_id.id)], order='code desc', limit=1)
            if batch_id:
                # fees_term_id = course_id.fees_term_id
                # fees = fees_term_id.product_id.lst_price
                if data.get('name'):
                    name = data.get('name')
                    vals.update({'name': name})
                else:
                    name = ' '.join([
                        data.get('last_name', ''),
                        data.get('middle_name', ''),
                        data.get('first_name', '')]).replace('  ', ' ').strip()
                    vals.update({
                        'first_name': data.get('first_name', ''),
                        'middle_name': data.get('middle_name', ''),
                        'last_name': data.get('last_name', ''),
                        'name': name,
                    })
                country_state_id = COUNTRY_STATE.browse(int(data.get('state_id')) if data.get('state_id') else False)
                category_id = CATEGORY.browse(int(data.get('category_id')) if data.get('category_id') else False)
                vals.update({
                    # 'batch_id': batch_id.id,
                    # 'course_id': course_id.id,
                    # 'fees_term_id': fees_term_id.id,
                    # 'fees': fees,
                    'batch_code': batch_id.code,
                    'state_id': country_state_id.id,
                    'category_id': category_id.id,
                })

                if data.get('profile_image_file'):
                    # profile_image_name = data.get('profile_image_file[1][0]').filename
                    profile_image_datas = base64.b64encode(data.get('profile_image_file').read())
                    vals.update({
                        'image_1920': profile_image_datas
                    })

                if data.get('institute_cert_img_file'):
                    # profile_image_name = data.get('profile_image_file[1][0]').filename
                    institute_cert_image_datas = base64.b64encode(data.get('institute_cert_img_file').read())
                    vals.update({
                        'institute_cert_img': institute_cert_image_datas
                    })

                check_email = STUDENT.check_email(vals['mobile'])
                if check_email:
                    res_student = STUDENT.create(vals)
                    student_datas['student_id'] = res_student

                    if res_student:
                        res_student.create_student_user()
                        for c in res_student.course_detail_ids:
                            if vals['institute_cert'] == 'no_cert':
                                c.total_reminder_admission_paper()
                            # if RepresentsFloat(data.get('prev_result')):
                            #     if float(data.get('prev_result')) >= 5.0:
                            #         c.total_reminder_admission_paper()
                            c.get_fees()
                        data_attachments = [d for d in data if d.endswith('_fileattach')]
                        if data_attachments:
                            for d in data_attachments:
                                attachment_vals = {
                                    'name': data.get(d).filename,
                                    'type': 'binary',
                                    'datas': base64.b64encode(data.get(d).read()),
                                    'res_model': 'op.student',
                                    'res_id': res_student.id
                                }
                                IR_ATTACHMENT.create(attachment_vals)
                else:
                    student_datas['message'] = _('Your Email already exist!')
                    student_datas['student_id'] = 0

        return request.render('vtt_edu_admission_form.vtt_tmp_admission_form_success', student_datas)

    @http.route(['/edu/admission/report/<idcode>'], type='http', auth='public', website=True, csrf=False)
    def get_report_by_code(self, idcode):
        path = '/#'
        idcode += '='
        try:
            idcode_str = base64.urlsafe_b64decode(idcode).decode().replace('vtt_edu', '')
        except Exception:
            return request.redirect(path)
        if idcode_str:
            if RepresentsInt(idcode_str):
                check_exist = request.env['op.student.course'].browse(int(idcode_str))
                if check_exist:
                    pdf = request.env.ref('vtt_edu_admission_form.action_student_course_report').sudo()._render_qweb_pdf([int(idcode_str)])[0]
                    pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
                    return request.make_response(pdf, headers=pdfhttpheaders)
                else:
                    return request.redirect(path)
            else:
                return request.redirect(path)

        else:
            return request.redirect(path)