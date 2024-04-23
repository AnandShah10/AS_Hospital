from odoo import models, fields, api, _


class DoctorReport(models.AbstractModel):
    _name = 'report.as_hospital.report_doctor_details_with_cases'
    _description = "Doctor Report Abstract Class"

    @api.model
    def _get_report_values(self, docids, data=None):
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>hello')
        print('---------------', docids)
        print('___________________________', data)
        docs = self.env['hospital.doctor'].browse(docids[0])
        print(docs)
        cases = self.env['hospital.case'].search([('doctor', '=', docids[0])])
        case_list = []
        for case in cases:
            vals = {
                'c_id': case.c_id,
                'p_name': case.p_name,
                'p_id': case.p_id,
            }
            print('(((((((((((((', cases)
            case_list.append(vals)
            print('))))))))))))', case_list)
        return {
            'data': data,
            'doc_ids': docids,
            'doc_model': 'hospital.doctor',
            'docs': docs,
            'case_list': case_list
        }
