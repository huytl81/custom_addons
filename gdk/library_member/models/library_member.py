from odoo import fields, models, api


class Member(models.Model):
    _name = "library.member"
    _description = "Library Member"
    _inherit = ["mail.thread","mail.activity.mixin"]
    # _inherits = {"res.partner": "partner_id"}
    # partner_id = fields.Many2one(
    #     "res.partner",
    #     ondelete="cascade",
    #     required=True)

    partner_id = fields.Many2one("res.partner", delegate=True, ondelete="cascade", required=True)

    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    card_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')