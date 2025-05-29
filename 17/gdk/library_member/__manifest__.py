{
    "name": "Library Members",
    "license": "AGPL-3",
    "description": "Manage members borrowing books.",
    "author": "Huy Ta",
    "depends": ["library_app","mail"],
    "license": "LGPL-3",
    "application": False,
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'views/library_book.xml',
        'views/member_view.xml',
        'views/library_menu.xml',
        'views/book_list_template.xml',
    ],
}
