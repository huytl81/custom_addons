# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class VttCarRepairOrder(models.Model):
    _inherit = 'vtt.car.repair.order'

    @api.depends("old_revision_ids")
    def _compute_has_old_revisions(self):
        for order in self:
            if order.with_context(active_test=False).old_revision_ids:
                order.has_old_revisions = True
            else:
                order.has_old_revisions = False

    current_revision_id = fields.Many2one('vtt.car.repair.order', 'Current revision', readonly=True, copy=True)
    old_revision_ids = fields.One2many('vtt.car.repair.order', 'current_revision_id', 'Old revisions', readonly=True, domain=["|", ("active", "=", False), ("active", "=", True)], context={"active_test": False})
    revision_number = fields.Integer(string="Revision", copy=False, default=0)
    unrevisioned_name = fields.Char('Original Order Reference', copy=True, readonly=True)
    active = fields.Boolean(default=True)
    has_old_revisions = fields.Boolean(compute="_compute_has_old_revisions")

    _sql_constraints = [
        (
            "revision_unique",
            "unique(unrevisioned_name, revision_number, company_id)",
            "Order Reference and revision must be unique per Company.",
        )
    ]

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if default.get("name", "/") == "/":
            seq = self.env["ir.sequence"]
            default["name"] = seq.next_by_code('vtt.car.repair.order') or "/"
            default["revision_number"] = 0
            default["unrevisioned_name"] = default["name"]
        return super().copy(default=default)

    def copy_revision_with_context(self):
        default_data = self.default_get([])
        new_rev_number = self.revision_number + 1
        default_data.update(
            {
                "revision_number": new_rev_number,
                "unrevisioned_name": self.unrevisioned_name,
                "name": "%s-%02d" % (self.unrevisioned_name, new_rev_number),
                "old_revision_ids": [(4, self.id, False)],
                'order_line_ids': [(0, 0, {
                    'product_id': l.product_id.id,
                    'name': l.name,
                    'price_unit': l.price_unit,
                    'product_uom': l.product_uom.id,
                    'tax_id': [(4, t.id) for t in l.tax_id] if l.tax_id else [],
                    'vtt_car_service_id': l.vtt_car_service_id.id if l.vtt_car_service_id else False,
                    'discount': l.discount,
                    'sequence': l.sequence
                }) for l in self.order_line_ids]
            }
        )
        new_revision = self.copy(default_data)
        self.old_revision_ids.write({"current_revision_id": new_revision.id})
        self.write(
            {"active": False, "state": "cancel", "current_revision_id": new_revision.id}
        )
        return new_revision

    @api.model
    def create(self, values):
        if "unrevisioned_name" not in values:
            if values.get("name", "/") == "/":
                seq = self.env["ir.sequence"]
                values["name"] = seq.next_by_code("vtt.car.repair.order") or "/"
            values["unrevisioned_name"] = values["name"]
        return super().create(values)

    def create_revision(self):
        revision_ids = []
        # Looping over sale order records
        for order_rec in self:
            # Calling  Copy method
            copied_sale_rec = order_rec.copy_revision_with_context()

            msg = _("New revision created: %s") % copied_sale_rec.name
            copied_sale_rec.message_post(body=msg)
            order_rec.message_post(body=msg)

            revision_ids.append(copied_sale_rec.id)

        action = {
            "type": "ir.actions.act_window",
            "name": _("New Repair Order Revisions"),
            "res_model": "vtt.car.repair.order",
            "domain": "[('id', 'in', %s)]" % revision_ids,
            "auto_search": True,
            "views": [
                (False, "tree"),
                (False, "form"),
            ],
            "target": "current",
            "nodestroy": True,
        }

        # Returning the new sale order view with new record.
        return action