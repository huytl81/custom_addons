# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import UserError



class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def default_sh_stock_bm_is_cont_scan(self):
        return self.env.company.sh_stock_bm_is_cont_scan

    sh_stock_barcode_mobile = fields.Char(string="Mobile Barcode")

    sh_stock_bm_is_cont_scan = fields.Char(
        string='Continuously Scan?',
        default=default_sh_stock_bm_is_cont_scan,
        readonly=True)

    @api.onchange('sh_stock_barcode_mobile')
    def _onchange_sh_stock_barcode_mobile(self):

        if self.sh_stock_barcode_mobile in ['', "", False, None]:
            return

        barcode = self.sh_stock_barcode_mobile

        CODE_SOUND_SUCCESS = ""
        CODE_SOUND_FAIL = ""
        if self.env.company.sudo().sh_stock_bm_is_sound_on_success:
            CODE_SOUND_SUCCESS = "SH_BARCODE_MOBILE_SUCCESS_"

        if self.env.company.sudo().sh_stock_bm_is_sound_on_fail:
            CODE_SOUND_FAIL = "SH_BARCODE_MOBILE_FAIL_"

        if not self.picking_type_id:
            if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                message = _(CODE_SOUND_FAIL +
                            'You must first select a Operation Type.')
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })

            return

        if self and self.state not in ['assigned', 'draft', 'confirmed']:
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0]
                          == self.state), self.state)
            # raise UserError(
            #     _(warm_sound_code + "You can not scan item in %s state.") % (value))
            if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                message = _(CODE_SOUND_FAIL + "You can not scan item in %s state.") % (value)
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })
            return            

        elif self:
            # =================================================================
            # If detailed operation enabled
            # =================================================================
            if self.show_operations:
                field_stock_move_line = False
                field_name_stock_move_line = ''

                field_stock_move_line = ''
                # Find field based on operation type and it's settings
                if self.picking_type_id.code in ["internal", "outgoing"]:
                    field_stock_move_line = 'move_line_ids_without_package'

                if self.picking_type_id.code in ['incoming']:
                    field_stock_move_line = 'move_line_nosuggest_ids'
                    if self.show_reserved:
                        field_stock_move_line = 'move_line_ids_without_package'

                if not hasattr(self, field_stock_move_line):
                    # raise UserError(
                    #     _('No any valid stock move line field found for this operation'))
                    if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                        message = _(CODE_SOUND_FAIL + 'No any valid stock move line field found for this operation')
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger', {
                                'title': _("Failed"),
                                'message': message,
                            })
                    return                       

                field_name_stock_move_line = field_stock_move_line
                field_stock_move_line = getattr(
                    self, field_stock_move_line, False)

                records_stock_move_line = False
                domain = []
                # field_stock_move_line.update({
                #     'sh_inventory_barcode_scanner_is_last_scanned': False,
                #     'sequence': 0,
                # })

                if self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'barcode':
                    records_stock_move_line = field_stock_move_line.filtered(
                        lambda ml: ml.product_id.barcode == barcode)
                    domain = [("barcode", "=", barcode)]

                elif self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'int_ref':
                    records_stock_move_line = field_stock_move_line.filtered(
                        lambda ml: ml.product_id.default_code == barcode)
                    domain = [("default_code", "=", barcode)]

                elif self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'sh_qr_code':
                    records_stock_move_line = field_stock_move_line.filtered(
                        lambda ml: ml.product_id.sh_qr_code == barcode)
                    domain = [("sh_qr_code", "=", barcode)]

                elif self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'all':
                    records_stock_move_line = field_stock_move_line.filtered(lambda ml: ml.product_id.barcode == barcode or
                                                                             ml.product_id.default_code == barcode or
                                                                             ml.product_id.sh_qr_code == barcode
                                                                             )

                    domain = ["|", "|",

                              ("default_code", "=", barcode),
                              ("barcode", "=", barcode),
                              ("sh_qr_code", "=", barcode)

                              ]

                # ---------------------------------------
                # Quantity increase or add line logic
                # --------------------------------------
                if records_stock_move_line:
                    # 15.0.4
                    if len(records_stock_move_line) > 1:
                        records_stock_move_line = records_stock_move_line[len(records_stock_move_line) - 1]                                                              
                    
                    qty_done = records_stock_move_line.qty_done + 1
                    vals_line = {
                        'qty_done': qty_done,
                    }                        
                    self.update({
                        field_name_stock_move_line:
                        [(1, records_stock_move_line.id, vals_line)]
                    })                          

                    if records_stock_move_line.qty_done == records_stock_move_line.product_uom_qty + 1:
                        # warning_mess = {
                        #     'title': _('Alert!'),
                        #     'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                        # }
                        # return {'warning': warning_mess} 
                    
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL +
                                'Becareful! Quantity exceed than initial demand!'
                            )
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Alert"),
                                    'message': message,
                                })  
                        return
                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_success:
                        message = _(CODE_SOUND_SUCCESS +
                                    'Product: %s Qty: %s') % (
                                        records_stock_move_line.product_id.name,
                                        qty_done)
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_info',
                            {
                                'title': _("Succeed"),
                                'message': message,
                            })
                    return
                                                          
                    # 15.0.4                    
                    # for line in records_stock_move_line:
                    #     line.qty_done += 1
                    #     line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    #     line.sequence = sequence
                    #
                    #     break
                elif self.state == 'draft':
                    if self.env.user.company_id.sudo().sh_stock_bm_is_add_product:
                        search_product = self.env["product.product"].search(
                            domain, limit=1)
                        if search_product:
                            line_val = {
                                'product_id': search_product.id,
                                'location_dest_id': self.location_dest_id.id,
                                'qty_done': 1,
                                'location_id': self.location_id.id,
                            }
                            if search_product.uom_id:
                                line_val.update({
                                    "product_uom_id": search_product.uom_id.id,
                                })
                            self.update({
                                field_name_stock_move_line: [(0, 0, line_val)]
                            })
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s') % (
                                                search_product.name,
                                                1)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })
                            return
                                            
                        else:
                            # raise UserError(
                            #     _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
                            
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode)
                                    
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Failed"),
                                        'message': message,
                                    })
    
                            return
                    else:
                        # raise UserError(
                        #     _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
                        
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode)
                                
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })

                        return                        

                else:
                    # raise UserError(
                    #     _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode)
                            
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })

                    return
                # ---------------------------------------
                # Quantity increase or add line logic
                # --------------------------------------

            # =================================================================
            # If detailed operation enabled
            # =================================================================
            else:
                # =================================================================
                # If detailed operation not enabled
                # =================================================================
                # self.move_ids_without_package.update({
                #     'sh_inventory_barcode_scanner_is_last_scanned': False,
                #     'sequence': 0,
                # })
                search_mls = False
                domain = []
                if self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'barcode':
                    search_mls = self.move_ids_without_package.filtered(
                        lambda ml: ml.product_id.barcode == barcode)
                    domain = [("barcode", "=", barcode)]

                elif self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'int_ref':
                    search_mls = self.move_ids_without_package.filtered(
                        lambda ml: ml.product_id.default_code == barcode)
                    domain = [("default_code", "=", barcode)]

                elif self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'sh_qr_code':
                    search_mls = self.move_ids_without_package.filtered(
                        lambda ml: ml.product_id.sh_qr_code == barcode)
                    domain = [("sh_qr_code", "=", barcode)]

                elif self.env.user.company_id.sudo().sh_stock_barcode_mobile_type == 'all':
                    search_mls = self.move_ids_without_package.filtered(lambda ml: ml.product_id.barcode == barcode or
                                                                        ml.product_id.default_code == barcode or
                                                                        ml.product_id.sh_qr_code == barcode
                                                                        )

                    domain = ["|", "|",

                              ("default_code", "=", barcode),
                              ("barcode", "=", barcode),
                              ("sh_qr_code", "=", barcode)

                              ]

                if search_mls:
                    for move_line in search_mls:     
                        # 15.0.4
                        if not self.immediate_transfer and self.state == 'draft' and move_line.is_initial_demand_editable:
                            move_line.product_uom_qty = move_line.product_uom_qty + 1
                            
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s') % (
                                                move_line.product_id.name,
                                                move_line.product_uom_qty)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })
                            #break
                            #return                            
                            # move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                            # move_line.sequence = sequence                                              
                        elif self.immediate_transfer and move_line.is_quantity_done_editable:
                            move_line.quantity_done = move_line.quantity_done + 1
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s') % (
                                                move_line.product_id.name,
                                                move_line.quantity_done)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })
                            #break
                            #return                              
                            # move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                            # move_line.sequence = sequence
                        elif move_line.is_quantity_done_editable:
                            move_line.quantity_done = move_line.quantity_done + 1
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s') % (
                                                move_line.product_id.name,
                                                move_line.quantity_done)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })                             
                            # move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                            # move_line.sequence = sequence
                            if move_line.quantity_done == move_line.product_uom_qty + 1:
                                # warning_mess = {
                                #     'title': _('Alert!'),
                                #     'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                                # }
                                # return {'warning': warning_mess}   
                                if self.env.company.sudo(
                                ).sh_stock_bm_is_notify_on_fail:
                                    message = _(
                                        CODE_SOUND_FAIL +
                                        'Becareful! Quantity exceed than initial demand!'
                                    )
                                    self.env['bus.bus']._sendone(
                                        self.env.user.partner_id,
                                        'sh_inventory_barcode_mobile_notification_danger',
                                        {
                                            'title': _("Alert"),
                                            'message': message,
                                        })
    
                                #return                                                     
                        elif move_line.show_details_visible:
                            if move_line.show_details_visible:
                                # raise UserError(
                                #     _(warm_sound_code + "You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item."))
                                #
                                #

                                if self.env.company.sudo(
                                ).sh_stock_bm_is_notify_on_fail:
                                    message = _(
                                        CODE_SOUND_FAIL +
                                        "You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item."
                                    )
                                    self.env['bus.bus']._sendone(
                                        self.env.user.partner_id,
                                        'sh_inventory_barcode_mobile_notification_danger',
                                        {
                                            'title': _("Failed"),
                                            'message': message,
                                        })                                                                          
                        break
                        # 15.0.4                                                                                                
                  
                    # for move_line in search_mls:
                    #     if move_line.show_details_visible:
                    #         raise UserError(
                    #             _(warm_sound_code + "You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item."))
                    #
                    #     if self.state == 'draft':
                    #         move_line.product_uom_qty += 1
                    #         move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    #         move_line.sequence = sequence
                    #     else:
                    #         move_line.quantity_done = move_line.quantity_done + 1
                    #         move_line.sh_inventory_barcode_scanner_is_last_scanned = is_last_scanned
                    #         move_line.sequence = sequence
                    #         if move_line.quantity_done == move_line.product_uom_qty + 1:
                    #             warning_mess = {
                    #                 'title': _('Alert!'),
                    #                 'message': warm_sound_code + 'Becareful! Quantity exceed than initial demand!'
                    #             }
                    #             return {'warning': warning_mess}
                    #     break
                elif self.state == 'draft':
                    if self.env.user.company_id.sudo().sh_stock_bm_is_add_product:
                        if not self.picking_type_id:
                            # raise UserError(
                            #     _(warm_sound_code + "You must first select a Operation Type."))
                            
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL +
                                    "You must first select a Operation Type."
                                )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Failed"),
                                        'message': message,
                                    })
                            return
                                                                
                        search_product = self.env["product.product"].search(
                            domain, limit=1)
                        if search_product:
                            order_line_val = {
                                "name": search_product.name,
                                "product_id": search_product.id,
                                #"product_uom_qty": 1,
                                "price_unit": search_product.lst_price,
                                "location_id": self.location_id.id,
                                "location_dest_id": self.location_dest_id.id,
                                # 'sh_inventory_barcode_scanner_is_last_scanned': is_last_scanned,
                                # 'sequence': sequence,
                            }
                            if search_product.uom_id:
                                order_line_val.update({
                                    "product_uom": search_product.uom_id.id,
                                })
                            if self.immediate_transfer:
                                order_line_val.update({
                                    "quantity_done": 1,
                                })  
                            else:
                                order_line_val.update({
                                    "product_uom_qty": 1,
                                })    
                            old_lines = self.move_ids_without_package
                            new_order_line = self.move_ids_without_package.new(
                                order_line_val)
                            self.move_ids_without_package = old_lines + new_order_line
                            new_order_line._onchange_product_id()
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_success:
                                message = _(CODE_SOUND_SUCCESS +
                                            'Product: %s Qty: %s') % (
                                                search_product.name,
                                                1)
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_info',
                                    {
                                        'title': _("Succeed"),
                                        'message': message,
                                    })
                            return  
                                                    
                        else:
                            # raise UserError(
                            #     _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode)
                                    
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Failed"),
                                        'message': message,
                                    })
        
                            return                    
                    else:
                        # raise UserError(
                        #     _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))

                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode)
                                
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })
    
                        return
                
                else:
                    # raise UserError(
                    #     _(warm_sound_code + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode))
                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL + "Scanned Internal Reference/Barcode/QR Code '%s' does not exist in any product!") % (barcode)
                            
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })

                    return
                # =================================================================
                # If detailed operation not enabled
                # =================================================================
