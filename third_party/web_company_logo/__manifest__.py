{
    'name': "Company Logo in Backend Navbar",
    'description': """
                    Adding the company logo to the Backend Navbar.
                   """,
    'author': "Kareem Abuzaid, kareem.abuzaid123@gmail.com",
    'version': "13.0.1.0",
    'website': "https://www.kareemabuzaid.com",
    'license': "AGPL-3",
    'depends': [
        'base',
        'web',
    ],
    'images': ['static/description/company_logo.png'],
    'qweb': [
        "static/src/xml/menu.xml",
    ],
    'data': [
        'views/templates.xml',
    ],
    'installable': True,
    'application': False,
}
