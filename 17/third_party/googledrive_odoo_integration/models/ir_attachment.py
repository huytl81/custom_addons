# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models

class CloudSnippet(models.TransientModel):
    _inherit = 'cloud.snippet'
    
    @api.model
    def read_googledrive_file(self, connection, file_map_id):
        gdrive = connection.get('googledrive',False)
        url, import_id = connection.get('url',False), file_map_id.file_id
        access_token = connection.get('access_token',False)
        status, data, return_vals = False, '', {} 
        if url and access_token:
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
                }
            status, message, data = self.get_file_content_gdrive(connection,gdrive,import_id,headers)
            
        return_vals.update({
            'status':status,
            'content':data
        })
        return return_vals
