odoo.define('vtt_web_branding.client', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var WebClient = require('web.WebClient');

var _t = core._t;
var QWeb = core.qweb;

WebClient.include({
    init: function(parent) {
    	this._super.apply(this, arguments);
    	this.set('title_part', {
    		"zopenerp": session.vtt_page_title
    	});
    },
});

});