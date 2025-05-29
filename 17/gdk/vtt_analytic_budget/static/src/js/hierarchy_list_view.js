/** @odoo-module **/

import { registry } from "@web/core/registry";
//import { HierarchyListRenderer } from "./hierarchy_list_renderer";
//import { ListRenderer } from "@web/views/list/list_renderer";

//import { HierarchyTreeModel } from "./hierarchy_list_model";
//import { HierarchyListRenderer } from "./hierarchy_list_renderer";

import { sectionAndNoteFieldOne2Many, SectionAndNoteListRenderer } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";


export class HierarchyListRender extends SectionAndNoteListRenderer {
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

export const HierarchyListView = {
    ...sectionAndNoteFieldOne2Many,
//    component: HierarchyListRender,
//    Model: HierarchyTreeModel,
}
HierarchyListView.component.components.ListRenderer = HierarchyListRender
HierarchyListView.component.components.ListRenderer.template = 'vtt_analytic_budget.hierarchyList';
HierarchyListView.component.components.ListRenderer.recordRowTemplate = 'vtt_analytic_budget.hierarchyList.RecordRow';

registry.category("fields").add("hierarchy_list", HierarchyListView);
