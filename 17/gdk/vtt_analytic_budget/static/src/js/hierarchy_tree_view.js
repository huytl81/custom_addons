/** @odoo-module **/

import { registry } from "@web/core/registry";
import { ListRenderer } from "@web/views/list/list_renderer";
import { listView } from "@web/views/list/list_view";


export class HierarchyTreeRender extends ListRenderer {
    isCategory(record=null) {
        record = record || this.record;
        return record.data.type === 'group';
    }

    getCellClass(column, record) {
        const classNames = super.getCellClass(column, record);
        if (this.isCategory(record)) {
            return `${classNames} o_hierarchy_list_categ_cell`;
        }
        return classNames;
    }

    getRowLevel(record) {
        return record.data['level'];
    }

}

export const HierarchyTreeView = {
    ...listView,
}

HierarchyTreeView.Renderer = HierarchyTreeRender
HierarchyTreeView.Renderer.recordRowTemplate = 'vtt_analytic_budget.hierarchyTree.RecordRow'

registry.category("views").add("hierarchy_tree", HierarchyTreeView);