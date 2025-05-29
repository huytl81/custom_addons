# -*- coding: utf-8 -*-
{
    'name':"VTT Map View",
    'summary':"Defines the map view for odoo enterprise",
    'description':"Allows the viewing of records on a map",
    'category': 'Hidden',
    'version':'1.0',
    'depends':['web', 'base_setup'],
    'data':[
        "views/assets.xml",
        "data/datas.xml",
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
    ],
    'qweb':[
        "static/src/xml/map.xml"
    ],
    'auto_install': False,
    'license': 'OEEL-1',
}
