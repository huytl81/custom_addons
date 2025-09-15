/** @odoo-module **/

import { Component, useRef, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { TodoTaskPopupModal } from "./todo_task_popup_modal";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

const actionRegistry = registry.category("actions");

// Using Service Layer approach
export class TodoTaskAction extends Component {
    setup() {
        super.setup();
        // my custom services
        this.taskService = useService("todo.task.service");
        this.userService = useService("user.service");
        // orm service
        this.orm = useService("orm");
        // dialog service
        this.dialog = useService("dialog");

        this.state = useState({
            task: { name: "", priority: "", is_done: false, user_id: "", deadline: "" , color: ""},
            taskList: [],
            users: [],
            search: ''
        });

        this.searchInput = useRef("searchInput");

        this.modal = null;

        onWillStart(async () => {
            // Đảm bảo lấy danh sách người dùng trước
            await this.getAllUsers();
            // Sau đó mới lấy danh sách công việc
            await this.getAllTasks();

            const fields = await this.env.services.orm.call("todo.task", "fields_get", [["priority"], ["selection"]]);
            this.state.priorityOptions = (fields.priority.selection || []).map(([value, label]) => ({value,label}));
        })
    }

    async getAllUsers() {
        try{
            this.state.users = await this.userService.getAllUsersService() || [];
        }catch (error){
            console.error("Error fetching users:", error);
            this.state.users = [];
        }
    }

    async getAllTasks() {
        try {
            this.state.taskList = await this.taskService.getAllTasksService() || [];
        } catch (error) {
            console.error("Error fetching tasks:", error);
            this.state.taskList = [];
        }
    }

    getUserName(userId) {
        const user = this.state.users.find(user => user.id === userId);
        return user ? user.name : '';
    }

    async addTask() {
        this.resetForm();
        // if use dialog modal useService("dialog") else comment out this line below;
        this.openTaskForm();
    }

    async editTask(task) {
        // Ensure user_id is properly handled when editing
        this.state.task = {
            ...task,
            user_id: task.user_id || ""  // Convert to empty string if false
        };
        this.openTaskForm();
    }

    openTaskForm() {
        // Create a deep copy of the task to avoid reference issues
        const taskData = JSON.parse(JSON.stringify({
            ...this.state.task,
            // Ensure user_id is a string for the select input
            user_id: this.state.task.user_id ? String(this.state.task.user_id) : ""
        }));
        
        this.dialog.add(TodoTaskPopupModal, {
            title: this.state.task.id ? 'Edit Task' : 'New Task',
            task: taskData,
            users: this.state.users,
            priorityOptions: this.state.priorityOptions,
            onSave: async (taskData) => {
                // Convert back to number when saving
                this.state.task = { 
                    ...taskData,
                    user_id: taskData.user_id ? parseInt(taskData.user_id) : false
                };
                await this.saveTask();
            }
        }, {
            onClose: () => {
                // Reset the task after dialog is closed
                this.state.task = { name: "", color: "", user_id: "", is_done: false, priority: "", deadline: "" };
            }
        });
    }

    async saveTask() {
        try {
            // Prepare task data with proper user_id handling
            const taskData = {
                ...this.state.task,
                user_id: this.state.task.user_id || false  // Ensure user_id is false if empty
            };

            if (taskData.id === undefined || taskData.id === null) {
                // Create new task
                await this.taskService.createTaskService(taskData);
            } else {
                // Update existing task
                await this.taskService.updateTaskService(taskData.id, taskData);
            }
            // close dialog if use dialog modal useService("dialog");
            // or use jQuery: $("#taskModal").modal('hide');
            this.dialog.closeAll();

            await this.getAllTasks();  // Refresh the task list
            await this.resetForm();

        } catch (error) {
            console.error("Error saving task:", error);
        }
    }

    async confirmDialog(title, message) {
        return new Promise((resolve) => {
            this.dialog.add(ConfirmationDialog, {
                title: title,
                body: message,
                confirm: () => resolve(true),
                cancel: () => resolve(false)
            });
        });
    }

    // Then use it like this:
    async   deleteTask(task) {
        try {
            const confirmed = await this.confirmDialog("Confirm Deletion",`Are you sure you want to delete task "${task.name}"?`);
            if (confirmed) {
                await this.taskService.deleteTaskService(task.id);
                await this.getAllTasks();
            }
        } catch (error) {
            console.error("Error deleting task:", error);
        }
    }

    async updateColor(el, task){
        try{
            await this.taskService.updateTaskService(task.id, {color: el.target.value});
            await this.getAllTasks();
        }catch(error){
            console.error("Error updating task color:", error);
        }
    }

    async updateComplete(el, task){
        try{
            await this.taskService.updateTaskService(task.id, {is_done: el.target.checked});
            await this.getAllTasks();
        }catch(error){
            console.error("Error updating task complete:", error);
        }
    }

    async searchTasks(){
        try{
            const text = this.searchInput.el.value;
            this.state.taskList = await this.taskService.searchTasksService(text) || [];
        }catch(error){
            console.error("Error searching tasks:", error);
            this.state.taskList = [];
        }
    }

    resetForm() {
        this.state.task = { name: "", color: "", user_id: "", is_done: false, priority: "", deadline: "" };
    }

}

TodoTaskAction.template = "todo_task_action";

// Đăng ký action để gọi từ XML
actionRegistry.add("todo_task_action", TodoTaskAction);
