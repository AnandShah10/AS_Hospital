from odoo import api, fields, models


class PrintCaseWizard(models.TransientModel):
    _name = 'print.case.wizard'
    _description = 'Printing Case'
    # _inherit = 'case.wizard.abstract'

    name = fields.Char('Case ID:', required=True)

    def print_case_wizard_xls_report(self):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', self.read()[0])
        data = {
            'model': 'print.case.wizard', 'form': self.read()[0]
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
            criticality = dict(case._fields['criticality'].selection).get(case.criticality)
            patient = case.c_ids
            if patient:
                gender = dict(patient._fields['gender'].selection).get(patient.gender)
            state = dict(case._fields['state'].selection).get(case.state)
            doctor = case.doctor
            if doctor:
                d_gender = dict(doctor._fields['d_gender'].selection).get(doctor.d_gender)

            print('@@@@@@@@@@@@@@@@@@@@', criticality, state, gender)
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
                'state': state,
            }
            case_list.append(vals)
        data['cases'] = case_list
        print(data)
        return self.env.ref('as_hospital.report_case_wizard_details_xlsx').report_action(self, data=data)

    def print_case_wizard_report(self):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', self.read()[0])
        data = {
            'model': 'print.case.wizard', 'form': self.read()[0]
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
                'state': state,
            }
            case_list.append(vals)
        data['cases'] = case_list
        print(data)
        return self.env.ref('as_hospital.report_case_wizard_details_pdf').report_action(self, data=data)
