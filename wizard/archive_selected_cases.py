from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ArchiveCasesWizard(models.TransientModel):
    _name = 'archive.cases.wizard'
    _description = 'Canceling Case'

    name = fields.Many2many('hospital.case',string='Cases:', required=True)
    found = fields.Boolean(default=False)
    message = fields.Char(readonly=True, default="Case Does Not Exist!")


    def action_archive_cases(self):
        record = self.env['hospital.case'].search([])
        for i in record:
            if i.id in self.name.ids:
                i.write({'active': False})
                self.write({'found': True})
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

    @api.model
    def default_get(self, fields):
        res = super(ArchiveCasesWizard, self).default_get(fields)
        # Get the default_ids from context
        if self.env.context.get('default_ids'):
            case_ids = self.env.context['default_ids']
            res.update({'name': [(6, 0, case_ids)]})
        return res