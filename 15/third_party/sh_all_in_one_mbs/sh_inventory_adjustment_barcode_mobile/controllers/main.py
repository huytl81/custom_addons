# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.


from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class StockAdjustment(http.Controller):

    @http.route(['/sh_all_in_one_mbs/sh_barcode_scanner_get_widget_data'], type="json", auth="user", cors="*")
    def sh_barcode_scanner_get_widget_data(self, **post):
        values = {}
        user_is_stock_manager = request.env.user.has_group('stock.group_stock_manager')
        user_has_stock_multi_locations = request.env.user.has_group('stock.group_stock_multi_locations')
        values['user_is_stock_manager'] = user_is_stock_manager 
        values['user_has_stock_multi_locations'] = user_has_stock_multi_locations 
        values['sh_inventory_adjt_bm_is_cont_scan'] = request.env.company.sudo().sh_inventory_adjt_bm_is_cont_scan 
        
        if user_has_stock_multi_locations:
            domain = [('usage', 'in', ['internal', 'transit'])]                   
            locations = request.env['stock.location'].search_read(domain,['id', 'display_name'])
            values['locations'] = locations             
        return values
    
        
        
    @http.route(['/sh_all_in_one_mbs/sh_barcode_scanner_search_stock_quant_by_barcode'], type="json", auth="user", cors="*")
    def sh_barcode_scanner_search_stock_quant_by_barcode(self, **post):

        CODE_SOUND_SUCCESS = ""
        CODE_SOUND_FAIL = ""
        if request.env.company.sudo().sh_inventory_adjt_bm_is_notify_on_success:
            CODE_SOUND_SUCCESS = "SH_BARCODE_MOBILE_SUCCESS_"

        if request.env.company.sudo().sh_inventory_adjt_bm_is_notify_on_fail:
            CODE_SOUND_FAIL = "SH_BARCODE_MOBILE_FAIL_"
            
        
        values = {}
        values['result'] = False
        barcode = post.get('barcode',False)
        location_id = post.get('location_id',False)
        location_name = post.get('location_name',False)

        if barcode not in ['',"",False,None]:
            domain_product = []
            if request.env.company.sudo().sh_inventory_adjt_barcode_mobile_type == "barcode":
                domain_product = [("product_id.barcode", "=", barcode)]
            elif request.env.company.sudo().sh_inventory_adjt_barcode_mobile_type == "int_ref":
                domain_product = [("product_id.default_code", "=", barcode)]
            elif request.env.company.sudo().sh_inventory_adjt_barcode_mobile_type == "sh_qr_code":
                domain_product = [("product_id.sh_qr_code", "=", barcode)]
            elif request.env.company.sudo().sh_inventory_adjt_barcode_mobile_type == "all":
                domain_product = ["|", "|",
                          ("product_id.default_code", "=", barcode),
                          ("product_id.barcode", "=", barcode),
                          ("product_id.sh_qr_code", "=", barcode)
                        ]
                            
            
            domain = [
                ('location_id.usage', 'in', ['internal', 'transit']),              
            ]
            if location_id:
                domain.append( ('location_id','=',location_id) )    
                
                
            domain = domain + domain_product
            quant = request.env['stock.quant'].search( domain )
            if quant:
                # Take only one first quant if multiple quants found.
                quant = quant[0]
                quant.inventory_quantity += 1
                values['result'] = True
                
                # -----------------------------
                # Give Success Message
                if request.env.company.sudo().sh_inventory_adjt_bm_is_notify_on_success:
                    message = _(CODE_SOUND_SUCCESS + 'Product: %s Counted Quantity: %s'
                                ) % (quant.product_id.name,
                                     quant.inventory_quantity)
                    request.env['bus.bus']._sendone(
                        request.env.user.partner_id,
                        'sh_inventory_adjustment_barcode_mobile_notification_info', {
                            'title': _("Succeed"),
                            'message': message,
                        })
                # -----------------------------
                # Give Success Message                                        
                
            else:
                values['result'] = False
                message = 'Record not found for this scanned barcode:' + barcode
                if location_name:
                    message = 'Record not found for this scanned barcode:' + barcode + ' and location: ' + location_name                    
                values['message'] = message     
                
                # -----------------------------
                # Give Failer Message
                if request.env.company.sudo().sh_inventory_adjt_bm_is_notify_on_fail:
                    message = _(CODE_SOUND_FAIL + message)
                    request.env['bus.bus']._sendone(
                        request.env.user.partner_id,
                        'sh_inventory_adjustment_barcode_mobile_notification_danger', {
                            'title': _("Failed"),
                            'message': message,
                        })
                # -----------------------------
                # Give Failer Message   
                                
                      
        else:
            values['result'] = False
            values['message'] = _('Please enter/type barcode in barcode input and try again.')     
            message = _(CODE_SOUND_FAIL + 'Please enter/type barcode in barcode input and try again.')   
                        
            # -----------------------------
            # Give Failer Message
            if request.env.company.sudo().sh_inventory_adjt_bm_is_notify_on_fail:
                message = _(CODE_SOUND_FAIL + message)
                request.env['bus.bus']._sendone(
                    request.env.user.partner_id,
                    'sh_inventory_adjustment_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })
            # -----------------------------
            # Give Failer Message   
                
        return values
    
              
              
    @http.route(['/sh_all_in_one_mbs/sh_barcode_scanner_stock_quant_tree_btn_apply'], type="json", auth="user", cors="*")
    def sh_barcode_scanner_stock_quant_tree_btn_apply(self, **post):  
        if not request.env.user.has_group('stock.group_stock_manager'):
            raise UserError(_('Only stock manager can do this action'))            
        
        values = {}
        domain = [
            ('location_id.usage', 'in', ['internal', 'transit']),
            ('inventory_quantity_set', '!=', False),                            
        ]            
        quants = request.env['stock.quant'].search( domain )
        if quants:
            for quant in quants:
                quant.action_apply_inventory()
            values['result'] = True
            values['message'] = 'All Counted Quantity successfully applied'
        else:
            values['result'] = False
            values['message'] = 'No any inventory line found for this action - Apply'
        return values
    
        