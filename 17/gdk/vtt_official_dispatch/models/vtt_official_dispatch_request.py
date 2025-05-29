from odoo import fields, models, api, _
from odoo.exceptions import UserError


class OfficialDispatchDocument(models.Model):
    _name = "vtt.official.dispatch.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Document Request"
    _check_company_auto = True
    _order = "id desc"

    @api.model
    def _get_approver_domain(self):
        ids = self.env.ref(
            'vtt_official_dispatch.group_official_dispatch_approver').users.ids
        domain = [('user_id', 'not in', [False]), ('user_id', 'in', ids)]
        if self.company_id.edit_department_id:
            domain.append(('department_id', '=', 'company_id.edit_department_id.id'))
        return domain

    @api.model
    def _get_composer_domain(self):
        ids = self.env.ref(
            'vtt_official_dispatch.group_official_dispatch_editor').users.ids
        domain = [('user_id', 'not in', [False]), ('user_id', 'in', ids)]
        if self.company_id.edit_department_id:
            domain.append(('department_id', '=', 'company_id.edit_department_id.id'))
        return domain

    name = fields.Char('Document Request', required=True,
                       index=True, copy=False, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),  # Nháp
        ('confirm', 'Confirmed'),  # Chờ duyệt/Xác nhận
        ('approve', 'Approved'),  # Người phê duyệt đã duyệt
        ('reject', 'Rejected'),  # Người phê duyệt không duyệt
        ('cancel', 'Cancel')  # Hủy bỏ
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    requestor_id = fields.Many2one(string='Requestor', comodel_name='hr.employee', check_company=True,
                                   default=lambda self: self.env.user.employee_id,
                                   )
    reject_reason = fields.Text(string='Reason')
    requestor_readonly = fields.Boolean(string="Requestor readonly?", compute='_compute_requestor_info')
    requestor_user_id = fields.Many2one(
        string='Requestor User', related='requestor_id.user_id', store=True)
    job_id = fields.Char(string='Requestor\'s Position',
                         compute='_compute_requestor_info', readonly=True, store=True)
    department_id = fields.Many2one(string='Requestor\'s Department', comodel_name='hr.department',
                                    compute='_compute_requestor_info', readonly=True, store=True)
    composer_id = fields.Many2one(
        string='Composer', check_company=True,
        comodel_name='hr.employee', domain=_get_composer_domain
    )
    approver_id = fields.Many2one(
        string='Approver', comodel_name='hr.employee', required=True, check_company=True, domain=_get_approver_domain)
    approver_job_id = fields.Char(string='Approver\'s Position',
                                  compute='_compute_approver_info', readonly=True, store=True)
    approver_user_id = fields.Many2one(
        string='Approver User',
        related='approver_id.user_id', store=True
    )

    type = fields.Selection([
        ('internal', 'Internal'),  # công văn nội bộ
        ('external', 'External'),  # công văn gửi ra ngoài
    ], required=True, string='Type', copy=False, default='internal')
    request_date = fields.Date('Request Date', copy=False,
                               help="Request Date", default=fields.Datetime.now,
                               readonly=True
                               )
    approve_date = fields.Date('Approved Date', copy=False,
                               help="Approved Date", readonly=True)

    line_ids = fields.One2many('vtt.official.dispatch.request.line',
                               'request_id', string='Detail List')
    description_text = fields.Html(string='Description')

    @api.depends('approver_id')
    def _compute_approver_info(self):
        for rec in self:
            rec = rec.with_company(rec.company_id)
            if rec.approver_id:
                rec.approver_job_id = rec.approver_id.job_id.name

    @api.depends('requestor_id')
    def _compute_requestor_info(self):
        for rec in self:
            rec = rec.with_company(rec.company_id)
            if rec.requestor_id:
                rec.department_id = rec.requestor_id.department_id
                rec.job_id = rec.requestor_id.job_id.name
            if self.env.user.has_group('hr.group_hr_manager'):
                rec.requestor_readonly = False
            else:
                rec.requestor_readonly = True

    @api.onchange('requestor_id')
    def _onchange_requestor_id(self):
        if self.requestor_id and self.requestor_id.department_id:
            return {'domain': {'requestor_id': [('department_id', '=', self.requestor_id.department_id.id)]}}

    def action_create_mail_activity(self, user_id, summary, content):
        self.ensure_one()
        activity_type = self.env['mail.activity.type'].search([('name', 'ilike', 'email')])[0]
        self.env['mail.activity'].create({
            'activity_type_id': activity_type and activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': content or activity_type.default_note,
            'res_model_id': self.env['ir.model']._get_id('vtt.official.dispatch.request'),
            'res_id': self.id,
            'user_id': user_id.id,
        })

    def action_confirm(self):
        """
        Action confirm the document request by requestor.
        """
        for rec in self:
            if rec.state == 'draft':
                if not rec.line_ids or not len(rec.line_ids):
                    raise UserError(_('Request details must not be empty!'))
                rec.state = 'confirm'
                summary = _('Document Request Await')
                content = _('Request %s ready to be approve.') %(rec.name)
                rec.action_create_mail_activity(rec.approver_user_id, summary=summary, content=content)

    def action_approve(self):
        """
        Action approve the document request content by approver.
        """
        for rec in self:
            if rec.state == 'confirm':
                if not rec.composer_id:
                    raise UserError(_('Composer have yet to be specific.'))
                rec.state = 'approve'
                rec.line_ids.write({'state': 'approve'})
                rec.approve_date = fields.Datetime.now()
                summary = _('Document Request Have Been Approved')
                content = _('Request %s have been approved') %(rec.name)
                rec.action_create_mail_activity(rec.composer_id.user_id, summary=summary, content=content)

    def action_reject(self):
        """
        Action reject the document request content by approver.
        """
        for rec in self:
            if rec.state == 'confirm':
                rec.state = 'reject'
                summary = _('Document Request Have Been Rejected')
                content = _('Request %s have been rejected with reason: %s') %(rec.name,rec.reject_reason)
                rec.action_create_mail_activity(rec.requestor_user_id, summary=summary, content=content)

    def action_cancel(self):
        """
        Action cancel the document request by requestor.
        """
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'cancel'
                rec.line_ids.write({'state': 'cancel'})

    def action_draft(self):
        for rec in self:
            if rec.state == 'reject':
                rec.state = 'draft'
                rec.line_ids.write({'state': 'cancel'})

    def unlink(self):
        for rec in self:
            if rec.state != "cancel":
                raise UserError(_("Only canceled requests can be unlink."))
        super(OfficialDispatchDocument, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'request_date' in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['request_date']))
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'vtt.official.dispatch.request', sequence_date=seq_date) or '/'
        res = super(OfficialDispatchDocument, self).create(vals)
        return res


