# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64, json


class CampaignImportWizard(models.TransientModel):
    _name = 'campaign.import.wizard'
    _description = 'Campaign Import Wizard'

    file_datas = fields.Binary('XML file')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    def import_campaign_from_json(self):
        docs = json.loads(base64.decodebytes(self.file_datas))
        if docs.get('campaign_data'):
            doc = docs.get('campaign_data')
            location = self.env['investigate.location'].search([
                ('name', '=', doc.get('location'))
            ], limit=1)
            if not location:
                location = self.env['investigate.location'].create({'name': doc.get('location')})
            campaign_vals = {
                'location_id': location.id,
                'description': doc.get('description'),
                'date_from': doc.get('from_date'),
                'date_to': doc.get('to_date')
            }
            campaign = self.env['investigate.campaign'].create(campaign_vals)
            if doc.get('investigations'):
                invest_val_list = []
                for invest in doc.get('investigations'):
                    vals = {
                        'name': invest.get('name'),
                        'department': invest.get('department'),
                        'use_person': invest.get('user'),
                        'device_information': invest.get('device_info'),
                        'preliminary_summary': invest.get('device_preliminary_result'),
                        'date': invest.get('investigation_date'),
                        'campaign_id': campaign.id
                    }
                    invest_val_list.append(vals)
                if invest_val_list:
                    self.env['investigate.investigate'].create(invest_val_list)
