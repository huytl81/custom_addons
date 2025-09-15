/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class TodoTaskPopupModal extends Component {
    setup() {
        this.dialog = useService("dialog");
        
        // Initialize with default values
        const defaultTask = { 
            name: "", 
            user_id: "", 
            is_done: false, 
            priority: "", 
            deadline: "", 
            color: "#000000" 
        };
        
        // Ensure user_id is a string for the select input
        const taskData = this.props.task 
            ? {
                ...defaultTask,
                ...this.props.task,
                user_id: this.props.task.user_id !== undefined && this.props.task.user_id !== null 
                    ? String(this.props.task.user_id) 
                    : ""
            } 
            : defaultTask;
        
        this.state = useState({
            task: taskData,
            errors: {},
            users: (this.props.users || []).map(user => ({
                ...user,
                id: String(user.id) // Chuyển đổi ID thành chuỗi ngay tại đây
            })),
            priorityOptions: this.props.priorityOptions || []
        });                     
    }

    // Promise version
    // onSave(ev) {
    //     ev.preventDefault();
    //     if (this.validateForm()) {
    //         if (this.props.onSave) {
    //             // Prepare task data with proper type conversion
    //             const taskData = {
    //                 ...this.state.task,
    //                 // Convert empty string to false for user_id
    //                 user_id: this.state.task.user_id || false
    //             };
    //             // Return a promise that resolves when save is complete
    //             return Promise.resolve(this.props.onSave(taskData))
    //                 .then(() => this.props.close());
    //         }
    //         return this.props.close();
    //     }
    //     return Promise.resolve();
    // }

    async onSave(eve){
        if (!this.validateForm()){
            return;
        }
        try {
            if (this.props.onSave()){
            const taskData = {
                    ...this.state.task,
                    user_id: this.state.task.user_id || false
            };
            await this.props.onSave(taskData);
        }
        this.props.close();
        } catch(error){
            console.error("Error saving task:", error);
        }
    }

    async onCancel(ev) {
        await ev.preventDefault();
        this.props.close();
    }

    validateForm() {
        const errors = {};
        if (!this.state.task.name || this.state.task.name.trim() === '') {
            errors.name = 'Task name is required';
        }
        this.state.errors = errors;
        return Object.keys(errors).length === 0;
    }
}

TodoTaskPopupModal.props = {
    title: { type: String, optional: true },
    task: { type: Object, optional: true },
    users: { type: Array, optional: true },
    priorityOptions: { type: Array, optional: true },
    onSave: { type: Function, optional: true },
    close: { type: Function, optional: false },
};

TodoTaskPopupModal.template = "todo_task_popup_modal";
TodoTaskPopupModal.components = {};