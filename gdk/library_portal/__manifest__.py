{
    "name": "Library Portal",
    "description": "Portal for library members",
    "author": "Huy Ta",
    "license": "AGPL-3",
    "depends": [
        "library_checkout", "portal"
    ],
    "data": [
        "security/library_security.xml",
        "security/ir.model.access.csv",
        "views/portal_templates.xml",
        "views/main_templates.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "library_portal/static/src/css/library.css",
        }
    }
}
