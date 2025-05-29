/* @odoo-module */

import { DiscussSidebarCategories } from "@mail/discuss/core/web/discuss_sidebar_categories";
import { patch } from "@web/core/utils/patch";
import { cleanTerm } from "@mail/utils/common/format";

patch(DiscussSidebarCategories.prototype, {

    // override the filteredThreads method
    filteredThreads(category) {
        console.log('__________________________________________ abc ___________________________');
        var t = category.threads.filter((thread) => {
            console.log(thread.name);
            console.log(thread.last_interest_dt);
            
            return (
                thread.displayToSelf &&
                (!this.state.quickSearchVal ||
                    cleanTerm(thread.name).includes(cleanTerm(this.state.quickSearchVal)))
            );
        });

        var threads = t.sort((a, b) => {
            return new Date(b.last_interest_dt) - new Date(a.last_interest_dt);
        });

        console.log(category);
        console.log(category.threads);

        return threads;
        // return category.threads.filter((thread) => {
        //     // console.log(thread);
        //     // console.log(category);
        //     // console.log(category.threads);
        //     // console.log(thread.displayToSelf);
        //     // last_interest_dt = thread.last_interest_dt;
        //     console.log(thread.name);
        //     console.log(thread.last_interest_dt);
            
        //     return (
        //         thread.displayToSelf &&
        //         (!this.state.quickSearchVal ||
        //             cleanTerm(thread.name).includes(cleanTerm(this.state.quickSearchVal)))
        //     );
        // });
    }
});
