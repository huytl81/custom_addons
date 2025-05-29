# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    car_repair_id = fields.Many2one('vtt.car.repair.order', 'Car Repair Order')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='car_repair_id.vehicle_id', store=True)
    vehicle_license_plate = fields.Char('License Plate', related='vehicle_id.license_plate', store=True)


class StockMove(models.Model):
    _inherit = 'stock.move'

    car_repair_id = fields.Many2one('vtt.car.repair.order', 'Car Repair Order', related='picking_id.car_repair_id', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='car_repair_id.vehicle_id', store=True)
    vehicle_license_plate = fields.Char('License Plate', related='vehicle_id.license_plate', store=True)

    car_repair_line_id = fields.Many2one('vtt.car.repair.order.line', 'Car Repair Line')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    car_repair_id = fields.Many2one('vtt.car.repair.order', 'Car Repair Order', related='move_id.car_repair_id', store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', related='car_repair_id.vehicle_id', store=True)
    vehicle_license_plate = fields.Char('License Plate', related='vehicle_id.license_plate', store=True)