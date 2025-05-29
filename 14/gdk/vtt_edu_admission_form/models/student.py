# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EduStudent(models.Model):
    # _inherit = 'op.student'
    _inherit = ['op.student', 'multi.step.wizard.mixin']
    _name = 'op.student'
    _order = 'create_date desc'

    identify_id = fields.Char('Identify No.')

    prev_institute_id = fields.Char('Previous Institute')
    prev_result = fields.Char('Previous Result', size=256)

    # prev_result_term1 = fields.Char('Previous Result Term 1', size=256)

    course_id = fields.Many2one('op.course', 'Current Course')
    batch_id = fields.Many2one('op.batch', 'Current Batch')
    batch_code = fields.Char('Batch Code')
    roll_number = fields.Char('Current Roll Number')

    transfer_img = fields.Image('Transfer Image')

    institute_cert = fields.Selection([
        ('has_cert', 'Has Certify'),
        ('no_cert', 'Not Certify Yet')
    ], 'Institute Cert', default='has_cert')

    institute_cert_img = fields.Image('Institute Cert Image')
    # institute_cert_tmp_img = fields.Image('Temporary Institute Cert Image')

    @api.onchange('first_name', 'middle_name', 'last_name')
    def _onchange_name(self):
        if not self.middle_name:
            self.name = str(self.last_name) + " " + str(self.first_name)
        else:
            self.name = str(self.last_name) + " " + str(self.middle_name) + " " + str(self.first_name)

    @api.model
    def create(self, vals):
        res = super(EduStudent, self).create(vals)
        if res and 'batch_code' in vals:
            batch = self.env['op.batch'].search([('code', '=', vals.get('batch_code'))], limit=1)
            if batch:
                # Course Generate
                res.batch_id = batch.id
                res.course_id = batch.course_id.id
                res.course_detail_ids = [
                    (0, 0, {
                        'student_id': res.id,
                        'category_id': batch.course_id.category_id.id,
                        'course_id': batch.course_id.id,
                        'batch_id': batch.id,
                        'fees_term_id': batch.course_id.fees_term_id.id,
                        'fees': batch.course_id.fees_term_id.product_id.lst_price,
                    })
                ]
                for c in res.course_detail_ids:
                    c.get_fees()

                # Fees Generate
                # Subjects Reg Generate
                # reg_id = self.env['op.subject.registration'].create({
                #     'student_id': res.id,
                #     'batch_id': batch.id,
                #     'course_id': batch.course_id.id,
                #     'min_unit_load': batch.course_id.min_unit_load or 0.0,
                #     'max_unit_load': batch.course_id.max_unit_load or 0.0,
                #     'state': 'draft',
                # })
                # reg_id.get_subjects()
            else:
                res.batch_code = ''

        return res

    def check_email(self, email):
        # self.ensure_one()
        exist = self.env['res.users'].search([('login', '=', email)])
        available = True
        if exist:
            available = False
        return available

    def create_student_user(self):
        user_group = self.env.ref("vtt_edu_admission_form.vtt_group_op_student") or False
        student_view_group = self.env.ref("vtt_edu_admission_form.vtt_group_op_student_view") or False
        users_res = self.env['res.users']
        for record in self:
            if not record.user_id:
                user_id = users_res.create({
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'login': record.mobile,
                    'email': record.email,
                    'groups_id': user_group,
                    'is_student': True,
                    'tz': self._context.get('tz'),
                })
                user_id.groups_id = [(4, student_view_group.id)]
                if not self.transfer_img:
                    user_id.groups_id = [(4, self.env.ref('vtt_edu_admission_form.vtt_group_op_student_show_admission_step').id)]
                record.user_id = user_id

    # For Multistep purpose
    @api.model
    def _selection_multistep_state(self):
        return [
            ("start", "Start"),
            ('contact_info', 'Contact Information'),
            ('fees_info', 'Fees Configure'),
            ('payment', 'Payment'),
            ("final", "Final")
        ]

    def _reopen_self(self):
        view_id = self.env.ref('vtt_edu_admission_form.vtt_view_form_op_student_multistep')
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            'view_id': view_id.id,
            "target": "main",
        }

    # Next
    def multistep_state_exit_start(self):
        self.multistep_state = "contact_info"

    def multistep_state_exit_contact_info(self):
        self.multistep_state = "fees_info"

    def multistep_state_exit_fees_info(self):
        self.multistep_state = "payment"

    def multistep_state_exit_payment(self):
        self.multistep_state = "final"

    #     Step done
    def multistep_final_done(self):
        # action = self.env['ir.actions.act_window']._for_xml_id('openeducat_core.act_open_op_student_view_2')
        groups = self.env.ref('vtt_edu_admission_form.vtt_group_op_student_show_admission_step').sudo()
        groups.users = [(3, self.user_id.id)]
        for f in self.fees_detail_ids:
            f.sudo().get_invoice()
            f.sudo().invoice_id.vtt_has_transfer_img = True
        # action['tag'] = 'reload'
        # action['target'] = 'main'
        action = {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

        return action

    # Back
    def state_previous_contact_info(self):
        self.multistep_state = "start"

    def state_previous_fees_info(self):
        self.multistep_state = "contact_info"

    def state_previous_payment(self):
        self.multistep_state = "fees_info"

    # def state_previous_final(self):
    #     self.multistep_state = "start"

    # @api.model
    def action_student_multistep(self):
        # action_id = self.env.ref('vtt_edu_admission_form.vtt_act_window_op_student_multistep')
        # action = self.env["ir.actions.act_window"]._for_xml_id('vtt_edu_admission_form.vtt_act_window_op_student_multistep')
        # action['res_id'] = student.id
        student = self.env['op.student'].search([('user_id', '=', self.env.user.id)], limit=1)
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'op.student',
            'view_mode': 'form',
            'view_id': self.env.ref('vtt_edu_admission_form.vtt_view_form_op_student_multistep').id,
            'context': {'form_view_initial_mode': 'edit'},
            'res_id': student.id,
            'name': 'Admission for now'
        }
        return action


class Partner(models.Model):
    _inherit = 'res.partner'

    def _get_default_country_id(self):
        country = self.env['res.country'].search([('code', '=', 'VN')], limit=1)
        country_id = country and country.id or False
        return country_id

    country_id = fields.Many2one(default=_get_default_country_id)


class SubjectRegistration(models.Model):
    _inherit = "op.subject.registration"

    student_id = fields.Many2one(ondelete="cascade")