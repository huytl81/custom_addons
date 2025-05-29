# -*- coding: utf-8 -*-

from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('vn', 'account.account')
    def _get_vn_vtt_account_account(self):
        return self._parse_csv('vn', 'account.account', module='vtt_l10n_vn')

    @template('vn', 'account.tax')
    def _get_vn_vtt_withholding_account_tax(self):
        additionnal = self._parse_csv('vn', 'account.tax', module='vtt_l10n_vn')
        self._deref_account_tags('vn', additionnal)
        return additionnal

    @template('vn', 'account.tax.group')
    def _get_vn_vtt_withholding_account_tax_group(self):
        return self._parse_csv('vn', 'account.tax.group', module='vtt_l10n_vn')
