from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SearchCaseWizard(models.TransientModel):
    _name = 'search.case.wizard'
    _description = 'Search The Case Records'

    name = fields.Char(string='Case ID')
    c_ids = fields.Many2one('hospital.patient', string='Patient Name')

    def action_search_case(self):
        action = self.env.ref('as_hospital.action_hospital_case').read()[0]
        action['domain'] = ['|', ('c_ids', '=', self.c_ids.id), ('c_id', '=', self.name)]
        return action

    def action_search_by_case_id(self):
        action = self.env.ref('as_hospital.action_hospital_case').read()[0]
        action['domain'] = [('c_id', '=', self.name)]
        return action

    def action_search_by_patient_name(self):
        action = self.env.ref('as_hospital.action_hospital_case').read()[0]
        action['domain'] = [('c_ids', '=', self.c_ids.id)]
        return action

    def print_case_report(self):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', self.read()[0])
        data = {
            'model': 'search.case.wizard', 'form': self.read()[0]
        }
        print('-------------------', data)
        domain = []
        if data['form']['c_ids']:
            selected_patient = data['form']['c_ids'][0]
            print('---------->', selected_patient)
            domain += [('c_ids', '=', selected_patient)]
        if data['form']['name']:
            selected_cases = data['form']['name']
            print('<---------', selected_cases)

            domain += [('c_id', '=', selected_cases)]
        if (not data['form']['name']) and (not data['form']['c_ids']):
            print('h')
            raise UserError(_("Please Enter name or Case ID!"))
        cases = self.env['hospital.case'].search(domain)
        if not cases:
            action = self.env.ref('as_hospital.action_hospital_case')
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': '%s',
                    'type': 'warning',
                    'sticky': True,
                    'links': [{
                        'label': _('Case Record Not Found!'),
                        'url': f'#action={action.id}&model=hospital.case',
                        'target': '_self',
                    }],
                    # 'next': {'type': 'ir.actions.act_window_close'},
                    'next': {
                        'context': self.env.context,
                        # 'domain': [('id', 'in', .ids)],
                        'name': _('Redirecting to Case'),
                        'res_model': 'hospital.case',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'list',
                        'views': [[False, 'list'], [False, 'form']],
                    },
                }
            }
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
