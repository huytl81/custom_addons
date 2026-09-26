import { patch } from '@web/core/utils/patch';

import {ListArchParser} from '@web/views/list/list_arch_parser';

patch(ListArchParser.prototype, {
    parse(xmlDoc, models, modelName) {
        const res = super.parse(xmlDoc, models, modelName);
        res?.columns.forEach(column => {
            if (column.type === 'field' && column.hasLabel && column.attrs.icon) {
                column.labelIcon = column.attrs.icon;
                column.hasLabel = false;
            }
        });
        return res;
    },
});
