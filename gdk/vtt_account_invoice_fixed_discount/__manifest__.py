# Copyright 2017 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Account Fixed Discount by VietTotal",
    "summary": "Allows to apply fixed amount discounts in invoices.",
    "category": "Accounting & Finance",
    "author": "Evils",
    "application": False,
    "installable": True,
    "depends": ["account"],
    "data": [
        "views/account_move_view.xml",
        # "reports/report_account_invoice.xml"
    ],
}
