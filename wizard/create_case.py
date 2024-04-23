from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import date, datetime


# patient class
class CreateCaseWizard(models.TransientModel):
    _name = "create.case.wizard"
    _description = 'Creating a Case'

    name = fields.Char(string='Case ID:', required=True,
                       copy=False, readonly=True,
                       default=lambda self: _('New'), index=True,
                       )
    d_id = fields.Many2one('hospital.doctor', string='doctor name')
    admission_date = fields.Date(string='Admission date')
    prev = fields.Text(string="Previous illness")
    curr = fields.Text(string="Current illness")
    c_ids = fields.Many2one("hospital.patient", string="Patient:")
    criticality = fields.Selection([('undetermined', 'Undetermined'),
                                    ('serious', 'Serious'),
                                    ('good', 'Good'), ('fair', 'Fair'), ('critical', 'Critical'),
                                    ('dead', 'Dead'), ('grave', 'Grave'),
                                    ('extremely_critical', 'Extremely critical'),
                                    ('extremely_critical_stable', 'Extremely critical But Stable'),
                                    ('serious_stable', 'Serious But Stable'),
                                    ('satisfactory', 'Satisfactory')],
                                   string='Criticality',
                                   required=True)

    def action_create_case(self):
        # self.env['hospital.check'].write(name)
        info = {'c_id': self.name, 'doctor': self.d_id.id, 'criticality': self.criticality,
                'admission_date': self.admission_date,
                'curr_illness': self.curr, 'prev_illness': self.prev, 'c_ids': self.c_ids.id}
        appointment_rec = self.env['hospital.case'].create(info)

        return {
            'name': 'case',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hospital.case',
            'res_id': appointment_rec.id,
            'target': 'new',
        }

    # Case ID Sequence
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.case.sequence') or _('New')
        res = super(CreateCaseWizard, self).create(vals)
        return res

    def print_case_report(self):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', self.read()[0])
        data = {
            'model': 'create.case.wizard', 'form': self.read()[0]
        }
        print('-------------------', data)
        if data['form']['name']:
            selected_cases = data['form']['name']
            print('<---------', selected_cases)
            cases = self.env['hospital.case'].search([('c_id', '=', selected_cases)])
        else:
            print('h')
            cases = self.env['hospital.case'].search([])
        print(cases)

        case_list = []
        for case in cases:
            for case in cases:
                criticality = dict(case._fields['criticality'].selection).get(case.criticality)
                patient = case.c_ids
                if patient:
                    gender = dict(patient._fields['gender'].selection).get(patient.gender)
                doctor = case.doctor
                if doctor:
                    d_gender = dict(doctor._fields['d_gender'].selection).get(doctor.d_gender)
                state = dict(case._fields['state'].selection).get(case.state)

            vals = {
                'c_id': case.c_id,
                'p_name': case.p_name,
                'p_id': case.p_id,
                'criticality': criticality,
                'p_age': case.p_age,
                'p_gender': gender,
                'p_is_child': case.p_is_child,
                # 'p_image': case.p_image,
                'p_blood_group': case.p_blood_group,
                'p_mob': case.p_mob,
                'doctor': case.doctor.doctor,
                'd_id': case.d_id,
                'd_email': case.d_email,
                'doc_mob': case.doc_mob,
                'd_gender': d_gender,
                'admission_date': case.admission_date,
                'discharge_date': case.discharge_date,
                'is_admitted': case.is_admitted,
                'final_total': case.final_total,
                'room_type': case.room_type,
                'c_notes': case.c_notes,
                'fees': case.fees,
                'fee_tax': case.fee_tax,
                'total_fee': case.total_fee,
                'room_price': case.room_price,
                'total_charge': case.total_charge,
                'room_tax': case.room_tax,
                'total_room_charge': case.total_room_charge,
                'prev_illness': case.prev_illness,
                'curr_illness': case.curr_illness,
                'm_notes': case.m_notes,
                'a_ids': case.a_ids,
                'prescription_ids': case.prescription_ids,
                'progress_rate': case.progress_rate,
                'total_price': case.total_price,
                'tax': case.tax,
                'tax_total': case.tax_total,
                'duration': case.duration,
            }
            case_list.append(vals)
        data['cases'] = case_list
        print(data)
        return self.env.ref('as_hospital.report_case_wizard_details_pdf').report_action(self, data=data)
