# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    vtt_has_transfer_img = fields.Boolean('Has Transfer Image?', default=False)

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()
        for move in self:
            if move.payment_state == 'paid':
                fees = self.env['op.student.fees.details'].search([('invoice_id', '=', move.id)])
                if fees:
                    if not fees.course_detail_id.roll_number:
                        res = fees.env['op.student.course'].search([
                            ('batch_id', '=', fees.batch_id.id),
                            ('roll_number', '!=', '')
                        ], order='roll_number desc', limit=1)
                        if res:
                            old_number = int(res.roll_number[len(fees.batch_id.code):])
                            new_number = old_number + 1
                            new_roll = f'{fees.batch_id.code}{new_number:03}'
                        else:
                            new_roll = f'{fees.batch_id.code}001'

                        fees.course_detail_id.roll_number = new_roll
                        fees.student_id.roll_number = new_roll
                        fees.student_id.course_id = fees.course_id.id
                        fees.student_id.batch_id = fees.batch_id.id
                        if fees.student_id:
                            self.env.ref('vtt_edu_admission_form.vtt_email_template_student_payment_confirm').with_context(fees_payment_value=move.amount_total_signed, currency=move.currency_id).send_mail(fees.student_id.id, force_send=False)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fees_element_id = fields.Many2one('op.fees.element', 'Fees Element')