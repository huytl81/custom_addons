# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import magic
import base64
import xlrd
from odoo.exceptions import ValidationError


class StockCustomImportWizard(models.TransientModel):
    _name = 'vtt.stock.custom.import.wz'
    _description = 'Stock Custom Import Wizard'

    type = fields.Selection([
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('internal', 'Internal')
    ], 'Type')

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation')

    datas = fields.Binary('Datas')
    filename = fields.Char('Filename')

    use_batch = fields.Boolean('Use Batch?')

    date = fields.Date('Date', default=fields.Date.today())

    def stock_custom_import(self):
        mime = magic.from_buffer(base64.decodebytes(self.datas), mime=True)
        valid_mime = mime in [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
        ]

        if valid_mime:
            RES_PARTNER = self.env['res.partner']
            UOM_UOM = self.env['uom.uom']
            PRODUCT_CATEGORY = self.env['product.category']
            PRODUCT_PRODUCT = self.env['product.product']
            PRODUCT_TEMPLATE = self.env['product.template']
            STOCK_PICKING = self.env['stock.picking']

            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.datas))
            sheet = wb.sheets()[0]

            warehouse = self.picking_type_id.warehouse_id

            pickings = []

            # DATA KEY
            kw_dict = dict.fromkeys([
                'STT', 'Mã hàng', 'Tên hàng', 'Đơn vị tính',
            ], False)
            if self.picking_type_id.code in ['incoming']:
                kw_dict.update({
                    'Mã nhà cung cấp': False,
                    'SL Yêu cầu': False,
                    'Tổng SL Lẻ': False,
                    'SL Thùng': False,
                    'SL Lẻ': False,
                    'Giá lẻ': False,
                    'Quy cách': False,
                    'Ghi chú': False,
                })
            elif self.picking_type_id.code in ['outgoing']:
                kw_dict.update({
                    'Mã khách hàng': False,
                    'SL Thùng': False,
                    'SL Lẻ': False,
                    'Tổng SL Lẻ': False,
                    'Xe': False,
                })
            for col in range(sheet.ncols):
                for k in kw_dict:
                    if sheet.cell(0, col).value.lower().strip() == k.lower().strip():
                        kw_dict[k] = col

            # Check all Valid column
            if all(kw_dict[k] is not False for k in kw_dict) and sheet.nrows > 1:
                # BASE Data
                base_uom = self.env.ref('uom.product_uom_unit')
                base_uom_categ = self.env.ref('uom.product_uom_categ_unit')
                base_product_categ = self.env.ref('product.product_category_all')
                # base_package_type = self.env.ref('vtt_minhduong_config.vtt_data_stock_package_type_box')
                base_product_removal = self.env.ref('product_expiry.removal_fefo')
                base_package_type = self.env.ref('vtt_minhduong_config.vtt_data_stock_package_type_box')

                # Default values
                default_product_values = {
                    'detailed_type': 'product',
                    'uom_id': base_uom.id,
                    'uom_po_id': base_uom.id,
                    'tracking': 'lot',
                    'use_expiration_date': True,
                    'vtt_show_expiration_percentage': True,
                    # 'vtt_use_production_date': True,
                    'categ_id': base_product_categ.id,
                }

                # RAW Data
                raw_data_key_map = {
                    'sequence': 'STT',
                    # 'category_name': 'Ngành hàng',
                    # 'vtt_partner_code': 'Mã nhà cung cấp',
                    'default_code': 'Mã hàng',
                    'name': 'Tên hàng',
                    # 'product_uom_qty': 'SL nhập mua chuyển đổi',
                    # 'price_unit': 'ĐG mua chuyển đổi',
                    'uom_name': 'Đơn vị tính',
                }
                if self.picking_type_id.code in ['incoming']:
                    raw_data_key_map.update({
                        'vtt_partner_code': 'Mã nhà cung cấp',
                        'vtt_demand_qty': 'SL Yêu cầu',
                        'product_uom_qty': 'Tổng SL Lẻ',
                        'vtt_pack_qty': 'SL Thùng',
                        'vtt_surplus_qty': 'SL Lẻ',
                        'price_unit': 'Giá lẻ',
                        'packing_specification': 'Quy cách',
                        'note': 'Ghi chú',
                    })
                elif self.picking_type_id.code in ['outgoing']:
                    raw_data_key_map.update({
                        'vtt_partner_code': 'Mã khách hàng',
                        'vtt_pack_qty': 'SL Thùng',
                        'vtt_surplus_qty': 'SL Lẻ',
                        'product_uom_qty': 'Tổng SL Lẻ',
                        'license_plate': 'Xe',
                    })

                raw_datas = [
                    {dk: sheet.cell(row, kw_dict[raw_data_key_map[dk]]).value for dk in raw_data_key_map}
                    for row in range(sheet.nrows) if row > 0]

                # Fix null quantity
                lst_qty_keys = ['vtt_demand_qty', 'product_uom_qty', 'price_unit', 'packing_specification',
                                'vtt_pack_qty', 'vtt_surplus_qty', ]
                for r in raw_datas:
                    for k in lst_qty_keys:
                        if k in r:
                            if not str(r[k]).replace('.','',1).isdigit():
                                r[k] = 0.0

                # Type check for Product Default code
                for rd in raw_datas:
                    if type(rd['default_code']) is float:
                        if rd['default_code'].is_integer():
                            # rd_tmp = int(rd['default_code'])
                            rd['default_code'] = str(int(rd['default_code']))

                # VEHICLE
                if self.picking_type_id.code in ['outgoing']:
                    raw_vehicles = {
                        dr['license_plate']: False for dr in raw_datas if dr['license_plate']
                    }
                else:
                    raw_vehicles = {}
                if raw_vehicles:
                    for lcp in raw_vehicles:
                        vehicle_id = self.env['fleet.vehicle'].search([('license_plate', '=', lcp)], limit=1)
                        raw_vehicles[lcp] = vehicle_id

                # PARTNER
                raw_partners = {
                    dr['vtt_partner_code']: {
                        'vtt_partner_code': dr['vtt_partner_code'],
                    } for dr in raw_datas
                }
                for r_partner in raw_partners:
                    partner_id = self.env['res.partner'].search([('vtt_partner_code', '=', r_partner)], limit=1)
                    if not partner_id:
                        partner_id = self.env['res.partner'].create({
                            'name': r_partner,
                            'vtt_partner_code': r_partner,
                            'company_type': 'company',
                        })
                    raw_partners[r_partner]['partner_id'] = partner_id

                # UOM
                raw_uoms = {
                    dr['uom_name']: False for dr in raw_datas if dr['uom_name']
                }
                for uom in raw_uoms:
                    uom_id = self.env['uom.uom'].search([('name', '=', uom)], limit=1)
                    if not uom_id:
                        uom_id = self.env['uom.uom'].create({
                            'category_id': base_uom_categ.id,
                            'name': uom,
                            'uom_type': 'smaller',
                        })
                    raw_uoms[uom] = uom_id

                # CATEGORY
                '''
                raw_product_categs = {}
                for dr in raw_datas:
                    if dr['category_name']:
                        categ = ' / '.join(c.strip() for c in dr['category_name'].split('/'))
                        raw_product_categs[categ] = False
                # New Resolve
                for dr_name in raw_product_categs:
                    dr_name_split = dr_name.split('/')
                    if len(dr_name_split) == 1:
                        categ = dr_name_split[0].strip()
                        categ_id = self.env['product.category'].search([('complete_name', '=', categ)], limit=1)
                        if not categ_id:
                            categ_id = self.env['product.category'].create({
                                'name': categ,
                                'removal_strategy_id': base_product_removal.id,
                                # 'parent_id': base_product_categ.id,
                            })
                        raw_product_categs[categ] = categ_id
                    else:
                        for i_index in range(len(dr_name_split)):
                            dr_name_range = dr_name_split[:i_index + 1]
                            categ = ' / '.join([c.strip() for c in dr_name_range])
                            if raw_product_categs.get(categ, False):
                                categ_id = raw_product_categs[categ]
                            else:
                                categ_id = self.env['product.category'].search([('complete_name', '=', categ)],
                                                                               limit=1)
                                if not categ_id:
                                    categ_vals = {
                                        'name': dr_name_split[i_index].strip(),
                                        'removal_strategy_id': base_product_removal.id,
                                    }
                                    if i_index > 0:
                                        parent_categ = ' / '.join([pc.strip() for pc in dr_name_range[:i_index]])
                                        categ_vals['parent_id'] = raw_product_categs[parent_categ].id
                                    categ_id = self.env['product.category'].create(categ_vals)
                            raw_product_categs[categ] = categ_id
                            '''

                # PRODUCTS
                raw_products = {
                    dr['default_code']: {
                        'default_code': dr['default_code'],
                        'name': dr['name'],
                        'uom_name': dr['uom_name'],
                        # 'category_name': dr['category_name'],
                        'packing_specification': dr.get('packing_specification', False),
                    } for dr in raw_datas
                }
                for r_product in raw_products:
                    product_id = self.env['product.product'].search([('default_code', '=', r_product)], limit=1)
                    if not product_id:
                        product_vals = default_product_values.copy()
                        product_vals['name'] = raw_products[r_product]['name']
                        product_vals['default_code'] = r_product
                        if raw_products[r_product]['uom_name']:
                            product_vals['uom_id'] = raw_uoms[raw_products[r_product]['uom_name']].id
                            product_vals['uom_po_id'] = raw_uoms[raw_products[r_product]['uom_name']].id
                        # Category
                        # if raw_products[r_product]['category_name']:
                        #     categ = ' / '.join(c.strip() for c in raw_products[r_product]['category_name'].split('/'))
                        #     product_vals['categ_id'] = raw_product_categs[categ].id
                        if raw_products[r_product]['packing_specification']:
                            product_vals['packaging_ids'] = [(0, 0, {
                                'name': 'Thùng',
                                'package_type_id': base_package_type.id,
                                'qty': raw_products[r_product]['packing_specification'],
                            })]
                            product_vals['packing_specification'] = raw_products[r_product]['packing_specification']
                        product_tmpl = self.env['product.template'].create(product_vals)
                        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl.id)],
                                                                        limit=1)
                    raw_products[r_product]['product_id'] = product_id

                # # GROUP DATA by PARTNER CODE
                # partner_group_datas = {
                #     p_code: [nr for nr in raw_datas if nr['vtt_partner_code'] == p_code] for p_code in raw_partners
                # }
                # GROUP DATA by PARTNER CODE & LICENSE PLATE
                partner_group_datas = {}
                if self.picking_type_id.code in ['outgoing']:
                    for r_data in raw_datas:
                        if (r_data['vtt_partner_code'], r_data['license_plate']) not in partner_group_datas:
                            partner_group_datas[(r_data['vtt_partner_code'], r_data['license_plate'])] = []
                        partner_group_datas[(r_data['vtt_partner_code'], r_data['license_plate'])].append(r_data)
                else:
                    for r_data in raw_datas:
                        if (r_data['vtt_partner_code'], 0) not in partner_group_datas:
                            partner_group_datas[(r_data['vtt_partner_code'], 0)] = []
                        partner_group_datas[(r_data['vtt_partner_code'], 0)].append(r_data)

                # PICKING LOCATION
                if self.picking_type_id.code in ['incoming']:
                    loc_id = self.picking_type_id.default_location_src_id and \
                             self.picking_type_id.default_location_src_id.id or \
                             self.env.ref('stock.stock_location_suppliers').id
                    loc_dest_id = self.picking_type_id.default_location_dest_id.id
                elif self.picking_type_id.code in ['outgoing']:
                    loc_id = self.picking_type_id.default_location_src_id.id
                    loc_dest_id = self.picking_type_id.default_location_dest_id and \
                                  self.picking_type_id.default_location_dest_id.id or \
                                  self.env.ref('stock.stock_location_customers').id

                # LOOP by Partner
                if partner_group_datas:
                    for pgd in partner_group_datas:
                        picking_vals = {
                            'user_id': self.env.user.id,
                            'picking_type_id': self.picking_type_id.id,
                            'scheduled_date': self.date,
                            'date': self.date,
                            'company_id': self.picking_type_id.company_id.id,
                            'location_id': loc_id,
                            'location_dest_id': loc_dest_id,
                            'partner_id': raw_partners[pgd[0]]['partner_id'].id,
                        }
                        if self.picking_type_id.code in ['outgoing']:
                            picking_vals.update({
                                'vtt_fleet_vehicle_id': pgd[1] and raw_vehicles[pgd[1]].id or False,
                                'vtt_fleet_driver_id': pgd[1] and raw_vehicles[pgd[1]].driver_id.id or False,
                            })
                        # Moves
                        move_lines = []
                        for ml_data in partner_group_datas[pgd]:
                            ml_vals = {
                                'sequence': ml_data['sequence'],
                                'name': ml_data['name'],
                                'product_id': raw_products[ml_data['default_code']]['product_id'].id,
                                # 'product_uom': raw_uoms[ml_data['uom_name']].id,
                                'product_uom': ml_data['uom_name'] and raw_uoms[ml_data['uom_name']].id or raw_products[ml_data['default_code']]['product_id'].uom_id.id,
                                'location_id': loc_id,
                                'location_dest_id': loc_dest_id,
                                # 'product_uom_qty': ml_data['product_uom_qty'],
                            }
                            # Quantity
                            # if not ml_data['product_uom_qty'] and (ml_data.get('vtt_pack_qty') or ml_data.get('vtt_surplus_qty')):
                            #     qty = ml_data.get('vtt_pack_qty', 0) * raw_products[ml_data['default_code']]['product_id'].packing_specification + ml_data.get('vtt_surplus_qty', 0)
                            # Fix null quantity
                            if ml_data['product_uom_qty'] == 0.0 and (ml_data['vtt_pack_qty'] > 0 or ml_data['vtt_surplus_qty'] > 0):
                                qty = ml_data['vtt_pack_qty'] * raw_products[ml_data['default_code']]['product_id'].packing_specification + ml_data['vtt_surplus_qty']
                            else:
                                qty = ml_data['product_uom_qty']
                            ml_vals['product_uom_qty'] = qty
                            if self.picking_type_id.code in ['incoming']:
                                ml_vals['price_unit'] = ml_data['price_unit']
                                packing_size = ml_data['packing_specification'] and ml_data['packing_specification'] or raw_products[ml_data['default_code']]['product_id'].packing_specification
                                ml_vals['vtt_demand_qty'] = ml_data['vtt_demand_qty'] * packing_size
                                ml_vals['note'] = ml_data['note']
                            # **Prepare for sale price
                            # if not ml_data.get('price_unit', False):
                            #     ml_vals['price_unit'] = raw_products[ml_data['default_code']]['product_id'].list_price
                            move_lines.append((0, 0, ml_vals))
                        # Add Moves to Picking vals
                        picking_vals['move_lines'] = move_lines
                        picking = STOCK_PICKING.create(picking_vals)
                        # picking = STOCK_PICKING.sudo().create(picking_vals)
                        pickings.append(picking.id)

            # BATCH-PICKING
            batch_ids = []
            if self.use_batch and pickings:
                picking_ids = self.env['stock.picking'].browse(pickings)
                if self.picking_type_id.code in ['outgoing']:
                    lst_lcp = list(set([p.vtt_fleet_vehicle_id for p in picking_ids]))
                    for lcp in lst_lcp:
                        batch_id = self.env['stock.picking.batch'].create({
                            'user_id': self.env.user.id,
                            'company_id': self.picking_type_id.company_id.id,
                            'picking_type_id': self.picking_type_id.id,
                            'vtt_fleet_vehicle_id': lcp.id,
                            'vtt_fleet_driver_id': lcp.driver_id.id,
                        })
                        lcp_pickings = picking_ids.filtered(lambda p: p.vtt_fleet_vehicle_id==lcp)
                        lcp_pickings.write({'batch_id': batch_id.id})
                        batch_ids.append(batch_id.id)
                else:
                    batch_id = self.env['stock.picking.batch'].create({
                        'user_id': self.env.user.id,
                        'company_id': self.picking_type_id.company_id.id,
                        'picking_type_id': self.picking_type_id.id,
                    })
                    picking_ids.write({'batch_id': batch_id.id})
                    batch_ids.append(batch_id.id)

            # RETURN ACTION
            action_pick = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
            action_batch = self.env['ir.actions.actions']._for_xml_id('stock_picking_batch.stock_picking_batch_action')
            if not pickings:
                return {'type': 'ir.actions.act_window_close'}
            else:
                if self.use_batch:
                    action = action_batch
                    if len(batch_ids) == 1:
                        form_view = [(self.env.ref('stock_picking_batch.stock_picking_batch_form').id, 'form')]
                        if 'views' in action:
                            action['views'] = form_view + [(state, view) for state, view in action['views'] if
                                                           view != 'form']
                        else:
                            action['views'] = form_view
                        action['res_id'] = batch_ids[0]
                    else:
                        action['domain'] = [('id', 'in', batch_ids)]
                else:
                    action = action_pick
                    if len(pickings) == 1:
                        form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
                        if 'views' in action:
                            action['views'] = form_view + [(state, view) for state, view in action['views'] if
                                                           view != 'form']
                        else:
                            action['views'] = form_view
                        action['res_id'] = pickings[0]
                    else:
                        action['domain'] = [('id', 'in', pickings)]
            return action
        else:
            raise ValidationError(_('Your file might not valid or included some mistake.'
                                    'Please checkout of it.'))
