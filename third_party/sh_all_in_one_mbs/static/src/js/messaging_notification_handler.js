/** @odoo-module **/

import { registerInstancePatchModel } from '@mail/model/model_core';

registerInstancePatchModel('mail.messaging_notification_handler', 'sh_all_in_one_mbs/static/src/js/messaging_notification_handler.js', {

	
    //----------------------------------------------------------------------
    // Private
    //----------------------------------------------------------------------

    /**
     * @override
     * To play sound when notification show and notification coming from 
     * barcode App - sh_all_in_one_mbs
     */	
	
    /**
     * @private
     * @param {Object} data
     * @param {string} [data.info]
     * @param {string} [data.type]
     */
    async _handleNotificationPartner(data) {   
        //for play sound start here
        //if message has SH_BARCODE_MOBILE_SUCCESS_
        var str_msg = data.message.match("SH_BARCODE_MOBILE_SUCCESS_");
        if (str_msg) {
            //remove SH_BARCODE_MOBILE_SUCCESS_ from message and make valid message
            data.message = data.message.replace("SH_BARCODE_MOBILE_SUCCESS_", "");

            //play sound
            var src = "/sh_all_in_one_mbs/static/src/sounds/picked.wav";
            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
        }
        //for play sound ends here

        //for play sound start here
        //if message has SH_BARCODE_MOBILE_FAIL_
        var str_msg = data.message.match("SH_BARCODE_MOBILE_FAIL_");
        if (str_msg) {
            //remove SH_BARCODE_MOBILE_FAIL_ from message and make valid message
            data.message = data.message.replace("SH_BARCODE_MOBILE_FAIL_", "");

            //play sound
            var src = "/sh_all_in_one_mbs/static/src/sounds/error.wav";
            $("body").append('<audio src="' + src + '" autoplay="true"></audio>');
        }
        //for play sound ends here    	
    	
    	
        return this._super(data);
    	
    },
    
});
