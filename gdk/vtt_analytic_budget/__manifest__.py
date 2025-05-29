# -*- coding: utf-8 -*-

{
    'name': 'Analytic Budget Estimate',
    'category': 'Accounting',
    'version': '1.0',
    'description': """
    Analytic Account Budget Estimate by VietTotal.
    """,
    'depends': [
        'web',
        'account',
        'analytic',
        'report_py3o',
    ],
    # 'auto_install': True,
    'data': [
        'security/ir.model.access.csv',
        'report/budget_template_export.xml',
        'views/budget_template_views.xml',
        'views/account_analytic_views.xml',
        'views/budget_line_views.xml',
        'views/account_analytic_line_views.xml',
        'wizard/budget_add_item_wz_views.xml',
        'wizard/budget_register_wz_views.xml',
        'wizard/budget_custom_import_wz_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'vtt_analytic_budget/static/src/js/*.js',
            'vtt_analytic_budget/static/src/xml/*.xml',
            'vtt_analytic_budget/static/src/scss/*.scss',
        ],
    },
    'license': 'LGPL-3',
}
