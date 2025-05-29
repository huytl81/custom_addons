# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class RepairOrderReport(models.Model):
    _name = 'vtt.repair.order.report'
    _description = 'Repair Order Report'
    _auto = False
    _rec_name = 'dt_order'
    _order = 'dt_order'

    # Order fields
    name = fields.Char('Name', readonly=True)
    dt_order = fields.Datetime('Order Time', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    equipment_id = fields.Many2one('vtt.equipment.equipment', 'Equipment', readonly=True)
    equipment_categ_id = fields.Many2one('vtt.equipment.categ', 'Equipment Category', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly=True)
    state = fields.Selection([
        ('new', 'Quotation'),
        ('confirm', 'Confirmed'),
        ('under_repair', 'Repairing'),
        ('repaired', 'Repaired'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], 'Status', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', "Analytic Account", readonly=True)

    # Partner fields
    partner_invoice_id = fields.Many2one('res.partner', 'Customer Entity', readonly=True)
    country_id = fields.Many2one('res.country', "Customer Country", readonly=True)
    industry_id = fields.Many2one('res.partner.industry', "Customer Industry", readonly=True)
    partner_zip = fields.Char("Customer ZIP", readonly=True)
    state_id = fields.Many2one('res.country.state', "Customer State", readonly=True)

    # Order Line fields
    order_reference = fields.Reference([('vtt.repair.order', 'Repair Order')], 'Related Order',
                                       group_operator="count_distinct")
    categ_id = fields.Many2one('product.category', string="Product Category", readonly=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string="Product Variant", readonly=True)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string="Product", readonly=True)
    uom_id = fields.Many2one(comodel_name='uom.uom', string="Unit of Measure", readonly=True)
    product_uom_qty = fields.Float(string="Qty Ordered", readonly=True)
    qty_to_deliver = fields.Float(string="Qty To Deliver", readonly=True)
    qty_delivered = fields.Float(string="Qty Delivered", readonly=True)
    qty_to_invoice = fields.Float(string="Qty To Invoice", readonly=True)
    qty_invoiced = fields.Float(string="Qty Invoiced", readonly=True)
    price_subtotal = fields.Monetary(string="Untaxed Total", readonly=True)
    price_total = fields.Monetary(string="Total", readonly=True)
    discount = fields.Float(string="Discount %", readonly=True)
    discount_amount = fields.Monetary(string="Discount Amount", readonly=True)

    # aggregates or computed fields
    nbr = fields.Integer(string="# of Lines", readonly=True)
    currency_id = fields.Many2one(comodel_name='res.currency', compute='_compute_currency_id')

    @api.depends_context('allowed_company_ids')
    def _compute_currency_id(self):
        self.currency_id = self.env.company.currency_id

    def _select_order(self):
        select_ = f"""
                    MIN(l.id) AS id,
                    l.product_id AS product_id,
                    t.uom_id AS uom_id,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.product_uom_qty / u.factor * u2.factor) ELSE 0 END AS product_uom_qty,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_delivered / u.factor * u2.factor) ELSE 0 END AS qty_delivered,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM((l.product_uom_qty - l.qty_delivered) / u.factor * u2.factor) ELSE 0 END AS qty_to_deliver,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_invoiced / u.factor * u2.factor) ELSE 0 END AS qty_invoiced,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.qty_to_invoice / u.factor * u2.factor) ELSE 0 END AS qty_to_invoice,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_total) ELSE 0
                    END AS price_total,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_subtotal) ELSE 0
                    END AS price_subtotal,
                    COUNT(*) AS nbr,
                    s.name AS name,
                    s.dt_order AS dt_order,
                    s.state AS state,
                    s.partner_id AS partner_id,
                    s.partner_invoice_id AS partner_invoice_id,
                    s.equipment_id AS equipment_id,
                    s.user_id AS user_id,
                    s.company_id AS company_id,
                    e.categ_id AS equipment_categ_id,
                    t.categ_id AS categ_id,
                    s.analytic_account_id AS analytic_account_id,
                    p.product_tmpl_id,
                    partner.country_id AS country_id,
                    partner.industry_id AS industry_id,
                    partner.state_id AS state_id,
                    partner.zip AS partner_zip,
                    l.discount AS discount,
                    CASE WHEN l.product_id IS NOT NULL THEN SUM(l.price_unit * l.product_uom_qty * l.discount / 100.0) ELSE 0
                    END AS discount_amount,
                    concat('vtt.repair.order', ',', s.id) AS order_reference"""

        additional_fields_info = self._select_additional_fields()
        template = """,
                    %s AS %s"""
        for fname, query_info in additional_fields_info.items():
            select_ += template % (query_info, fname)

        return select_

    def _case_value_or_one(self, value):
        return f"""CASE COALESCE({value}, 0) WHEN 0 THEN 1.0 ELSE {value} END"""

    def _select_additional_fields(self):

        return {}

    def _from_order(self):
        return """
            vtt_repair_order_line l
            LEFT JOIN vtt_repair_order s ON s.id=l.repair_order_id
            JOIN res_partner partner ON s.partner_id = partner.id
            JOIN vtt_equipment_equipment e ON s.equipment_id = e.id
            LEFT JOIN product_product p ON l.product_id=p.id
            LEFT JOIN product_template t ON p.product_tmpl_id=t.id
            LEFT JOIN uom_uom u ON u.id=l.uom_id
            LEFT JOIN uom_uom u2 ON u2.id=t.uom_id
            JOIN {currency_table} ON currency_table.company_id = s.company_id
            """.format(
            currency_table=self.env['res.currency']._get_query_currency_table(self.env.companies.ids, fields.Date.today())
            )

    def _where_order(self):
        return """
            l.display_type IS NULL"""

    def _group_by_order(self):
        return """
            l.product_id,
            l.repair_order_id,
            t.uom_id,
            t.categ_id,
            s.name,
            s.dt_order,
            s.partner_id,
            s.partner_invoice_id,
            s.equipment_id,
            s.user_id,
            s.state,
            s.company_id,
            s.analytic_account_id,
            e.categ_id,
            p.product_tmpl_id,
            partner.country_id,
            partner.industry_id,
            partner.state_id,
            partner.zip,
            l.discount,
            s.id,
            currency_table.rate"""

    def _query(self):
        return f"""
            SELECT {self._select_order()}
            FROM {self._from_order()}
            WHERE {self._where_order()}
            GROUP BY {self._group_by_order()}
        """

    @property
    def _table_query(self):
        return self._query()