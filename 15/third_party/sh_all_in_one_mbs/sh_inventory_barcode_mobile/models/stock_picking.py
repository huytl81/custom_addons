# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _


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
            value = next((v[1] for v in selections if v[0] == self.state),
                         self.state)
            if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                message = _(CODE_SOUND_FAIL +
                            'You can not scan item in %s state.') % (value)
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })
            return
        elif self:
            search_mls = False
            domain = []

            if self.env.company.sudo(
            ).sh_stock_barcode_mobile_type == 'barcode':
                search_mls = self.move_ids_without_package.filtered(
                    lambda ml: ml.product_id.barcode == self.
                    sh_stock_barcode_mobile)
                domain = [("barcode", "=", self.sh_stock_barcode_mobile)]

            elif self.env.company.sudo(
            ).sh_stock_barcode_mobile_type == 'int_ref':
                search_mls = self.move_ids_without_package.filtered(
                    lambda ml: ml.product_id.default_code == self.
                    sh_stock_barcode_mobile)
                domain = [("default_code", "=", self.sh_stock_barcode_mobile)]

            elif self.env.company.sudo(
            ).sh_stock_barcode_mobile_type == 'sh_qr_code':
                search_mls = self.move_ids_without_package.filtered(
                    lambda ml: ml.product_id.sh_qr_code == self.
                    sh_stock_barcode_mobile)
                domain = [("sh_qr_code", "=", self.sh_stock_barcode_mobile)]

            elif self.env.company.sudo(
            ).sh_stock_barcode_mobile_type == 'all':
                search_mls = self.move_ids_without_package.filtered(
                    lambda ml: ml.product_id.barcode == self.
                    sh_stock_barcode_mobile or ml.product_id.default_code ==
                    self.sh_stock_barcode_mobile)
                domain = [
                    "|",
                    "|",
                    ("default_code", "=", self.sh_stock_barcode_mobile),
                    ("barcode", "=", self.sh_stock_barcode_mobile),
                    ("sh_qr_code", "=", self.sh_stock_barcode_mobile),
                ]

            if search_mls:
                for move_line in search_mls:      
                    print("\n\n\n\n move_line ==>", move_line)          
                    # 15.0.3  
                    print("\n  self.immediate_transfer  ==>",  self.immediate_transfer )
                    print("\n  move_line.is_initial_demand_editable  ==>",  move_line.is_initial_demand_editable )
                    print("\n  move_line.is_quantity_done_editable  ==>",  move_line.is_quantity_done_editable )                    
                    if self.state == 'draft' and move_line.is_initial_demand_editable:
                        print("\n\n 1")
                        move_line.product_uom_qty = move_line.product_uom_qty + 1                                           
                    elif self.immediate_transfer and move_line.is_quantity_done_editable:
                        print("\n\n 2")
                        move_line.quantity_done = move_line.quantity_done + 1
                    elif move_line.is_quantity_done_editable:
                        print("\n\n 3")
                        move_line.quantity_done = move_line.quantity_done + 1
                        if move_line.quantity_done == move_line.product_uom_qty + 1:                        
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
                                        'title': _("Failed"),
                                        'message': message,
                                    })
                    elif move_line.show_details_visible:
                        if move_line.show_details_visible:
                            if self.env.company.sudo(
                            ).sh_stock_bm_is_notify_on_fail:
                                message = _(
                                    CODE_SOUND_FAIL +
                                    'You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item.'
                                )
                                self.env['bus.bus']._sendone(
                                    self.env.user.partner_id,
                                    'sh_inventory_barcode_mobile_notification_danger',
                                    {
                                        'title': _("Failed"),
                                        'message': message,
                                    })

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
                    break
                    # 15.0.3                
                # for move_line in search_mls:
                #     if move_line.show_details_visible:
                #         if self.env.company.sudo(
                #         ).sh_stock_bm_is_notify_on_fail:
                #             message = _(
                #                 CODE_SOUND_FAIL +
                #                 'You can not scan product item for Detailed Operations directly here, Pls click detail button (at end each line) and than rescan your product item.'
                #             )
                #             self.env['bus.bus']._sendone(
                #                 self.env.user.partner_id,
                #                 'sh_inventory_barcode_mobile_notification_danger',
                #                 {
                #                     'title': _("Failed"),
                #                     'message': message,
                #                 })
                #
                #         return
                #
                #     move_line.quantity_done += 1
                #     if self.env.company.sudo(
                #     ).sh_stock_bm_is_notify_on_success:
                #         message = _(CODE_SOUND_SUCCESS + 'Product: %s Qty: %s'
                #                     ) % (move_line.product_id.name,
                #                          move_line.quantity_done)
                #         self.env['bus.bus']._sendone(
                #             self.env.user.partner_id,
                #             'sh_inventory_barcode_mobile_notification_info', {
                #                 'title': _("Succeed"),
                #                 'message': message,
                #             })
                #     break
            elif self.state == 'draft':
                if self.env.company.sudo().sh_stock_bm_is_add_product:

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
                        }
                        if search_product.uom_id:
                            order_line_val.update({
                                "product_uom": search_product.uom_id.id,
                            })
                        if self.immediate_transfer:
                            order_line_val.update({
                                "quantity_done": 1,
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
                                            new_order_line.product_id.name,
                                            new_order_line.quantity_done)
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_info',
                                {
                                    'title': _("Succeed"),
                                    'message': message,
                                })
                        return

                    else:
                        if self.env.company.sudo(
                        ).sh_stock_bm_is_notify_on_fail:
                            message = _(
                                CODE_SOUND_FAIL +
                                'Scanned Internal Reference/Barcode not exist in any product!'
                            )
                            self.env['bus.bus']._sendone(
                                self.env.user.partner_id,
                                'sh_inventory_barcode_mobile_notification_danger',
                                {
                                    'title': _("Failed"),
                                    'message': message,
                                })

                        return

                else:
                    if self.env.company.sudo(
                    ).sh_stock_bm_is_notify_on_fail:
                        message = _(
                            CODE_SOUND_FAIL +
                            'Scanned Internal Reference/Barcode not exist in any product!'
                        )
                        self.env['bus.bus']._sendone(
                            self.env.user.partner_id,
                            'sh_inventory_barcode_mobile_notification_danger',
                            {
                                'title': _("Failed"),
                                'message': message,
                            })

                    return

            else:
                if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                    message = _(
                        CODE_SOUND_FAIL +
                        'Scanned Internal Reference/Barcode not exist in any product!'
                    )
                    self.env['bus.bus']._sendone(
                        self.env.user.partner_id,
                        'sh_inventory_barcode_mobile_notification_danger', {
                            'title': _("Failed"),
                            'message': message,
                        })

                return
        else:
            # failed message here
            if self.env.company.sudo().sh_stock_bm_is_notify_on_fail:
                message = _(
                    CODE_SOUND_FAIL +
                    'Scanned Internal Reference/Barcode not exist in any product!'
                )
                self.env['bus.bus']._sendone(
                    self.env.user.partner_id,
                    'sh_inventory_barcode_mobile_notification_danger', {
                        'title': _("Failed"),
                        'message': message,
                    })

            return
