# -*- coding: utf-8 -*-

from odoo import models, api, _

class AnitaBaseExtend(models.AbstractModel):
    """
    base extend
    """
    _inherit = "base"

    @api.model
    def load_views(self, views, options=None):
        """
        load views
        """
        options = options or {}
        action_id = options.get('action_id')
        self = self.with_context(anita_action_id=action_id)
        return super(AnitaBaseExtend, self).load_views(views, options)

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        extend to add user data
        """
        result = super(AnitaBaseExtend, self)._fields_view_get(
            view_id, view_type, toolbar, submenu)
        # get the default view id
        if not view_id:
            view_id = result.get('view_id', False)
        if view_type == 'tree' or view_type == 'form':
            self._post_process_user_data(view_id, view_type, result)
        return result

    @api.model
    def _post_process_user_data(self, view_id, view_type, result):
        """
        """
        context = self.env.context
        action_id = context.get('anita_action_id', False)
        user_data = self.env['anita_list_free.user_data'].get_user_data(
            self._name, action_id, view_id, view_type)
        result["anita_user_data"] = user_data
        
        return result
