from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,MissingError


class CancelCaseWizard(models.TransientModel):
    _name = 'cancel.case.wizard'
    _description = 'Canceling Case'

    name = fields.Char('Case NO:', required=True)
    found = fields.Boolean(default=False)
    message = fields.Text(readonly=True, default="Case Does Not Exist!")

    def action_cancel_case(self):
        record = self.env['hospital.case'].search([])
        for i in record:
            if i.c_id == self.name:
                # i.write({'active':False})
                self.write({'found': True})
                i.unlink()
        else:
            if self.found == False:
                raise MissingError(_('Record Not Found!'))
