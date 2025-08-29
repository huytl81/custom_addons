/** @odoo-module **/

import { registry } from "@web/core/registry";

const serviceRegistry = registry.category("services");

export const userService = {
    dependencies: ["orm"],

    start(env, { orm }) {
        const model = "res.users";
        return {
            /**
             * Get all active users
             * @returns {Promise<Array>} List of active users
             */
            async getAllUsersService() {
                try {
                    const users = await orm.searchRead(
                        model,
                        [['active', '=', true]], // Only get active users
                        ["id", "name", "login", "email"]
                    );

                    return users.map(user => ({
                        id: user.id,
                        name: user.name || "",
                        login: user.login || "",
                        email: user.email || ""
                    }));
                } catch (error) {
                    console.error("Error fetching users:", error);
                    return [];
                }
            },

            /**
             * Get user by ID
             * @param {number} userId - ID of the user to fetch
             * @returns {Promise<Object>} User data
             */
            async getUserById(userId) {
                try {
                    const [user] = await orm.searchRead(
                        model,
                        [['id', '=', userId]],
                        ["id", "name", "login", "email"]
                    );
                    return user || null;
                } catch (error) {
                    console.error(`Error fetching user ${userId}:`, error);
                    return null;
                }
            },

            /**
             * Search users by name or email
             * @param {string} searchTerm - Term to search for in name or email
             * @returns {Promise<Array>} List of matching users
             */
            async searchUsers(searchTerm) {
                try {
                    return await orm.searchRead(
                        model,
                        [
                            '|',
                            ['name', 'ilike', searchTerm],
                            ['email', 'ilike', searchTerm]
                        ],
                        ["id", "name", "email"]
                    );
                } catch (error) {
                    console.error("Error searching users:", error);
                    return [];
                }
            }
        };
    },
};

// Register the service
serviceRegistry.add("user.service", userService);
