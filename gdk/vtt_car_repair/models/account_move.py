# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    car_repair_ids = fields.One2many('vtt.car.repair.order', 'invoice_id', readonly=True, copy=False)

    # For showing Vehicle ref
    car_repair_id = fields.Many2one('vtt.car.repair.order', 'Car Repair Order')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='car_repair_id.vehicle_id', store=True)
    vehicle_license_plate = fields.Char('License Plate', related='vehicle_id.license_plate', store=True)

    def unlink(self):
        self.car_repair_ids.filtered(lambda repair: repair.state != 'cancel').write({
            'invoiced': False,
        })
        return super().unlink()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    car_repair_line_ids = fields.One2many('vtt.car.repair.order.line', 'invoice_line_id', readonly=True, copy=False)

    # car_repair_id = fields.Many2one('vtt.car.repair.order', 'Car Repair Order', related='move_id.car_repair_id', store=True)
    # vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='car_repair_id.vehicle_id', store=True)
    # vehicle_license_plate = fields.Char('License Plate', related='vehicle_id.license_plate', store=True)