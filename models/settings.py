from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import date, datetime


# patient class
class HospitalSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Hospital Settings'

    note = fields.Char(string="Notes:")

    # config_parameter

    def set_values(self):
        res = super(HospitalSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('as_hospital.note', self.note)

    @api.model
    def get_values(self):
        res = super(HospitalSettings, self).get_values()
        sudo = self.env['ir.config_parameter'].sudo()
        notes = sudo.get_param('as_hospital.note')
        res.update(
            note=notes
        )
        return res
