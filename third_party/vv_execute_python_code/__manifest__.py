{
    # App information
    'name': 'Execute Python Code',
    'version': '14.0.1.0.0',
    'category': 'Extra Tools',
    'license': 'OPL-1',
    'summary': 'Installing this module, user will be able to execute python code from Odoo ERP.',

    # Author
    'author': 'Er. Vaidehi Vasani',
    'maintainer': 'Er. Vaidehi Vasani',

    # Dependencies
    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'view/python_code_view.xml',
    ],
    'images': ['static/description/execute_python_coverpage.jpeg'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 0.00,
    'currency': 'EUR',
}
