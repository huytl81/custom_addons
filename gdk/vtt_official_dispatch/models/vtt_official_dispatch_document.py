from odoo import fields, models, api, _
from odoo.exceptions import AccessDenied, ValidationError, UserError


class OfficialDispatchDocument(models.Model):
    _name = "vtt.official.dispatch.document"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Official Document"
    _check_company_auto = True

    name = fields.Char('Offcial Document', required=True, index=True, copy=False, default='New')
    request_line_id = fields.Many2one('vtt.official.dispatch.request.line', check_company=True, string='Request',
                                      domain=[('state', 'not in', ['done'])])
    request_id = fields.Many2one(comodel_name='vtt.official.dispatch.request')  #
    requestor_id = fields.Many2one(comodel_name='hr.employee', default=lambda self: self.env.user.employee_id)  #
    requestor_user_id = fields.Many2one(related='requestor_id.user_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    type = fields.Selection([
        ('internal', 'Internal'),  # công văn nội bộ
        ('external', 'External'),  # công văn gửi ra ngoài
        ('incoming', 'Incoming')  # công văn đến
    ], required=True, string='Type', copy=False, default='internal')

    # dispatch_to_department_id = fields.Many2one(related='request_line_id.dispatch_to_department_id', store=True)
    # dispatch_to_company_id = fields.Many2one(related='request_line_id.dispatch_to_company_id', store=True)
    department_id = fields.Many2one(comodel_name='hr.department', store=True)  #
    request_approve_date = fields.Date()  #

    composer_id = fields.Many2one(
        string='Composer', check_company=True,
        comodel_name='hr.employee', default=lambda self: self.env.user.employee_id
    )
    composer_user_id = fields.Many2one(
        string='Composer User',
        related='composer_id.user_id', store=True
    )

    delivery_type = fields.Selection([
        ('email', 'Email'),  # công văn điện tử
        ('physical', 'Physical'),  # công văn giấy
    ], required=True, string='Delivery Type', copy=False, default='physical')

    approver_id = fields.Many2one(comodel_name='hr.employee')  #
    approver_job_id = fields.Char(string='Approver\'s Position',
                                  compute='_compute_approver_info', readonly=True, store=True)
    compose_date = fields.Date('Compose Date', copy=False,
                               default=fields.Datetime.now
                               )  # Ngày Ban Hành
    sent_date = fields.Date('Sent Date', copy=False,
                            )
    category_id = fields.Many2one('vtt.official.dispatch.category', string='Category', required=True)
    content = fields.Text('Content')  # Ghi Chú
    request_attachment_ids = fields.Many2many(
        'ir.attachment', 'vtt_official_dispatch_request_2_ir_attachments_rel',
        'vtt_dispatch_request_id', 'attachment_id', 'Attachments')
    request_file_name = fields.Char('Filename')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'vtt_official_dispatch_document_ir_attachments_rel',
        'vtt_dispatch_document_id', 'attachment_id', 'Attachments')
    file_name = fields.Char('Filename')

    state = fields.Selection([
        ('draft', 'Draft'),  # Nháp
        ('confirm', 'Confirmed'),  # Người soạn thảo xác nhận hoàn thành
        # ('approve', 'Approved'),  # Người yêu cầu xác nhận nội dung và yêu cầu gửi
        ('send', 'Sending'),  # Văn thư xác nhận công văn chuẩn bị gửi
        # ('reject', 'Rejected'),  # Người yêu cầu không xác nhận nội dung
        ('sent', 'Sent'),  # Văn thư xác nhận đã gửi công văn
        ('cancel', 'Cancel')  # Hủy bỏ
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    line_ids = fields.One2many('vtt.official.dispatch.document.line', 'document_id',
                               string='Destination List')  # Nội dung công việc
    total_copies = fields.Integer('Total Copies', compute='_compute_total_copies', store=True)
    total_copies_done = fields.Integer('Total Copies Done', compute='_compute_total_copies_done', store=True)
    delivery_details = fields.Text('Delivery Details', copy=False)
    allow_unseal = fields.Boolean(string="Allow unseal?", default=True)  #
    express = fields.Boolean(string="Express document?", default=False)  #
    check_copy_done = fields.Boolean(default=False)

    @api.depends('line_ids.copies')
    def _compute_total_copies(self):
        """
        Compute total copies from line_ids.
        """
        for rec in self:
            rec.with_company(rec.company_id)
            rec.total_copies = sum([x.copies for x in rec.line_ids])

    @api.depends('line_ids.copies_done')
    def _compute_total_copies_done(self):
        """
        Compute total copies done from line_ids.
        """
        for rec in self:
            rec.with_company(rec.company_id)
            rec.total_copies_done = sum([x.copies_done for x in rec.line_ids])

    @api.depends('approver_id')
    def _compute_approver_info(self):
        for rec in self:
            rec = rec.with_company(rec.company_id)
            if rec.approver_id:
                rec.approver_job_id = rec.approver_id.job_id.name

    def action_create_mail_activity(self, user_id, summary, content):
        self.ensure_one()
        activity_type = self.env['mail.activity.type'].search([('name', 'ilike', 'email')])[0]
        self.env['mail.activity'].create({
            'activity_type_id': activity_type and activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': content or activity_type.default_note,
            'res_model_id': self.env['ir.model']._get_id('vtt.official.dispatch.document'),
            'res_id': self.id,
            'user_id': user_id.id,
        })

    def action_confirm(self):
        """
        Action confirm the completion of document by composer.
        """
        for rec in self:
            if rec.state == 'draft' and len(rec.line_ids):
                rec.state = 'confirm'
                summary = _('Document Ready')
                content = _('Document %s Is Ready.') %(rec.name)
                clericals = self.env.ref("vtt_official_dispatch.group_official_dispatch_clerical").users.filtered(
                    lambda x: x.company_id.id == rec.company_id.id)
                for clerical in clericals:
                    rec.action_create_mail_activity(clerical, summary=summary, content=content)
            elif not len(rec.line_ids):
                raise ValidationError(_('Destination must not be empty!'))

    # def action_approve(self):
    #     """
    #     Action approve the document content by requestor.
    #     """
    #     for rec in self:
    #         if rec.state == 'confirm':
    #             rec.state = 'approve'
    #             rec.request_line_id.state = 'done'
    #             summary = 'Document Need To Be Dispatch'
    #             content = f'Document {rec.name} Is Ready.'
    #             clericals = self.env.ref("vtt_official_dispatch.group_official_dispatch_clerical").users.filtered(
    #                 lambda x: x.company_id.id == rec.company_id.id)
    #             for clerical in clericals:
    #                 rec.action_create_mail_activity(clerical, summary=summary, content=content)
    #
    # def action_reject(self):
    #     """
    #     Action reject the document content by requestor.
    #     """
    #     for rec in self:
    #         if rec.state == 'confirm':
    #             rec.state = 'reject'

    def action_cancel(self):
        """
        Action cancel the document by composer.
        """
        for rec in self:
            if rec.state == 'draft':
                rec.state = 'cancel'
                rec.line_ids.write({'state': 'cancel'})

    # def action_draft(self):
    #     """
    #     Action go back to draft phase by composer.
    #     """
    #     for rec in self:
    #         if rec.state == 'reject':
    #             rec.state = 'draft'
    #             rec.line_ids.write({'state': 'draft'})

    def action_send(self):
        """
        Action confirm to start dispatch document to partner by clerical user.
        """
        for rec in self:
            if rec.state == 'confirm':
                rec.state = 'send'
                rec.line_ids.write({'state': 'process'})

    def action_complete_amount(self):
        for rec in self:
            for line in rec.line_ids:
                line.copies_done = line.copies
            rec.update({'check_copy_done': True})

    def action_send_done(self):
        """
        Action confirm to complete dispatch document to partner by clerical user.
        """
        for rec in self:
            if rec.state == 'send':
                rec.check_copies_done()
                rec.state = 'sent'
                rec.line_ids.write({'state': 'sent'})
                rec.sent_date = fields.Datetime.now()
                if rec.type == 'internal':
                    receive = self.env['vtt.official.dispatch.receive']
                    line_ids = rec.line_ids.sorted(key=lambda r: r.company_id.id)
                    company_list = line_ids.mapped('dispatch_to_company_id')
                    company_ids = []
                    for company in company_list:
                        if int(company) not in company_ids:
                            company_ids.append(int(company))
                    company_ids.sort()
                    receive_dispatch_data = {'name': rec.name,
                                             'sender_id': rec.requestor_user_id.partner_id.id,
                                             'user_id': '',
                                             'delivery_type': rec.delivery_type,
                                             'attachment_ids': rec.attachment_ids,
                                             'recipient_ids': []}
                    for company in company_ids:
                        receive_dispatch_data['company_id'] = company
                        receive_dispatch_data['recipient_ids'] = []
                        for line in line_ids:
                            if company == line.company_id.id:
                                receive_dispatch_data['recipient_ids'].append(
                                    (0, 0, {'recipient_id': line.partner_id.id,
                                            'reception_department_id': line.dispatch_to_department_id,
                                            'number_of_dispatch': line.copies_done,
                                            }))
                                line_ids = line_ids - line
                            else:
                                break
                        company_search = self.env['res.company'].sudo().search([('id', '=', company)])
                        receive_record = receive.with_company(company_search).create(receive_dispatch_data)
                        clerical_groups_id = [self.env.ref('vtt_official_dispatch.group_official_dispatch_clerical').id]
                        clerical_user_id = self.env['res.users'].with_company(company_search).search(
                            [('groups_id.id', '=', clerical_groups_id)])
                        for user_id in clerical_user_id:
                            if company_search in user_id.company_ids:
                                receive_record.activity_schedule(
                                    'vtt_official_dispatch.vtt_official_dispatch_receive_activity',
                                    user_id=user_id.id,
                                    note=_('There is a new dispatch receive : %s') %(rec.name))

    def check_copies_done(self):
        for rec in self:
            for line in rec.line_ids:
                if (line.copies_done == 0) or (line.copies_done < line.copies):
                    raise UserError(_('The amount of documents that have been sent should be equal to requirement!'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'compose_date' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['compose_date']))
            vals['name'] = self.env.company.company_code + '-' + self.env['ir.sequence'].next_by_code(
                'vtt.official.dispatch.document', sequence_date=seq_date) or '/'
        res = super(OfficialDispatchDocument, self).create(vals)
        for template in res:
            if template.attachment_ids:
                template.attachment_ids.write({'res_model': self._name, 'res_id': template.id})
        return res


class OfficialDispatchDocumentLine(models.Model):
    _name = "vtt.official.dispatch.document.line"
    _description = "Dispatch Detail"

    # @api.model
    # def _get_partner_domain(self):
    #     domain = [('company_id', '=', False)]
    #     if self.dispatch_to_company_id:
    #         company_id = self.env['res.company'].search([('id', '=', self.dispatch_to_company_id)]).id
    #         domain = ['|', ('company_id', '=', company_id), ('company_id', '=', False)]
    #     return domain

    document_id = fields.Many2one('vtt.official.dispatch.document', string='Document')
    # company_id = fields.Many2one(related='document_id.company_id')
    dispatch_to_department_id = fields.Many2one('hr.department', string='To Department')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    company_id = fields.Many2one('res.company', 'Company', related='partner_id.company_id')
    dispatch_to_department_id = fields.Selection(
        selection=lambda self: self._department_selection(),
        string="To Department", store=True,
        required=True
    )
    dispatch_to_company_id = fields.Selection(
        selection=lambda self: self._company_selection(), compute='_compute_dispatch_to_company_id',
        string="To Company", store=True,
    )
    receive_location = fields.Char('Receive Location')
    phone = fields.Char('Phone')
    address = fields.Char('Address')
    copies = fields.Integer(
        string='Copies', default=1
    )
    copies_done = fields.Integer(
        string='Copies Done', default=0
    )
    state = fields.Selection([
        ('draft', 'Draft'),  # Nháp
        ('process', 'Process'),  # Đang xử lý
        ('sent', 'Sent'),  # Đã gửi
        ('cancel', 'Cancel')  # Hủy bỏ
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    @api.depends('document_id')
    def _compute_dispatch_to_company_id(self):
        for rec in self:
            if rec.document_id and rec.document_id.company_id:
                rec.dispatch_to_company_id = str(rec.document_id.company_id.id)

    @api.onchange('dispatch_to_company_id')
    def onchange_dispatch_to_department_id(self):
        if self.dispatch_to_company_id:
            return {'domain': {'partner_id': [('company_id', '=', int(self.dispatch_to_company_id))]}}

    @api.onchange('partner_id')
    def _compute_partner_info(self):
        """
        Automatically get partner's contact infomation.
        """
        for rec in self:
            rec = rec.with_company(rec.company_id)
            if rec.partner_id:
                if rec.partner_id.phone:
                    rec.phone = rec.partner_id.phone
                elif rec.partner_id.mobile:
                    rec.partner_id.phone = rec.partner_id.mobile
                rec.address = rec.get_partner_address()

    def get_partner_address(self):
        self.ensure_one()
        address = [x for x in [self.partner_id.street, self.partner_id.street2,
                               self.partner_id.city, self.partner_id.state_id.name, self.partner_id.country_id.name]
                   if x != False]
        return ', '.join(address)

    @api.constrains('copies_done')
    def _compute_copies_done(self):
        for rec in self:
            if rec.copies_done > rec.copies:
                rec.copies_done = rec.copies

    def _company_selection(self):
        company_list = self.env['res.company'].sudo().search([])
        return list(
            map(lambda company: (str(company.id), ', '.join([company.name])),
                company_list))

    def _department_selection(self):
        department_list = self.env['hr.department'].sudo().search([])
        return list(
            map(lambda department: (str(department.id), ', '.join([department.name])),
                department_list))
