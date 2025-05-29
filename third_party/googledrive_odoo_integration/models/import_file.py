# -*- coding: utf-8 -*-
##########################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
##########################################################################

from odoo import api, models
import base64

class CloudSnippet(models.TransientModel):
    _inherit = 'cloud.snippet'
    
    @api.model
    def read_googledrive_file(self,connection,file_map_id):
        gdriveapi = connection.get('googledrive',False)
        url = connection.get('url',False)
        import_id = file_map_id.file_id
        access_token = connection.get('access_token',False)
        status = False
        data = ''
        return_vals = {}
        if url and access_token:
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
                }
            status, message, data = self.get_file_content_gdrive(connection,gdriveapi,import_id,headers)
        return_vals.update({
            'status':status,
            'content':data
        })
        return return_vals

    
    @api.model
    def get_file_content_gdrive(self,connection,gdriveapi,import_id,headers):
        url = connection.get('url','')
        url += import_id + "?alt=media"    ##The alt=media URL parameter tells the server that a download of content is being requested.
        message = ''
        status = False
        data = {}
        try:
            response = gdriveapi.call_drive_api(url,'GET',data=data,headers=headers,files=None)
            status = True
        except Exception as e:
            message = import_id+':'+ str(e)
        if status:
            data = response
        return status,message,data
        
    
    @api.model
    def _import_googledrive_attachment_cloud(self,connection, instance_id,storage_type,
                                    folder_id,exported_records):
        printmessage = ''
        message_wizard = self.env['cloud.message.wizard']
        odoo_file_env = self.env['cloud.odoo.file.mapping']
        successfull_ids = []
        unsuccessfull_ids = []
        access_token = connection.get('access_token',False)
        gdriveapi = connection.get('googledrive',False)
        status = False
        url = connection.get('url',False)
        message = 'Error:Issue While Creating Folder In Odoo'
        count = 0
        if url and access_token:
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
                }
            for record in exported_records:
                model = exported_records[record].get('model')
                record_id = exported_records[record].get('record_id')
                record_folder_name = exported_records[record].get('record_folder_name')
                record_folder_path = exported_records[record].get('record_folder_path')
                record_folder_id = exported_records[record].get('record_folder_id')
                url += "?q=" + "'%s'"%record_folder_id + "+in+parents&fields=files(name,id,originalFilename)"                # urlold = "https://www.googleapis.com/drive/v3/files?q='"+"%s"%record_folder_id+"'+in+parents&fields=files(name,id,originalFilename)"            
                response_data = {}
                data= {}
                try:
                    response_data = gdriveapi.call_drive_api(url,'GET',data=data,headers=headers,files=None)
                except Exception as e:
                    message = str(e)
                if 'files' in response_data:
                    all_import_ids = set([check['id'] for check in response_data.get('files')]) ##all files_ids in folder e.g S00002id2 
                    exported_file_ids = set(exported_records[record]['file_ids'])   ##files_ids in which are already exported to folder e.g S00002id2 
                    all_import_ids -= exported_file_ids
                    to_import_ids = list(all_import_ids)  
                    for import_id in to_import_ids:
                        response_metadata = self.get_import_file_data_gdrive(connection,import_id,access_token,gdriveapi,headers) ##for get meta_data
                        message = response_metadata.get('message','')
                        if response_metadata.get('status',False):
                            status = False
                            file_id = response_metadata['file_id']
                            file_url = response_metadata['file_url']
                            name = response_metadata['name']
                            mime_type = response_metadata['mime_type']
                            status, message, data = self.get_file_content_gdrive(connection,gdriveapi,import_id,headers) ##for getting file raw data
                            if status:
                                content = base64.b64encode(data)
                                attachment_id = self.create_import_attachment(record_id, model, content, mime_type, name, import_id)
                                if attachment_id:
                                    vals = {
                                        'file_id':import_id,
                                        'file_url':file_url,
                                        'folder_id':folder_id,
                                        'instance_id':instance_id,
                                        'attachment_id':attachment_id.id,
                                        'record_folder_id':record_folder_id,
                                        'record_folder_path':record_folder_path,
                                        'record_folder_name':record_folder_name,
                                        'record_id':record_id,
                                        'state':'done',
                                        'message':'Successfully Imported'
                                    }
                                    self.create_file_mapping(vals,storage_type,'cloud.odoo.file.mapping')
                                    count+=1
                        else:
                            unsuccessfull_ids.append(message)
        if not unsuccessfull_ids and count:
            message = '%i Attachments Has Been Imported'%(count)
        if count and unsuccessfull_ids:
            message = '%i Attachments Has Been Imported And Unsuccessfull Attachment With Ids And Error Message%s'%(count,",".join(unsuccessfull_ids))
        if not count and not unsuccessfull_ids:
            message = 'No Attachment Found For Given Records In Cloud'
        return message_wizard.generate_message(message)



    
    @api.model
    def get_import_file_data_gdrive(self,connection,import_id,access_token,gdriveapi,headers):
        url = connection.get('url',False)
        url += import_id
        message = ''
        status = False
        return_vals = {}
        data = {}
        try:
            response = gdriveapi.call_drive_api(url,'GET',data=data,headers=headers,files=None)
            status = True
        except Exception as e:
            message ='Error:' + str(e)
        if status:
            return_vals.update({
            'file_id':response.get('id',''),
            'name': response.get('name',''),
            'mime_type':response.get('mimeType',{}),
            })
            if return_vals['file_id']:
                return_vals['file_url'] = 'https://drive.google.com/file/d/%s/view'%import_id
        return_vals.update({
            'status':status,
            'message':message
        })
        return return_vals
