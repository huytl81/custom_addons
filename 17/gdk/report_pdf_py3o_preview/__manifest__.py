
{
    "name": "Open PDF Reports and PDF Attachments in Browser",
    "version": "17.0.1.0.0",
    "summary": """
    Preview reports and pdf attachments in browser instead of downloading them.
    Open Report or PDF Attachment in new tab instead of downloading.
""",
    "author": "Ivan Sokolov, Cetmix, Evils",
    "category": "Productivity",
    "license": "LGPL-3",
    # "website": "https://cetmix.com",
    # "live_test_url": "https://demo.cetmix.com",
    "depends": [
        "web",
        "report_py3o",
    ],
    "images": ["static/description/banner.png"],
    "assets": {
        "web.assets_backend": [
            "report_pdf_py3o_preview/static/src/js/tools.esm.js",
            "report_pdf_py3o_preview/static/src/js/report.esm.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
