# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class EduAdmission(models.Model):
    _inherit = 'op.admission'

    identify_id = fields.Char('Identify No.')
    # school_avg_score = fields.Float('School Avg. Score', default=0.00)

    category_id = fields.Many2one('op.category', 'Category')

    phone = fields.Char(states={'submit': [('required', False)]})
    mobile = fields.Char(states={'submit': [('required', False)]})

    institute_cert = fields.Selection([
        ('has_cert', 'Has Certify'),
        ('no_cert', 'Not Certify Yet')
    ], 'Institute Cert', default='has_cert')

    def enroll_student(self):
        for record in self:
            if record.register_id.max_count:
                total_admission = self.env['op.admission'].search_count([
                    ('register_id', '=', record.register_id.id),
                    ('state', '=', 'done')
                ])
                if not total_admission < record.register_id.max_count:
                    msg = 'Max Admission In Admission Register :- (%s)' % (record.register_id.max_count)
                    raise ValidationError(_(msg))
            if not record.student_id:
                vals = record.get_student_vals()
                record.partner_id = vals.get('partner_id')
                record.student_id = student_id = self.env['op.student'].create(vals).id
                # Apply Admission Attachment to Student Profile
                attachments = self.env['ir.attachment'].search([
                    ('res_model', '=', 'op.admission'),
                    ('res_id', '=', record.id)
                ])
                if attachments:
                    attachments.write({
                        'res_model': 'op.student',
                        'res_id': student_id,
                    })

            else:
                student_id = record.student_id.id
                record.student_id.write({
                    'course_detail_ids': [[0, False, {
                        'course_id': record.course_id and record.course_id.id or False,
                        'batch_id': record.batch_id and record.batch_id.id or False,
                        'fees_term_id': record.fees_term_id.id,
                        'fees_start_date': record.fees_start_date,
                        'fees': record.fees,
                    }]],
                })

            # Remove for new fees define
            # if record.fees_term_id.fees_terms in ['fixed_days', 'fixed_date']:
            #     val = []
            #     product_id = record.register_id.product_id.id
            #     for line in record.fees_term_id.line_ids:
            #         no_days = line.due_days
            #         per_amount = line.value
            #         amount = (per_amount * record.fees) / 100
            #         dict_val = {
            #             'fees_line_id': line.id,
            #             'amount': amount,
            #             'fees_factor': per_amount,
            #             'product_id': product_id,
            #             'state': 'draft',
            #             'course_id': record.course_id and record.course_id.id or False,
            #             'batch_id': record.batch_id and record.batch_id.id or False,
            #         }
            #
            #         if line.due_date:
            #             date = line.due_date
            #             dict_val.update({
            #                 'date': date
            #             })
            #         elif self.fees_start_date:
            #             date = self.fees_start_date + relativedelta(days=no_days)
            #             dict_val.update({
            #                 'date': date,
            #             })
            #         else:
            #             date_now = (datetime.today() + relativedelta(days=no_days)).date()
            #             dict_val.update({
            #                 'date': date_now,
            #             })
            #         val.append([0, False, dict_val])
            #     record.student_id.write({
            #         'fees_detail_ids': val
            #     })

            record.write({
                'nbr': 1,
                'state': 'done',
                'admission_date': fields.Date.today(),
                'student_id': student_id,
                'is_student': True,
            })
            reg_id = self.env['op.subject.registration'].create({
                'student_id': student_id,
                'batch_id': record.batch_id.id,
                'course_id': record.course_id.id,
                'min_unit_load': record.course_id.min_unit_load or 0.0,
                'max_unit_load': record.course_id.max_unit_load or 0.0,
                'state': 'draft',
            })
            # if not record.phone or not record.mobile:
            #     raise UserError(_('Please fill in the mobile number'))
            reg_id.get_subjects()

    def get_student_vals(self):
        res = super(EduAdmission, self).get_student_vals()
        res.update({
            'identify_id': self.identify_id,
            'prev_institute_id': self.prev_institute_id,
            'prev_result': self.prev_result,
            'category_id': self.category_id.id,
            'institute_cert': self.institute_cert,
        })
        return res

    @api.onchange('student_id', 'is_student')
    def onchange_student(self):
        if self.is_student and self.student_id:
            sd = self.student_id
            self.identify_id = sd.identify_id
            # self.school_avg_score = sd.school_avg_score
            self.prev_institute_id = sd.prev_institute_id
            self.prev_result = sd.prev_result
            self.category_id = sd.category_id.id
            self.institute_cert = sd.institute_cert
        else:
            self.identify_id = ''
            # self.school_avg_score = 0.0
            self.prev_institute_id = ''
            self.prev_result = ''
            self.category_id = False
        super(EduAdmission, self).onchange_student()


class EduAdmissionRegister(models.Model):
    _inherit = 'op.admission.register'

    @api.onchange('course_id')
    def onchange_course_id(self):
        if self.course_id:
            if self.course_id.fees_term_id.product_id:
                self.product_id = self.course_id.fees_term_id.product_id.id