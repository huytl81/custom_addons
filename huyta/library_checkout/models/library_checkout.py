from odoo import models, fields, api, exceptions


class Checkout(models.Model):
    _name = "library.checkout"
    _description = "Checkout Request"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    @api.model
    def _default_stage_id(self):
        stage = self.env["library.checkout.stage"]
        return stage.search([("state", "=", "new")], limit=1)

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    name = fields.Char(string="Title")
    member_id = fields.Many2one("library.member", required=True)
    member_image = fields.Binary(related="member_id.image_128")
    user_id = fields.Many2one("res.users", "Librarian", default=lambda s: s.env.user)
    # request_date = fields.Date(default=lambda s: fields.Date.today())
    request_date = fields.Date(
        default=lambda s: fields.Date.today(),
        compute="_compute_request_date_onchange",
        store=True,
        readonly=False,
    )
    checkout_date = fields.Date(readonly=True)
    close_date = fields.Date(readonly=True)
    line_ids = fields.One2many("library.checkout.line", "checkout_id", string="Borrowed Books")
    stage_id = fields.Many2one("library.checkout.stage", default=_default_stage_id, group_expand=_group_expand_stage_id)
    state = fields.Selection(related="stage_id.state")
    count_checkouts = fields.Integer(compute="_compute_count_checkouts")
    num_books = fields.Integer(compute="_compute_num_books")
    kanban_state = fields.Selection([("normal", "Doing"),("blocked", "Blocked"),("done", "Ready")],"Kanban State",default="normal")
    color = fields.Integer()
    priority = fields.Selection([("0", "High"),("1", "Very High"),("2", "Critical")],default="0")
    @ api.model
    def create(self, vals):
        # Code before create: should use the 'vals' dict
        new_record = super().create(vals)
        # Code after create: can use the 'new_record' created
        if new_record.stage_id.state in ("open", "done"):
            raise exceptions.UserError("State not allowed for new checkouts.")
        return new_record

    # def write(self, vals):
    #     # Code before write: 'self' has the old values
    #     if "stage_id" in vals:
    #         stage = self.env["library.checkout.stage"]
    #         old_state = self.stage_id.state
    #         new_state = stage.browse(vals["stage_id"]).state
    #         if new_state != old_state and new_state == "open":
    #             vals['checkout_date'] = fields.Date.today()
    #         if new_state != old_state and new_state == "done":
    #             vals['close_date'] = fields.Date.today()
    #     super().write(vals)
    #     # Code after write: can use 'self' with the updated values
    #     return True

    def write(self, vals):
        # reset kanban state when changing stage
        if "stage_id" in vals and "kanban_state" not in vals:
            vals["kanban_state"] = "normal"
        # Code before write: 'self' has the old values
        old_state = self.stage_id.state
        super().write(vals)
        # Code after write: can use 'self' with the updated values
        new_state = self.stage_id.state
        if not self.env.context.get("_checkout_write"):
            if new_state != old_state and new_state == "open":
                self.with_context(_checkout_write=True).write({"checkout_date": fields.Date.today()})
            if new_state != old_state and new_state == "done":
                self.with_context(_checkout_write=True).write({"close_date": fields.Date.today()})
        return True

    # @api.onchange("member_id")
    # def onchange_member_id(self):
    #     today_date = fields.Date.today()
    #     if self.request_date != today_date:
    #         self.request_date = today_date
    #         return {
    #             "warning": {
    #                 "title": "Changed Request Date",
    #                 "message": "Request date changed to today!",
    #             }
    #         }
    @api.depends("member_id")
    def _compute_request_date_onchange(self):
        today_date = fields.Date.today()
        if self.request_date != today_date:
            self.request_date = today_date
            return {
                "warning": {
                    "title": "Changed Request Date",
                    "message": "Request date changed to today!",
                }
            }

    def button_done(self):
        Stage = self.env["library.checkout.stage"]
        done_stage = Stage.search([("state", "=", "done")], limit=1)
        for checkout in self:
            checkout.stage_id = done_stage
        return True

    def _compute_count_checkouts(self):
        members = self.mapped("member_id")
        domain = [
            ("member_id", "in", members.ids),
            ("state", "not in", ["done", "cancel"]),
        ]

        raw = self.read_group(domain, ["id:count"], ["member_id"])

        data = {
            x["member_id"][0]: x["member_id_count"] for x in raw
        }

        for checkout in self:
            checkout.count_checkouts = data.get(checkout.member_id.id, 0)

    @api.depends("line_ids")
    def _compute_num_books(self):
        for checkout in self:
            checkout.num_books = len(checkout.line_ids)
