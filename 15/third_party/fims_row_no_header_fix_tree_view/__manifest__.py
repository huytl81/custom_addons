# -*- coding: utf-8 -*-
###############################################################################
#
# Fortutech IMS Pvt. Ltd.
# Copyright (C) 2016-TODAY Fortutech IMS Pvt. Ltd.(<http://www.fortutechims.com>).
#
###############################################################################
{
    'name': 'Row Number Header Fix Tree View',
    'category': 'Report',
    'summary': 'Show Row Number and Fixed Header in Tree/List View',
    'version': '15.0.1.0',
    'license': 'OPL-1',
    'description': """User allow to see header even there is long scrolling datas, in tree view.""",
    'depends': ['base'],
    'author': "Fortutech IMS Pvt. Ltd.",
    'website': "http://www.fortutechims.com",
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            'fims_row_no_header_fix_tree_view/static/src/css/list_header.css',
            'fims_row_no_header_fix_tree_view/static/src/js/row_no.js',
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "images": ['static/description/banner.png'],
}
