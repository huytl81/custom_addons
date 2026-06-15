import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

import * as M2OField from "@web/views/fields/many2one/many2one_field";

const originalExtractM2OFieldProps = M2OField.extractM2OFieldProps;
const originalbuildM2OFieldDescription = M2OField.buildM2OFieldDescription;

const patchedExtractM2OFieldProps = function (staticInfo, dynamicInfo) {
    const result = originalExtractM2OFieldProps(staticInfo, dynamicInfo);
    if (
        session.disable_quick_create &&
        staticInfo.options.no_quick_create == undefined
    ) {
        result.canQuickCreate = false;
    }
    return result;
};

const patchedbuildM2OFieldDescription = function (component) {
    const result = originalbuildM2OFieldDescription(component);
    result.extractProps = patchedExtractM2OFieldProps;
    return result;
};

M2OField.extractM2OFieldProps = patchedExtractM2OFieldProps;
M2OField.buildM2OFieldDescription = patchedbuildM2OFieldDescription;

patch(registry.category("fields").get('many2one'), {
    extractProps({ options }) {
        let result = super.extractProps(...arguments);
        if (
            session.disable_quick_create &&
            options.no_quick_create == undefined
        ) {
            result.canQuickCreate = false;
        }
        return result;
    }
});
