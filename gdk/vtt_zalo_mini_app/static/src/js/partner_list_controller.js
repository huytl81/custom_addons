/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class PartnerListController extends ListController {
   setup() {
       super.setup();
   }
   OnTestClick() {
      // this.actionService.doAction('vtt_zalo_mini_app.action_quick_create_partner');
      this.actionService.doAction({
          type: 'ir.actions.act_window',
         //  res_id: 'view_quick_create_partner_form',
          res_model: 'quick.create.partner',
          name:'Tạo nhanh',
          view_id: 'view_quick_create_partner_form',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
registry.category("views").add("button_partner_in_tree", {
   ...listView,
   Controller: PartnerListController,
   buttonTemplate: "button_partner.ListView.Buttons",
});