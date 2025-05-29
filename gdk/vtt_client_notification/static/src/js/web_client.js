odoo.define('web_notify.WebClient', function (require) {
    "use strict";

    var WebClient = require('web.WebClient');
    var base_bus = require('bus.Longpolling');
    var session = require('web.session');
    require('bus.BusService');


    WebClient.include({
        show_application: function () {
            var res = this._super();
            this.start_polling();
            return res;
        },
        _notification_click: function(params) {
//            this.action_manager.doAction(params.action, params.options)
            console.log(params);
            this.do_action({
                    name: params.modelName,
                    type: params.type,
                    res_model: params.resModel,
                    view_mode: params.viewMode,
                    views: params.views,
                    target: params.target,
                    res_id: params.resId,
                    flags: params.flags,
                    context: params.context,
                    url: params.url,
                });
//            if (params.type == 'ir.actions.act_window') {
//                this.do_action({
//                    name: params.modelName,
//                    type: params.type,
//                    res_model: params.resModel,
//                    view_mode: params.viewMode,
//                    views: params.views,
//                    target: params.target,
//                    res_id: params.resId,
//                    flags: params.flags,
//                    context: params.context,
//                });
//            }
//
//            if (params.type == 'ir.actions.act_url') {
//                this.do_action({
//                    type: params.type,
//                    url: params.url,
//                    target: params.target,
//                });
//            }
        },
        start_polling: function () {
            this.channel_success = 'notify_success_' + session.uid;
            this.channel_danger = 'notify_danger_' + session.uid;
            this.channel_warning = 'notify_warning_' + session.uid;
            this.channel_info = 'notify_info_' + session.uid;
            this.channel_default = 'notify_default_' + session.uid;
            this.all_channels = [
                this.channel_success,
                this.channel_danger,
                this.channel_warning,
                this.channel_info,
                this.channel_default,
            ];
            this.call('bus_service', 'addChannel', this.channel_success);
            this.call('bus_service', 'addChannel', this.channel_danger);
            this.call('bus_service', 'addChannel', this.channel_warning);
            this.call('bus_service', 'addChannel', this.channel_info);
            this.call('bus_service', 'addChannel', this.channel_default);
            this.call(
                'bus_service', 'on', 'notification',
                this, this.bus_notification);
            this.call('bus_service', 'startPolling');
        },
        bus_notification: function (notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                if (
                    self.all_channels != null &&
                    self.all_channels.indexOf(channel) > -1
                ) {
                    self.on_message(message);
                }
            });
        },
        on_message: function (message) {
            return this.call(
                'notification', 'notify', {
                    type: message.type,
                    title: message.title,
                    message: message.message,
                    sticky: message.sticky,
                    className: message.className,
                    buttons: _.map(message.buttons, function(button) {
                        button.click = this._notification_click.bind(this, {
//                            'action': button.action,
                            'options': button.options,
                            'button': button,
                            'message': message,
                            'resId': button.resId,
                            'type': button.type,
                            'resModel': button.resModel,
                            'views': button.views,
                            'viewMode': button.viewMode,
                            'target': button.target,
                            'flags': button.flags,
                            'context': button.context,
                            'modelName': button.modelName,
                            'url': button.url
                        });
                        return button;
                    }, this),
                }
            );
        },
    });

});