class OfficialDispatchDocumentLine(models.Model):
    _name = "vtt.official.dispatch.request.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    name = fields.Char('Document Request Detail', required=True,
                       index=True, copy=False, default='New')
    request_id = fields.Many2one(
        'vtt.official.dispatch.request', string='Request', required=True)
    category_id = fields.Many2one(
        'vtt.official.dispatch.category', string='Category', required=True)
    requestor_id = fields.Many2one(
        string='Requestor', related='request_id.requestor_id', store=True)
    requestor_user_id = fields.Many2one(
        string='Requestor User', related='requestor_id.user_id', store=True)
    composer_id = fields.Many2one(
        string='Composer', related='request_id.composer_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                  default=lambda self: self.env.company)
    delivery_type = fields.Selection([
        ('email', 'Email'),  # công văn điện tử
        ('physical', 'Physical'),  # công văn giấy
    ], required=True, string='Delivery Type', copy=False, default='physical')
    type = fields.Selection(related='request_id.type')
    dispatch_to_department_id = fields.Many2one(
        'hr.department', string='To Department', check_company=False)
    dispatch_to_company_id = fields.Many2one(
        'res.company', string='To Company', check_company=False)
    content = fields.Text('Content')  # Ghi Chú
    release_date = fields.Date('Release date', index=True, copy=False)
    effective_date = fields.Date(related='request_id.approve_date')
    state = fields.Selection([
        ('draft', 'Draft'),  # Nháp
        ('approve', 'Approve'),  # Xác nhận
        ('complete', 'Edit done'),  # Hoàn tất soạn thảo
        ('done', 'Done'),  # Hoàn thành
        ('reject', 'Rejected'),  # Người yêu cầu không xác nhận nội dung
        ('cancel', 'Cancel'),  # Hủy
    ], required=True, string='State', copy=False, default='draft')

    attachment_ids = fields.Many2many(
        'ir.attachment', 'vtt_official_dispatch_request_ir_attachments_rel',
        'vtt_dispatch_request_id', 'attachment_id', 'Attachments', required=True)
    attachment_count = fields.Integer(string="Attachments count", compute='_compute_attachment_ids', store=True)
    file_name = fields.Char('Filename')
    allow_unseal = fields.Boolean(string="Allow unseal?", default=True)
    express = fields.Boolean(string="Express document?", default=False)
    document_ids = fields.One2many('vtt.official.dispatch.document', 'request_line_id', string='Related documents')
    document_count = fields.Integer(string="Documents count", compute='_compute_document_count', store=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = "Detail " + str(len(self.request_id.line_ids) + 1)
        res = super(OfficialDispatchDocumentLine, self).create(vals)
        for template in res:
            if template.attachment_ids:
                template.attachment_ids.write({'res_model': self._name, 'res_id': template.id})
        return res

    @api.depends('attachment_ids')
    def _compute_attachment_ids(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_ids) or 0

    @api.depends('document_ids')
    def _compute_document_count(self):
        for rec in self:
            rec.document_count = len(rec.document_ids) or 0

    def action_view_document(self):
        documents = self.mapped('document_ids')
        action = self.env["ir.actions.actions"]._for_xml_id(
            "vtt_official_dispatch.vtt_official_dispatch_document_view_action")
        if len(documents) > 1:
            action['domain'] = [('id', 'in', documents.ids)]
        elif len(documents) == 1:
            form_view = [(self.env.ref('vtt_official_dispatch.vtt_official_dispatch_document_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = documents.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

    def action_complete(self):
        for rec in self:
            if rec.state == 'approve':
                rec.state = 'complete'
                message_content = _('Document editing of %s is completed.') %(rec.name)
                message_title = _('Complete document editing')
                rec.action_create_mail_activity(rec.requestor_id.user_id, summary=message_title,
                                                content=message_content)

    def action_create_mail_activity(self, user_id, summary, content):
        self.ensure_one()
        activity_type = self.env['mail.activity.type'].search([('name', 'ilike', 'email')])[0]
        self.env['mail.activity'].create({
            'activity_type_id': activity_type and activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': content or activity_type.default_note,
            'res_model_id': self.env['ir.model'].sudo()._get_id('vtt.official.dispatch.request.line'),
            'res_id': self.id,
            'user_id': user_id.id,
        })

    def action_approve(self):
        """
        Action approve the document content by requestor.
        """
        for rec in self:
            if rec.state == 'complete':
                rec.state = 'done'
                # summary = 'Document Need To Be Dispatch'
                # content = f'Document {rec.name} Is Ready.'
                # clericals = self.env.ref("vtt_official_dispatch.group_official_dispatch_clerical").users.filtered(
                #     lambda x: x.company_id.id == rec.company_id.id)
                # for clerical in clericals:
                #     rec.action_create_mail_activity(clerical, summary=summary, content=content)

    def action_reject(self):
        """
        Action reject the document content by requestor.
        """
        for rec in self:
            if rec.state == 'complete':
                rec.state = 'reject'

    def action_draft(self):
        """
        Action go back to draft phase by composer.
        """
        for rec in self:
            if rec.state == 'reject':
                rec.state = 'draft'

    def create_new_document(self):
        """
        Action create new document from request detail by composer.
        """
        for rec in self:
            document = self.env['vtt.official.dispatch.document'].create({
                'request_line_id': rec.id,
                'type': rec.type,
                'department_id': rec.request_id.department_id.id or False,
                'delivery_type': rec.delivery_type,
                'category_id': rec.category_id.id or False,
                'content': rec.content,
                'request_attachment_ids': [(6, 0, [attachment_id for attachment_id in rec.attachment_ids.ids])],
                'request_file_name': rec.file_name,
                'allow_unseal': rec.allow_unseal,
                'approver_id': rec.request_id.approver_id.id,
                'requestor_id': self.env.user.employee_id.id or rec.requestor_id.id,
                'request_approve_date': rec.request_id.approve_date,
            })

        action = {
            'name': _('New Document'),
            'view_mode': 'form',
            'res_model': 'vtt.official.dispatch.document',
            'view_id': self.env.ref('vtt_official_dispatch.vtt_official_dispatch_document_form_view').id,
            'type': 'ir.actions.act_window',
            'res_id': document.id
        }
        return action

    def name_get(self):
        res = []
        for line in self:
            name = line.name if not line.request_id.name else '%s - %s' % (
                line.request_id.name, line.name)
            res.append((line.id, name))
        return res
