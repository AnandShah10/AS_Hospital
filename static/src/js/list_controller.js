/**@odoo-module**/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ListController.prototype,{
     setup() {
        super.setup();
        this.action = useService("action");
    },
    async onClick()
    {
        const context = this.model.root.selection.map((record) => record.resId);
        console.log('context Ids',context);
        await this.action.doAction({
            type : 'ir.actions.act_window',
            name : 'Archive Cases',
            view_mode : 'form',
            target : 'new',
            res_model : 'archive.cases.wizard',
            views : [[false,'form']],
            context:'{"default_ids":['+context+']}'
        })
    }
});