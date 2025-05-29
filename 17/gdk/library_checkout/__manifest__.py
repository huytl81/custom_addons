{
    "name": "Library Book Checkout",
    "description": "Members can borrow books from the library.",
    "author": "Huy Ta",
    "depends": ["library_member", "mail"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizard/checkout_massmessage_wizard_form.xml",
        "views/library_menu.xml",
        "views/checkout_view.xml",
        "views/checkout_kanban_view.xml",
        "data/library_checkout_stage.xml",
    ],
}
