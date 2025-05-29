/** @odoo-module **/
import { renderToElement } from "@web/core/utils/render";
import { Chatter } from "@mail/core/web/chatter";
import { jsonrpc } from "@web/core/network/rpc_service";
import { registry } from "@web/core/registry";

export class ChatterBox extends Chatter {

    setup() {
        var res_model = this.record.model;
        var res_id = this.record.data.id;
        var self = this;
        jsonrpc('/odoo_cloud_storage/get_models', {
        }).then(function (res) {
            if(jQuery.inArray(res_model,res) > -1){
                self.$('.o_topbar_right_area').before(renderToElement('cloud.chatter.cloud.Attachment.Button', {
                    res_id: res_id,
                    res_model: res_model
            }));
        }
        });
        return this.setup(this, arguments);
    }

    _render(def) {
        var self = this;
        var def = this._super.apply(this, arguments).then(function (data) {
            $("#id_res").val(self.record.data.id);
        });
        return def;
    }

    _onOpenCloudFolder(ev) {
        var id = $("#id_res").val();
        var model = $("#id_model").val();
        var url = '/odoo_cloud_storage/open_folder/';
        url += model + '/' + id;
        jsonrpc(url, {
        }).then(function (res) {
            var status = res.status
            var map_id = res.map_id
            if(status){
                window.open(res.url, '_blank');
            }
            else if(map_id){
                alert("Message:Not able To Open Folder In Cloud");
            }
            else{
                alert('Message:This Record Has Not Mapped With Any Of Files To Cloud');
            }
        });
    }
};

registry.category("views").add('ChatterBox',ChatterBox)
