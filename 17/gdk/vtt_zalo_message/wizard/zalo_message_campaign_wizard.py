from odoo import api, fields, models

class ZaloMessageCampaignWizard(models.TransientModel):
    _name = 'zalo.message.campaign.wizard'
    _description = 'Zalo Message Campaign Wizard'

    partner_ids = fields.Many2many('res.partner', string='Partners')

    def action_add_partners(self):
        campaign_id = self.env.context.get('active_id')
        if campaign_id:
            campaign = self.env['zalo.message.campaign'].browse(campaign_id)
            campaign.write({'recipient_ids': [(4, partner.id) for partner in self.partner_ids]})
        return {'type': 'ir.actions.act_window_close'}