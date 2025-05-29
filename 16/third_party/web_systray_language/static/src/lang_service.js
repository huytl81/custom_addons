/** @odoo-module **/

import {registry} from '@web/core/registry';

const langService = {
    dependencies: ['orm'],
    start(env, {orm}) {

        async function getLangs() {
            return await orm.searchRead(
                'res.lang', [],
                [
                    'name',
                    'code',
                    'iso_code',
                    'url_code',
                ]
            )
        }

        return {
            getLangs,
        }
    }
};

registry.category('services').add('lang', langService);