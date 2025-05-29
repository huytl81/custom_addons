/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from  "@odoo/owl";
const actionRegistry = registry.category("actions");
class RODashboard extends Component {}
RODashboard.template = "vtt_mro.CrmDashboard";
//  Tag name that we entered in the first step.
actionRegistry.add("vtt_ro_dashboard_tag", RODashboard);