from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
from datetime import *


# Prescription Class
class PatientPrescription(models.Model):
    _name = "patient.prescription"
    _description = "Patient Prescription"
    # _inherit = 'mail.thread'
    name = fields.Char(string="Medication", translate=True)
    quant = fields.Integer(string="Quantity")
    price = fields.Float(string="Price")
    currency = fields.Many2one('res.currency', string="Currency",
                               default=lambda self: self.env['res.currency'].search(
                                   [('name', '=', 'INR')]).id
                               , invisible=True)
    total = fields.Monetary(string="Total", default=0, currency_field='currency',
                            compute="calc_total",
                            readonly=True, store=True)
    c_id = fields.Many2one("hospital.case", ondelete='cascade')

    # To calculate total price of medicine
    @api.depends('total', 'price', 'quant')
    def calc_total(self):
        for i in self:
            if i.price:
                i.total += i.price * i.quant

    # To delete empty record
    @api.constrains('price', 'quant', 'name')
    def check_empty_val(self):
        for i in self:
            if (i.price == 0.00 or i.quant == 0 or (not i.name)):
                i.unlink()

