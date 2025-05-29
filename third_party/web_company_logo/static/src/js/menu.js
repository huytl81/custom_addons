odoo.define('web_company_logo.Menu', function (require) {
    'use strict';

    var session = require('web.session');
    var Menu = require('web.Menu');

    Menu.include({
        /**
        * @override
        */
        start: function (parent, options) {
            this._super.apply(this, arguments);

            // current url, <domain_name>:<port_number>
            var url = window.location.origin;

            // company id from the session
            var companyId = session.company_id;

            // use ajax to check if the company has a logo.
            // if there is no logo, remove the anchor, else
            // use the company's logo as the img src
            $.ajax({
                type: 'GET',
                data: {'company_id': companyId},
                url: `${url}/check_company_logo`,
                success: function (result) {
                    console.log('Inside the success function');
                    var result = JSON.parse(result);
                    if (result.has_logo == true) {
                        $('#company-logo')[0].src = `${url}/web/image?model=res.company&id=${companyId}&field=logo`;
                    }
                    else {
                        $('#company-logo-link')[0].remove();
                    }
                },
                error: function (xhr, ajaxOptions, thrownError) {
                    console.log('Error encountered');
                },
            });
        },
    });
});
