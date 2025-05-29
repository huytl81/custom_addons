# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api


class AnitaUserFields(models.Model):
    """
    user setting data
    """
    _name = 'anita_list_free.user_field'
    _description = 'anita_list_free.user_field'

    user_data = fields.Many2one(
        comodel_name="anita_list_free.user_data", string="user data", ondelete="cascade")
    name = fields.Char(string="Field Name", required="True")
    string = fields.Char(string="Field String", required="True")
    visible = fields.Boolean(string="Show Fields In List", default=True)
    order = fields.Integer(string="Name")
    
    # the width maybe a string like 100px
    width = fields.Char(string="width")
    parent = fields.Char(string="Parent")

    required = fields.Boolean(string="Required", default=False)
    readonly = fields.Boolean(string="Readonly", default=False)

    fixed_left = fields.Boolean(string="fixed left", default=False)
    fixed_right = fields.Boolean(string="fixed right", default=False)

    domain = fields.Char(string="Domain")
    context = fields.Char(string="Context")
    attrs = fields.Char(string="Attrs")
    options = fields.Char(string="Options")
