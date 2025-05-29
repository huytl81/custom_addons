# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import base64


class StudentFeesDetails(models.Model):
    _inherit = 'op.student.fees.details'

    course_detail_id = fields.Many2one('op.student.course', 'Course')

    fees_element_select_ids = fields.One2many('vtt.student.fees.details.select', 'student_fees_id', 'Elements')

    amount = fields.Monetary(compute='_compute_amount', store=True)

    invoice_payment_state = fields.Selection(related='invoice_id.payment_state', readonly=True, string='Payment Status')

    @api.depends('fees_element_select_ids.select', 'fees_element_select_ids')
    def _compute_amount(self):
        for fees in self:
            amount = 0.0
            fees_elements = fees.mapped('fees_element_select_ids').filtered(lambda fe: fe.select)
            if fees_elements:
                for fe in fees_elements:
                    amount += fe.amount
            fees.amount = amount

    def get_invoice(self):
        """ Create invoice for fee payment process of student """
        inv_obj = self.env['account.move']
        partner_id = self.student_id.partner_id
        # student = self.student_id
        account_id = False
        product = self.product_id
        if product.property_account_income_id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s".'
                  'You may have to install a chart of account from Accounting'
                  ' app, settings menu.') % product.name)
        if self.amount <= 0.00:
            raise UserError(
                _('The value of the deposit amount must be positive.'))
        else:
            amount = self.amount
            name = product.name
        invoice = inv_obj.create({
            # 'partner_id': student.name,
            'move_type': 'out_invoice',
            'partner_id': partner_id.id,

        })
        element_select_ids = self.mapped('fees_element_select_ids').filtered(lambda fs: fs.select)
        for records in element_select_ids:
            if records:
                line_values = {'name': records.product_id.name,
                               'fees_element_id': records.fees_element_id.id,
                               'account_id': account_id,
                               'price_unit': records.amount,
                               'quantity': 1.0,
                               'discount': self.discount or False,
                               'product_uom_id': records.fees_element_id.product_id.uom_id.id,
                               'product_id': records.fees_element_id.product_id.id, }
                invoice.write({'invoice_line_ids': [(0, 0, line_values)]})

        if not element_select_ids:
            line_values = {'name': name,
                           # 'origin': student.gr_no,
                           'account_id': account_id,
                           'price_unit': amount,
                           'quantity': 1.0,
                           'discount': self.discount or False,
                           'product_uom_id': product.uom_id.id,
                           'product_id': product.id}
            invoice.write({'invoice_line_ids': [(0, 0, line_values)]})

        invoice._compute_invoice_taxes_by_group()
        self.state = 'invoice'
        self.invoice_id = invoice.id
        return True

    def action_view_invoice(self):
        '''
        This function returns an action that
        display existing invoices of given student ids and show a invoice"
        '''
        result = self.env['ir.actions.act_window'].sudo()._for_xml_id('account.action_move_out_invoice_type')
        fees = result and result.id or False
        result = self.env['ir.actions.act_window'].browse(fees).read()[0]
        inv_ids = []
        for student in self:
            inv_ids += [invoice.id for invoice in student.invoice_ids]
            result['context'] = {'default_partner_id': student.partner_id.id}
        if len(inv_ids) > 1:
            result['domain'] = \
                "[('id','in',[" + ','.join(map(str, inv_ids)) + "])]"
        else:
            res = self.env.ref('account.view_move_form')
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result


class StudentFeesSelection(models.Model):
    _name = 'vtt.student.fees.details.select'
    _description = 'Fees Element Selection'

    student_fees_id = fields.Many2one('op.student.fees.details', 'Fees')
    fees_element_id = fields.Many2one('op.fees.element', string='Element')
    type = fields.Selection(related='fees_element_id.type')
    product_id = fields.Many2one(related='fees_element_id.product_id')
    amount = fields.Float('Amount')
    select = fields.Boolean('Select', default=True)


