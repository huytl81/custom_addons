# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ghn_token = fields.Char('GHN Token', config_parameter='ghn_token')
    # ghn_shop_id = fields.Char('GHN shop_id', config_parameter='ghn_shop_id')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        refresh_token = self.env['ir.config_parameter'].sudo().get_param('ghn_token', False)
        if refresh_token:
            res.update({'ghn_token': refresh_token})
        # refresh_shop_id = self.env['ir.config_parameter'].sudo().get_param('ghn_shop_id', False)
        # if refresh_shop_id:
        #     res.update({'ghn_shop_id':refresh_shop_id})
        return res
    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     res['ghn_shop_id'] = int(self.env['ir.config_parameter'].sudo().get_param('ghn_shop_id', default=0))
    #     return res

    @api.model
    def set_values(self):
        if self.ghn_token:
            self.env['ir.config_parameter'].sudo().set_param('ghn_token', self.ghn_token)
        # if self.ghn_shop_id:
        #     self.env['ir.config_parameter'].sudo().set_param('ghn_shop_id', self.ghn_shop_id)
        super(ResConfigSettings, self).set_values()

    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     if self.group_multi_currency:
    #         self.env.ref('base.group_user').write({'implied_ids': [(4, self.env.ref('product.group_sale_pricelist').id)]})
    #     # install a chart of accounts for the given company (if required)
    #     if self.env.company == self.company_id and self.chart_template_id and self.chart_template_id != self.company_id.chart_template_id:
    #         self.chart_template_id._load(15.0, 15.0, self.env.company)