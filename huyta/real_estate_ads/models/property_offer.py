from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError


class AbstractOffer(models.AbstractModel):
    _name = 'estate.property.offer.abstract'
    _description = 'Abstract Model for Property Offers'

    partner_phone = fields.Char(string="Phone")
    partner_email = fields.Char(string="Email")


class TransientOffer(models.TransientModel):
    _name = 'estate.property.offer.transient'
    _description = 'Transient Model for Property Offers'
    _transient_max_count = 0 # unlimited transient records
    _transient_max_hours = 0 # unlimited transient hours

    partner_phone = fields.Char(string="Phone")
    partner_email = fields.Char(string="Email")


class PropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estate Property Offer'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'estate.property.offer.abstract']

    # name = fields.Char(string="Property Offer", required=True, compute="_compute_display_name")
    price = fields.Monetary(string='Price')
    validity = fields.Integer(string='Validity (days)')
    created_date = fields.Date(string='Created Date', default=fields.Date.today())
    deadline = fields.Date(string='Deadline', compute="_compute_deadline", inverse="_inverse_deadline")
    state = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused'), ('pending', 'Pending'),], string='Status', default='pending')
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    partner_email = fields.Char(string="Email", related="partner_id.email")
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id)

    # _sql_constraints = [('check_validity', 'check(validity > 0)', 'Validity cannot be negative')]
    @api.depends('property_id', 'partner_id')
    def _compute_display_name(self) -> None:
        for rec in self:
            # rec.name = (
            rec.display_name = (
                f"{rec.property_id.name} - {rec.partner_id.name}"
                if rec.property_id and rec.partner_id
                else "New Offer"
            )

    @api.depends('created_date', 'validity')
    @api.depends_context('uid')
    def _compute_deadline(self):
        # print(self.env.context)
        # print(self._context)
        for record in self:
            if record.validity and record.created_date:
                record.deadline = record.created_date + timedelta(days=record.validity)
            else:
                record.deadline = False

    def _inverse_deadline(self):
        for record in self:
            if record.deadline and record.created_date:
                record.validity = (record.deadline - record.created_date).days
            else:
                record.validity = False

    def action_accept(self):
        if self.state != 'accepted':
            self._validate_offer_accepted()
            self.state = 'accepted'
            if self.property_id:
                self.property_id.write(
                    {
                        'selling_price': self.price,
                        'state': 'accepted'
                    }
                )
            # self.property_id.selling_price = self.price

    def _validate_offer_accepted(self):
        offer_accepted_count = self.env['estate.property.offer'].search_count([('property_id', '=', self.property_id.id),('state', '=', 'accepted')],limit=1)
        if offer_accepted_count:
            raise ValidationError("Property already has an offer accepted")

    def action_refuse(self):
        if self.state != 'refused':
            self.state = 'refused'
            if self.property_id:
            # if all(self.property_id.offer_ids.mapped('state')):
                self.property_id.update({
                    'state': 'received',
                    'selling_price': 0
                })
                # self.property_id.write({
                #     'state': 'received'
                # })

    # @api.autovacuum
    # def _clean_offers(self):
    #     self.search([('status', '=', 'refused')]).unlink()

    # @api.model_create_multi
    # def create(self,vals_list):
    #     for vals in vals_list:
    #         if not vals.get('created_date'):
    #             vals['created_date'] = fields.Date.today()
    #     return super(PropertyOffer, self).create(vals_list)

    @api.constrains('validity')
    def _check_validity(self):
        for record in self:
            if (record.deadline and record.created_date):
                if (record.deadline <= record.created_date):
                    raise ValidationError("Created date cannot be greater than or equal Deadline")
            else:
                record.validity = False

    # def write(self,vals):
    #     print(vals)
    #     print(self)
    #     print(self.env.cr)
    #     print(self.env.uid)
    #     print(self.env.context)
    #     print(self.env.user)
    #     print(self.env.company)
    #     print(self.env.registry)
    #
    #     rpb = self.env['res.partner'].browse([1,2,3])
    #     print(rpb.name)
    #
    #     rpr = self.env['res.partner'].read(['name', 'email'], domain=[('is_company', '=', True)])
    #     print(rpr)
    #
    #     rprg = self.env['res.partner'].read_group([('is_company', '=', True)], ['name', 'email'], groupby='country_id')
    #     print(rprg)
    #
    #     res_partner_counted = self.env['res.partner'].search_count([
    #         ('is_company', '=', True)
    #     ])
    #     print("Total Partners:", res_partner_counted)
    #
    #     res_partner_ids = self.env['res.partner'].search(
    #         [('is_company', '=', True)],
    #         limit=3, order='name desc'
    #     )
    #     print(res_partner_ids.mapped('name'))
    #
    #     print(res_partner_ids.mapped(lambda r: (r.name, r.phone)))
    #
    #     res_partner_ids_filtered = self.env['res.partner'].search(
    #         [('is_company', '=', True)],
    #         limit=3, order='name desc'
    #     ).filtered(lambda r: len(r.name) > 50)
    #     print(res_partner_ids_filtered.mapped('name'))
    #
    #     return super(PropertyOffer, self).write(vals)

    def extend_offer_deadline(self):
        # dung active_ids chi de tham khao, Odoo chuan dung self
        # for record in self:
        #     record.validity =10
        active_ids = self.env.context.get('active_ids', [])
        print("active_ids: ", active_ids)

        if active_ids:
            offers = self.env['estate.property.offer'].browse(active_ids)
            if offers:
                for offer in offers:
                    offer.validity = 10


    def _extend_offer_deadline(self):
        """Extend the offer deadline by 1 day for all active offers."""
        offers = self.search([])
        for offer in offers:
            if offer.validity:
                offer.validity += 1