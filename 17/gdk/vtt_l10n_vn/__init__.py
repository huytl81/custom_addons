# -*- coding: utf-8 -*-

import logging
from . import models

_logger = logging.getLogger(__name__)


def _l10n_vn_vtt_post_init(env):
    """ Existing companies that have the Vietnamese Chart of Accounts set """
    for company in env['res.company'].search([('chart_template', '=', 'vn')]):
        _logger.info("Company %s already has the Vietnamese localization installed, updating...", company.name)
        ChartTemplate = env['account.chart.template'].with_company(company)
        ChartTemplate._load_data({
            'account.account': ChartTemplate._get_vn_vtt_account_account(),
            'account.tax': ChartTemplate._get_vn_vtt_withholding_account_tax(),
            'account.tax.group': ChartTemplate._get_vn_vtt_withholding_account_tax_group(),
        })