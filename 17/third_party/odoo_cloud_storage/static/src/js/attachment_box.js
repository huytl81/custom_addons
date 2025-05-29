/** @odoo-module **/
var AttachmentBox = require('mail.AttachmentBox');
import { jsonrpc } from "@web/core/network/rpc_service";

var test = AttachmentBox.include({
	_uploadAtatchmentToCloud: function (ev) {
		varattachment_id = $(ev.currentTarget).data('id');
		jsonrpc('/odoo_cloud_storage/action_attachment_cloud/export',
			{ "attachment_id": attachment_id }).then(function (res) {
				if (res) {
					alert("Attachment Successfully Exported To Cloud");
				}
				else {
					alert('Attachment Not Exported Succesfully To Cloud');
				}
			});
	},
});
