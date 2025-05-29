from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import AccessDenied, ValidationError, UserError


class OfficialDispatchRecipient(models.Model):
    _name = "vtt.official.dispatch.receive"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Official Dispatch Recipient"
    _check_company_auto = True
    _order = "id desc"

    name = fields.Text('Official Dispatch Recipient', required=True, index=True, copy=False, default='New')
    description = fields.Text('Description')
    state = fields.Selection([
        ('draft', 'Draft'),  # Nháp
        ('not_received', 'Not yet Receive'),  # Văn thư chưa nhận
        ('received', 'Received'),  # Người nhận đã nhận
        ('sent', 'Sent'),  # Đã gửi cho người nhận
        ('cancel', 'Cancel')  # Hủy bỏ
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    delivery_type = fields.Selection([
        ('email', 'Email'),  # công văn điện tử
        ('physical', 'Physical'),  # công văn giấy
    ], required=True, string='Delivery Type', copy=False, default='email')

    creator_id = fields.Many2one(string='Creator', comodel_name='hr.employee', related='user_id.employee_id')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    department_id = fields.Many2one(string='Creator\'s Department', comodel_name='hr.department',
                                    )
    company_id = fields.Many2one('res.company', 'Company', index=True, required=True,
                                 default=lambda self: self.env.company)
    receive_date = fields.Date(string='Receive Date', default=fields.Datetime.now)
    sender_id = fields.Many2one(string='Sender', comodel_name='res.partner', required=True)
    # sender_address = fields.Char(string='Sender Address', required=True)
    recipient_ids = fields.One2many('vtt.official.dispatch.receive.line', 'vtt_official_dispatch_id',
                                    string='Dispatch Recipient List')
    number_of_dispatches = fields.Integer(string='Number of dispatches')
    is_archive_dispatch = fields.Boolean(string='Is archive Dispatch?', default=False)
    is_sent_to_keeper = fields.Boolean(string='Is sent?', default=False)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'vtt_official_dispatch_recipient_ir_attachments_rel',
        'vtt_dispatch_recipient_id', 'attachment_id', 'Attachments', required=True)
    file_name = fields.Char('Filename')
    approve_date = fields.Date('Approved Date', copy=False)
    allow_unseal = fields.Boolean(string="Allow unseal?", default=True)
    express = fields.Boolean(string="Express document?", default=False)

    def action_receive_confirm(self):
        for rec in self:
            if rec.state == 'draft' or rec.state == 'not_received':
                rec.state = 'received'
                activity_id = self.env.ref('vtt_official_dispatch.vtt_official_dispatch_receive_activity').id
                activity = self.env['mail.activity'].search([
                    ('activity_type_id', '=', activity_id),
                    ('res_id', '=', rec.id)
                ])
                activity.action_feedback(feedback='Received')

    def action_not_receive_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'not_received'
                user_id = self.env.ref('vtt_official_dispatch.group_vtt_keeper').users
                for user in user_id:
                    rec.activity_schedule('vtt_official_dispatch.vtt_official_dispatch_receive_activity',
                                      user_id=user.id,
                                      note=_('There is a new dispatch receive : %s but have not received it yet ') %(rec.name))

    def action_sent(self):
        for rec in self:
            if rec.recipient_ids:
                if rec.state == 'received':
                    rec.state = 'sent'
                    partner_ids = rec.recipient_ids.recipient_id
                    for partner in partner_ids:
                        user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
                        rec.activity_schedule('vtt_official_dispatch.vtt_official_dispatch_receive_activity',
                                              user_id=user.id,
                                              note=_('There is a new dispatch receive : %s') %(rec.name))
            else:
                raise ValidationError(
                    _("No recipient information. Please fill out the information completely."))

    def action_cancel(self):
        for rec in self:
            if rec.state == 'received' or rec.state == 'not_received':
                rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.state = 'draft'

    @api.model
    def create(self, vals):
        templates = super(OfficialDispatchRecipient, self).create(vals)

        for template in templates:
            if template.attachment_ids:
                template.attachment_ids.write({'res_model': self._name, 'res_id': template.id})
        return templates

    def action_send_to_keeper(self):
        if self.is_archive_dispatch == True:
            user_id = self.env.ref('vtt_official_dispatch.group_vtt_keeper').users
            for user in user_id:
                self.activity_schedule('vtt_official_dispatch.vtt_official_dispatch_receive_activity',
                                   user_id=user.id,
                                   note=_('There is a dispatch receive : %s that needs to be archived') %(self.name))
            self.update(
                {'is_sent_to_keeper': True})


class OfficialDispatchRecipientLine(models.Model):
    _name = "vtt.official.dispatch.receive.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Official Dispatch Recipient"
    _order = "id desc"

    vtt_official_dispatch_id = fields.Many2one('vtt.official.dispatch.receive')
    recipient_id = fields.Many2one(string='Recipient', comodel_name='res.partner')
    company_id = fields.Many2one('res.company', 'Company', related='recipient_id.company_id')
    reception_department_id = fields.Selection(
        selection=lambda self: self._department_selection(),
        string="Department",
    )
    number_of_dispatch = fields.Integer(string='Number of dispatch')
    confirm_date = fields.Date(string='Receive Date')
    state = fields.Selection([
        ('not_received', 'Not yet Receive'),  # Văn thư chưa nhận
        ('received', 'Received'),  # Người nhận đã nhận
    ], string='Status', readonly=True, default='not_received')

    @api.onchange('recipient_id')
    def onchange_recipient_id(self):
        return {'domain': {'recipient_id': [
            ('company_id', 'in', [company.id for company in self.vtt_official_dispatch_id.user_id.company_ids])]}}

    @api.onchange('reception_department_id')
    def onchange_reception_department_id(self):
        return {'domain': {'reception_department_id': [
            ('company_id', 'in', [company.id for company in self.vtt_official_dispatch_id.user_id.company_ids])]}}

    def action_confirm(self):
        for rec in self:
            if not rec.confirm_date and rec.state == 'not_received':
                if rec.recipient_id.id == self.env.user.partner_id.id:
                    rec.update(
                        {'confirm_date': datetime.now(),
                         'state': 'received'})
                else:
                    raise UserError(
                        _("Can not confirm for others."))
            else:
                raise UserError(_("Dispatch has been received: confirm date is set or state is received!"))
            activity_id = self.env.ref('vtt_official_dispatch.vtt_official_dispatch_receive_activity').id
            activity = self.env['mail.activity'].search([
                ('activity_type_id', '=', activity_id),
                ('res_id', '=', rec.vtt_official_dispatch_id.id),
                ('user_id', '=', rec.recipient_id.user_id.id),
            ])
            activity.action_feedback(feedback='Received')

    def _department_selection(self):
        department_list = self.env['hr.department'].sudo().search([])
        return list(
            map(lambda department: (str(department.id), ', '.join([department.name])),
                department_list))
