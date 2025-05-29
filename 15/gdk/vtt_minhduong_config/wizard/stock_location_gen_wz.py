# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockLocationGenerateWizard(models.TransientModel):
    _name = 'vtt.stock.location.gen.wz'
    _description = 'Stock Location Generate Wizard'

    def _get_default_loc_parent(self):
        return self.env.ref('stock.stock_location_stock', False)

    def _get_default_loc_warehouse(self):
        return self.env.ref('stock.warehouse0', False)

    new_loc_name = fields.Char('New Location Name')
    code = fields.Char('Location Keyword')
    loc_pallet = fields.Integer('Pallets Number/ Level')
    loc_level = fields.Integer('Level')

    loc_pallet_start = fields.Integer('Pallet Start Number', default=1)
    loc_level_start = fields.Integer('Level Start Number', default=1)

    pattern = fields.Char('Location Pattern')
    use_barcode = fields.Boolean('Use Barcode?', default=True)

    loc_parent_id = fields.Many2one('stock.location', 'Parent Location', default=_get_default_loc_parent)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', default=_get_default_loc_warehouse)

    type = fields.Selection([
        ('main_loc', 'New Main Location'),
        ('sub_loc', 'Adjustment Sub Location'),
    ], 'Type', default='main_loc')

    @api.onchange('loc_parent_id')
    def onchange_loc_parent(self):
        if self.loc_parent_id:
            self.warehouse_id = self.loc_parent_id.warehouse_id

    def gen_new_stock_location(self):
        STOCK_LOCATION = self.env['stock.location']
        if self.type == 'main_loc':
            main_loc = STOCK_LOCATION.sudo().create({
                'name': self.new_loc_name,
                'warehouse_id': self.warehouse_id,
                'location_id': self.loc_parent_id.id,
                'usage': 'internal',
            })
            main_barcode = f'{self.warehouse_id.code}'
            if self.loc_parent_id:
                main_barcode += f'-{self.loc_parent_id.name.upper()}'
            main_barcode += f'-{self.code.upper()}'
            if self.use_barcode:
                main_loc.barcode = main_barcode
        else:
            main_loc = self.loc_parent_id
            main_barcode = main_loc.barcode
        level_range = range(self.loc_level_start, self.loc_level_start + self.loc_level) if self.loc_level else []
        pallet_range = range(self.loc_pallet_start, self.loc_pallet_start + self.loc_pallet) if self.loc_pallet else []
        if self.loc_level:
            lst_codes = []
            if self.loc_pallet > 0:
                for i in level_range:
                    for j in pallet_range:
                        sub_barcode = main_barcode.replace(self.code.upper(), f'{self.code}{i}.{j}')
                        lst_codes.append((f'{self.code}{i}.{j}', sub_barcode))
            else:
                for i in level_range:
                    sub_barcode = main_barcode.replace(self.code.upper(), f'{self.code}{i}')
                    lst_codes.append((f'{self.code}{i}', sub_barcode))
            val_list = []
            for c in lst_codes:
                vals = {
                    'warehouse_id': self.warehouse_id,
                    'usage': 'internal',
                    'location_id': main_loc.id,
                    'name': c[0]
                }
                if self.use_barcode:
                    vals.update({
                        'barcode': c[1]
                    })
                val_list.append(vals)
            STOCK_LOCATION.sudo().create(val_list)