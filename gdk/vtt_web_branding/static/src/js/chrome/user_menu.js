odoo.define('vtt_web_branding.menu', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var UserMenu = require('web.UserMenu');

var _t = core._t;
var QWeb = core.qweb;

UserMenu.include({
    _onMenuDocumentation: function () {
        window.open(session.vtt_page_documentation, '_blank');
    },
    _onMenuSupport: function () {
        window.open(session.vtt_page_support, '_blank');
    }
});

});