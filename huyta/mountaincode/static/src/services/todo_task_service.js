/** @odoo-module **/

import { registry } from "@web/core/registry";

const serviceRegistry = registry.category("services");

export const todoTaskService = {
    dependencies: ["orm"],

    start(env, { orm }) {
        const model = "todo.task"
        // debugger;
        // console.log(this.model);
        return {
            /**
             * Get all todo tasks
             * @returns {Promise<Array>} List of todo tasks
             */

            async getAllTasksService() {
                const tasks = await orm.searchRead(
                    model,
                    [],
                    ["id","name", "user_id", "deadline", "is_done", "color", "priority"]
                );

                return await Promise.all(tasks.map(t => ({
                    id: t.id,
                    user_id: t.user_id ? t.user_id[0] : false, // Sửa ở đây: lấy ID thay vì tên
                    //user_id: t.user_id ? t.user_id[1] : "",  // chỉ lấy tên
                    //user_id: t.user_id ? { id: t.user_id[0], name: t.user_id[1] } : false, // Sửa: Lấy cả ID và tên
                    name: t.name || "",                      // fallback nếu null
                    deadline: t.deadline || "",
                    priority: t.priority || "",
                    is_done: t.is_done || "",
                    color: t.color || ""
                })));
                // return await orm.searchRead(this.model,[],["name", "user_id", "deadline", "is_done", "color", "priority"]);
            },

            /**
             * Create a new todo task
             * @param {Object} taskData - Task data
             * @returns {Promise<number>} ID of the created task
             */
            async createTaskService(task) {
                return await orm.create(model, [task]);
            },

            /**
             * Update an existing todo task
             * @param {number} taskId - ID of the task to update
             * @param {Object} fields - Fields to update
             * @returns {Promise<boolean>} True if successful
             */
            async updateTaskService(taskId, fields) {
                return await orm.write(model, [taskId], fields);
            },

            /**
             * Delete a todo task
             * @param {number} taskId - ID of the task to delete
             * @returns {Promise<boolean>} True if successful
             */
            async deleteTaskService(taskId) {
                return await orm.unlink(model, [taskId]);
            },

            /**
             * Search todo task
             * @param {text} text - name of the task to search
             * @returns {Promise<Array>} List of todo tasks
             */
            async searchTasksService(text) {
                return await orm.searchRead(model, [['name','ilike',text]], ["name", "color", "is_done", "user_id", "deadline", "priority"])
            },
        };
    },
};

// Register the service
serviceRegistry.add("todo.task.service", todoTaskService);
