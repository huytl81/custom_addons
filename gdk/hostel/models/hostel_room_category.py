# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RoomCategory(models.Model):
    _name = 'hostel.room.category'
    _description = "Hostel Room Category"

    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one('hostel.room.category', string='Parent Category', ondelete='restrict', index=True)
    child_ids = fields.One2many('hostel.room.category', 'parent_id', string='Child Categories')

    def create_categories(self):
        category1 = {
            'name': 'Category 1',
            'description': 'Description for Category 1'
        }
        category2 = {
            'name': 'Category 2',
            'description': 'Description for Category 2'
        }
        parent_category ={
            'name': 'Category Parent',
            'description': 'Description for parent category',
            'child_ids': [(0,0,category1), (0,0, category2)]
        }

        self.env['hostel.room.category'].create(parent_category)

    def create_categories_batch(self):
        category3 = {
            'name': 'Category 3',
            'description': 'Description for Category 3'
        }
        category4 = {
            'name': 'Category 4',
            'description': 'Description for Category 4'
        }
        self.env['hostel.room.category'].create([category3, category4])