# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2025-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Abbas P(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
{
    'name': 'Draggable And Resizable Wizard',
    'version': '1.0.0',
    'summary': 'Draggable and Resizable Wizard in Odoo Backend',
    'description': 'Make Every Backend Wizard In Odoo Resizable And Draggable.',
    'category': 'Extra Tools',
    'author': 'Huy Ta',
    'maintainer': 'Huy Ta',
    'company': 'Huy Ta',
    'website': 'https://www.odoovn.info',
    'depends': ['base', 'web'],
    'assets': {
        'web.assets_backend': [
            'dragable_and_resizable_wizard/static/src/scss/dragable.scss',
        ]
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3'
}
