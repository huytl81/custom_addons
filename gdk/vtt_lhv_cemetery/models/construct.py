# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, SUPERUSER_ID


class VttConstruct(models.Model):
    _name = 'vtt.construct'
    _description = 'Construction'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'vtt.custom.rating.mixin']

    name = fields.Char('Name')

    land_contract_id = fields.Many2one('vtt.land.contract', 'Land Contract')
    plot_id = fields.Many2one('vtt.land.plot', 'Plot')
    tomb_id = fields.Many2one('vtt.land.tomb', 'Tomb')

    partner_id = fields.Many2one('res.partner', 'Partner')

    construct_item_ids = fields.One2many('vtt.construct.item', 'construct_id', 'Construct Items')

    state = fields.Selection([
        ('new', 'New'),
        ('design_progress', 'Design Progress'),
        ('design_review', 'Review Design'),
        ('cost_estimate', 'Cost Estimate'),
        ('cost_review', 'Cost Review'),
        ('contract', 'Contraction'),
        ('design_done', 'Design Done'),
        ('construct_progress', 'Construction Progress'),
        ('construct_acceptance', 'Construction Acceptance'),
        ('payment', 'Payment'),
        ('done', 'Done')
    ], 'State', default='new')

    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")
    attachment_count = fields.Integer('Attachment Count', compute='_compute_attachment_count')

    def _get_default_stage_id(self):
        return self.env['vtt.construct.stage'].search([('fold', '=', False),
                                                       ('is_closed', '=', False),
                                                       ('stage_type', '=', 'design')], order='sequence', limit=1).id

    def _get_default_construct_stage_id(self):
        return self.env['vtt.construct.stage'].search([('fold', '=', False),
                                                       ('is_closed', '=', False),
                                                       ('stage_type', '=', 'construct')], order='sequence', limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([('stage_type', '=', 'design')], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.model
    def _read_group_construct_stage_ids(self, stages, domain, order):
        stage_ids = stages._search([('stage_type', '=', 'construct')], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    stage_id = fields.Many2one('vtt.construct.stage', string='Designing Stage',
                               store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
                               default=_get_default_stage_id, group_expand='_read_group_stage_ids',
                               copy=False)

    construct_stage_id = fields.Many2one('vtt.construct.stage', string='Construction Stage',
                                         store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
                                         default=_get_default_construct_stage_id,
                                         group_expand='_read_group_construct_stage_ids', copy=False)

    date_contract = fields.Date('Contract Date')
    date_handing = fields.Date('Handing Date')
    date_warranty = fields.Date('Warranty End Date')

    warranty_policy = fields.Text('Warranty Policy')

    contact_ids = fields.Many2many('res.partner', 'construct_partner_contact_rel', string='Contacts')

    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    invoice_ids = fields.Many2many("account.move", string='Invoices')

    amount_total = fields.Float('Total Amount', compute='_compute_amount', store=True)
    amount_untaxed = fields.Float('Untaxed Amount', compute='_compute_amount', store=True)
    amount_tax = fields.Float('Tax Amount', compute='_compute_amount', store=True)
    amount_residual = fields.Float('Residual Amount', compute='_compute_amount', store=True)

    task_ids = fields.One2many('project.task', 'vtt_construct_id', 'Tasks')
    task_count = fields.Integer('Task Count', compute='_compute_task_count')

    show_construct_stage = fields.Boolean('Show Construct Stage?', compute='_compute_show_construct_stage')

    def _compute_show_construct_stage(self):
        for cc in self:
            show_construct_stage = False
            if cc.stage_id.is_closed:
                show_construct_stage = True
            cc.show_construct_stage = show_construct_stage

    def _compute_task_count(self):
        for cc in self:
            cc.task_count = len(cc.task_ids)

    def _compute_attachment_count(self):
        for cc in self:
            cc.attachment_count = len(cc.attachment_ids)

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.amount_residual')
    def _compute_amount(self):
        for cc in self:
            invoices = cc.mapped('invoice_ids').filtered(lambda m: m.state in ['posted'])
            cc.amount_total = sum([i.amount_total for i in invoices])
            cc.amount_untaxed = sum([i.amount_untaxed for i in invoices])
            cc.amount_tax = sum([i.amount_tax for i in invoices])
            cc.amount_residual = sum([i.amount_residual for i in invoices])

    def _compute_invoice_count(self):
        for cc in self:
            invoices = cc.mapped('invoice_ids').filtered(lambda m: m.state not in ['cancel'])
            cc.invoice_count = len(invoices)

    def create_invoice(self):
        self.ensure_one()
        invoice_vals = {
            'move_type': 'out_invoice',
            'invoice_user_id': self.env.user.id,
            'partner_id': self.partner_id.id,
            'currency_id': self.env.company.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'price_unit': 0.0,
                'quantity': 1.0,
            })]
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.write({'invoice_ids': [(4, invoice.id)]})
        return self.view_construct_invoice()

    def view_construct_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.env.user.id,
            })
        action['context'] = context
        return action

    def _get_custom_rating_context(self):
        context = super(VttConstruct, self)._get_custom_rating_context()
        context.update({
            'default_partner_id': self.partner_id.id
        })
        return context

    def view_construct_tasks(self):
        return {
            'name': _('Tasks'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('vtt_construct_id', '=', self.id)],
            'context': {
                'default_vtt_construct_id': self.id,
                'default_user_ids': [self.env.user.id],
                'default_partner_id': self.partner_id.id
            }
        }

    def action_documents(self):
        domain = [('id', 'in', self.attachment_ids.ids)]
        return {
            'name': _("Documents"),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'context': {'create': False},
            'view_mode': 'tree,form',
            'domain': domain
        }
