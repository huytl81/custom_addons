# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HierarchyMixin(models.AbstractModel):
    _name = 'hierarchy.mixin'
    _description = 'Hierarchy List Mixin'
    _hierarchy_parent = 'parent_id'

    hierarchy_level = fields.Integer('Hierarchy Level', compute='_compute_hierarchy_level', precompute=True, store=True)

    def _get_hierarchy_level_depends(self):
        return [self._hierarchy_parent]

    @api.depends(lambda self: self._get_hierarchy_level_depends())
    def _compute_hierarchy_level(self):
        parent_field = self._hierarchy_parent
        for line in self:
            if line[parent_field]:
                line.hierarchy_level = line[parent_field].hierarchy_level + 1
            else:
                line.hierarchy_level = 0