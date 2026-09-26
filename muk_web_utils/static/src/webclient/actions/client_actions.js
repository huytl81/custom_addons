import { registry } from '@web/core/registry';

export async function multiAction(env, action) {
    const params = action.params || {};
    const actions = params.actions || [];
    for (const action of actions) {
        await env.services.action.doAction(action);
    }
}

registry.category('actions').add('multi_actions', multiAction);