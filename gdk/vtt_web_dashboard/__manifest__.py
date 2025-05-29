# -*- coding: utf-8 -*-
{
    'name': "vtt_web_dashboard",
    'category': 'Hidden',
    'version': '1.0',
    'description':
        """
Odoo Dashboard View.
========================

This module defines the Dashboard view, a new type of reporting view. This view
can embed graph and/or pivot views, and displays aggregate values.
        """,
    'depends': ['web'],
    'auto_install': False,
    'license': 'OEEL-1',
    'assets': {
        'web.assets_backend': [
            'vtt_web_dashboard/static/src/**/*',
            ("remove", "vtt_web_dashboard/static/src/legacy/**/*"),
        ],
        "web.assets_backend_legacy_lazy": [
            "vtt_web_dashboard/static/src/legacy/**/*",
        ],
        'web.qunit_suite_tests': [
            'vtt_web_dashboard/static/tests/**/*.js',
        ],
        'web.assets_qweb': [
            'vtt_web_dashboard/static/src/**/*.xml',
        ],
    }
}
