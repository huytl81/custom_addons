/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class MyCustomAction extends Component {}
MyCustomAction.template = "my_custom_tag_template";

// Đăng ký action để gọi từ XML
registry.category("actions").add("my_custom_tag", MyCustomAction);


