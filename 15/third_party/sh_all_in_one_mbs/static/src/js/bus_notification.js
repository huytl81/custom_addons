odoo.define('sh_sale_barcode_mobile.notification_manager', function (require) {
    "use strict";

    var AbstractService = require('web.AbstractService');
    var core = require("web.core");

    var sh_sale_barcode_mobile_notification_manager = AbstractService.extend({
        dependencies: ['bus_service'],

        /**
         * @override
         */
        start: function () {
            this._super.apply(this, arguments);
            this.call('bus_service', 'onNotification', this, this._onNotification);
        },

        _onNotification: function (notifications) {
            for (const { payload, type } of notifications) {
            	
            	// -------------------------------
                // MBS app wise conding here
                // -------------------------------
                /**
                 * -----------------------------------------
                 * Sale
                 * -----------------------------------------
                 */
            	
            	if (type === "sh_sale_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_sale_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }

                /**
                 * -----------------------------------------
                 * Purchase
                 * -----------------------------------------
                 */
            	if (type === "sh_purchase_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_purchase_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }

                /**
                 * -----------------------------------------
                 * Product
                 * -----------------------------------------
                 */
                
                if (type === "sh_product_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_product_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }
                /**
                 * -----------------------------------------
                 * Invoice
                 * -----------------------------------------
                 */
                
                if (type === "sh_invoice_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_invoice_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message){
                    	var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                        	payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  
                        
                    }
                    
                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }

                /**
                 * -----------------------------------------
                 * Inventory Stock Picking
                 * -----------------------------------------
                 */
                
                if (type === "sh_inventory_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message) {
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  

                    }

                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_inventory_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message) {
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  

                    }

                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }

                /**
                 * -----------------------------------------
                 * BOM
                 * -----------------------------------------
                 */
                
                if (type === "sh_bom_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message) {
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  

                    }

                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_bom_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message) {
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  

                    }

                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }
                
                /**
                 * -----------------------------------------
                 * Inventory Adjustment
                 * -----------------------------------------
                 */
                if (type === "sh_inventory_adjustment_barcode_mobile_notification_info") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message) {
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  

                    }

                    this.displayNotification({ title: payload.title, message: payload.message, type: 'info', sticky: false });
                }
                if (type === "sh_inventory_adjustment_barcode_mobile_notification_danger") {
                    //for play sound start here
                    //if message has SH_BARCODE_MOBILE_SUCCESS_
                    if (payload.message) {
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_SUCCESS_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here

                        //for play sound start here
                        //if message has SH_BARCODE_MOBILE_FAIL_
                        var str_msg = payload.message.match("SH_BARCODE_MOBILE_FAIL_");
                        if (str_msg) {
                            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
                            payload.message = payload.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

                            //play sound
                            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
                            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
                        }
                        //for play sound ends here  

                    }

                    this.displayNotification({ title: payload.title, message: payload.message, type: 'danger', sticky: false });
                }
                
                
            	// -------------------------------
                // MBS app wise conding here
                // -------------------------------


            }
        }

    });

    core.serviceRegistry.add('sh_sale_barcode_mobile_notification_manager', sh_sale_barcode_mobile_notification_manager);

    return sh_sale_barcode_mobile_notification_manager;

});