class StudentCourse(models.Model):
    _inherit = 'op.student.course'

    fees = fields.Float('Fees', default=0.0)

    date_to_enroll = fields.Date('Expected Enroll Date')

    can_edit_course = fields.Boolean('Edit Course Available', compute='_compute_can_edit_course')

    paper_url = fields.Char('Admission Paper Url')

    paper_code = fields.Char('Paper Code')

    is_done = fields.Boolean('Done?', default=False)

    def _compute_can_edit_course(self):
        edit_available = True
        fees_lines = self.env['op.student.fees.details'].search([('course_detail_id', '=', self.id)])
        invoices = fees_lines.sudo().invoice_id
        if any(inv.state == 'posted' for inv in invoices):
            edit_available = False
        self.can_edit_course = edit_available

    category_id = fields.Many2one('op.category', 'Category')

    @api.onchange('course_id')
    def onchange_course(self):
        if self.course_id:
            # if not self.fees_term_id:
            self.fees_term_id = self.course_id.fees_term_id.id
            batch = self.env['op.batch'].search([('course_id', '=', self.course_id.id)], order='code desc', limit=1)
            self.batch_id = batch.id
            self.category_id = self.course_id.category_id.id

    def get_fees(self):
        if self.fees_term_id and self.fees_term_id.product_id:
            exist_fees = self.env['op.student.fees.details'].search([
                ('course_detail_id', '=', self.id)
            ])
            val = []
            product_id = self.fees_term_id.product_id.id
            for line in self.fees_term_id.line_ids:
                if not exist_fees.filtered(lambda f: f.fees_line_id.id == line.id):
                    no_days = line.due_days
                    dict_val = {
                        'fees_line_id': line.id,
                        'course_detail_id': self.id,
                        'product_id': product_id,
                        'state': 'draft',
                        'course_id': self.course_id and self.course_id.id or False,
                        'batch_id': self.batch_id and self.batch_id.id or False,
                    }

                    if line.value_type == 'percent':
                        per_amount = line.value
                        amount = (per_amount * self.fees) / 100
                        dict_val.update({
                            'fees_factor': per_amount,
                            # 'amount': amount,
                            'fees_element_select_ids': [
                                (0, 0, {
                                    'fees_element_id': fe.id,
                                    'amount': (amount * fe.value) / 100
                                }) for fe in line.fees_element_line
                            ]
                        })
                    else:
                        dict_val.update({
                            'fees_factor': 100.0,
                            # 'amount': line.exact_value,
                            'fees_element_select_ids': [
                                (0, 0, {
                                    'fees_element_id': fe.id,
                                    'amount': fe.exact_value
                                }) for fe in line.fees_element_line
                            ]
                        })

                    if line.due_date:
                        date = line.due_date
                        dict_val.update({
                            'date': date
                        })
                    elif self.fees_start_date:
                        date = self.fees_start_date + relativedelta(days=no_days)
                        dict_val.update({
                            'date': date,
                        })
                    else:
                        date_now = (datetime.today() + relativedelta(days=no_days)).date()
                        dict_val.update({
                            'date': date_now,
                        })
                    val.append([0, False, dict_val])
            if val:
                self.student_id.write({
                    'fees_detail_ids': val
                })

    @api.onchange('fees_term_id')
    def onchange_fees_term(self):
        if self.fees_term_id and self.fees_term_id.product_id:
            self.fees = self.fees_term_id.product_id.lst_price

    def write(self, vals):
        res = super(StudentCourse, self).write(vals)
        if vals.get('course_id'):
            if vals.get('fees_term_id'):
                fees_lines = self.env['op.student.fees.details'].search([('course_detail_id', '=', self.id)])
                invoices = fees_lines.sudo().invoice_id
                for inv in invoices:
                    inv.sudo().button_draft()
                invoices.sudo().unlink()
                fees_lines.sudo().unlink()
                self.get_fees()
            self.roll_number = ''
        return res

    @api.model
    def create(self, vals):
        paper_code = self.env["ir.sequence"].next_by_code("vtt.student.course")

        vals.update({
            'paper_code': paper_code
        })
        res = super(StudentCourse, self).create(vals)
        if res:
            idcode = base64.urlsafe_b64encode(f'vtt_edu{res.id}'.encode()).decode()
            res.paper_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/') + f'/edu/admission/report/{idcode}'

        return res

    def send_notify_admission_paper(self):
        self.ensure_one()
        if not self.paper_code:
            self.paper_code = self.env["ir.sequence"].next_by_code("vtt.student.course")
        if not self.paper_url and self.id:
            idcode = base64.urlsafe_b64encode(f'vtt_edu{self.id}'.encode()).decode()
            self.paper_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/') + f'/edu/admission/report/{idcode}'

        if self.student_id.user_id:
            user = self.student_id.user_id
            # self.env.ref('vtt_edu_admission_form.vtt_email_template_student_course_confirm').sudo().send_mail(self.id, force_send=True)
            user.sudo()._notify_channel(
                type_message='info',
                message=_('This is your Admission Paper to complete The Admission.'),
                title=_('Admission Paper.'),
                sticky=True,
                buttons=[
                    {
                        'type': 'ir.actions.act_url',
                        'url': self.paper_url,
                        'target': '_blank',
                        'text': _('Get Your Paper'),
                    }
                ],
            )

    def send_email_admission_paper(self):
        self.ensure_one()
        if not self.paper_code:
            self.paper_code = self.env["ir.sequence"].next_by_code("vtt.student.course")
        if not self.paper_url and self.id:
            idcode = base64.urlsafe_b64encode(f'vtt_edu{self.id}'.encode()).decode()
            self.paper_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/') + f'/edu/admission/report/{idcode}'
        self.env.ref('vtt_edu_admission_form.vtt_email_template_student_course_confirm').sudo().send_mail(self.id, force_send=True)

    def total_reminder_admission_paper(self):
        self.ensure_one()
        self.send_notify_admission_paper()
        self.send_email_admission_paper()

    def to_done(self):
        return self.write({
            'is_done': True,
        })