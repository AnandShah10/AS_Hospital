from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ArchiveCaseWizard(models.TransientModel):
    _name = 'archive.case.wizard'
    _description = 'Canceling Case'
    # _inherit = 'case.wizard.abstract'

    name = fields.Char('Case NO:', required=True)
    found = fields.Boolean(default=False)
    message = fields.Char(readonly=True, default="Case Does Not Exist!")


    def action_archive_case(self):
        record = self.env['hospital.case'].search([])
        for i in record:
            if i.c_id == self.name:
                i.write({'active': False})
                self.write({'found': True})
                break
        else:
            if not self.found:
                return {
                    'name': 'view_archive_case_not_found_form',
                    'type': 'ir.actions.act_window',
                    'res_model': 'archive.case.wizard',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'target': 'new'
                }


class CaseWizardAbstract(models.AbstractModel):
    _name = 'case.wizard.abstract'
    _description = 'Archive case Abstract Model'

    message = fields.Text(readonly=True, default="Case Does Not Exist!")
