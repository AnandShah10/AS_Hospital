from odoo import models, fields, api, _


class CaseXlsReport(models.AbstractModel):
    _name = 'report.as_hospital.report_case_xls_details'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Case Excel Report Abstract Class"

    def generate_xlsx_report(self, workbook, data, lines):
        print('------->', lines, data)
        format1 = workbook.add_format({'bold': True, 'align': 'center'})
        format2 = workbook.add_format({'bold': True, 'align': 'center'})

        sheet = workbook.add_worksheet('Case Excel Report')
        row = 0
        col = 0
        sheet.write(row, col, 'Case ID:', format1)
        sheet.write(row, col + 1, 'Patient Name', format1)
        sheet.write(row, col + 2, 'Patient ID', format1)
        sheet.write(row, col + 3, 'Gender', format1)
        sheet.write(row, col + 4, 'Age', format1)
        sheet.write(row, col + 5, 'Blood Group', format1)
        sheet.write(row, col + 6, 'Criticality', format1)
        sheet.write(row, col + 7, 'State', format1)
        sheet.write(row, col + 8, 'Current Illness', format1)
        sheet.write(row, col + 9, 'Previous Illness', format1)
        sheet.write(row, col + 10, 'Mobile No', format1)
        sheet.write(row, col + 11, 'Doctor Name', format1)
        sheet.write(row, col + 12, 'Doctor ID', format1)
        sheet.write(row, col + 13, 'Doctor Gender', format1)
        sheet.write(row, col + 14, 'Doctor Mobile No', format1)
        sheet.write(row, col + 15, 'Case Fees(With Tax)', format1)
        sheet.write(row, col + 16, 'Was Admitted', format1)
        sheet.write(row, col + 17, 'Admission Date', format1)
        sheet.write(row, col + 18, 'Discharge Date', format1)
        sheet.write(row, col + 19, 'Room', format1)
        sheet.write(row, col + 20, 'Duration', format1)
        sheet.write(row, col + 21, 'Room Charge (With Tax)', format1)
        sheet.write(row, col + 22, 'Medicine Total Cost', format1)
        sheet.write(row, col + 23, 'Total Cost', format1)
        sheet.write(row, col + 24, 'Progress Rate', format1)
        sheet.write(row, col + 25, 'Case Notes', format1)
        sheet.write(row, col + 26, 'Medical Notes', format1)


        sheet.set_column('A:B', 15)
        sheet.set_column('C:F', 20)
        sheet.set_column('G:AA', 40)


        for case in lines:
            row += 1
            sheet.write(row, col, case['c_id'], format2)
            sheet.write(row, col + 1, case['p_name'], format2)
            sheet.write(row, col + 2, case['p_id'], format2)
            sheet.write(row, col + 3, case['p_gender'], format2)
            sheet.write(row, col + 4, case['p_age'], format2)
            sheet.write(row, col + 5, case['p_blood_group'], format2)
            sheet.write(row, col + 6, case['criticality'], format2)
            sheet.write(row, col + 7, case['state'], format2)
            sheet.write(row, col + 8, case['curr_illness'], format2)
            sheet.write(row, col + 9, case['prev_illness'], format2)
            sheet.write(row, col + 10, case['p_mob'], format2)
            sheet.write(row, col + 11, case['doctor'].doctor, format2)
            sheet.write(row, col + 12, case['d_id'], format2)
            sheet.write(row, col + 13, case['d_gender'], format2)
            sheet.write(row, col + 14, case['doc_mob'], format2)
            sheet.write(row, col + 15, case['total_fee'], format2)
            sheet.write(row, col + 16, bool(case['is_admitted']), format2)
            sheet.write(row, col + 17, case['admission_date'], format2)
            sheet.write(row, col + 18, case['discharge_date'], format2)
            sheet.write(row, col + 19, case['room_type'], format2)
            sheet.write(row, col + 20, case['duration'], format2)
            sheet.write(row, col + 21, case['total_room_charge'], format2)
            sheet.write(row, col + 22, case['tax_total'], format2)
            sheet.write(row, col + 23, case['final_total'], format2)
            sheet.write(row, col + 24, case['progress_rate'], format2)
            sheet.write(row, col + 25, case['c_notes'], format2)
            sheet.write(row, col + 26, case['m_notes'], format2)




class CaseWizardXlsReport(models.AbstractModel):
    _name = 'report.as_hospital.report_case_wizard_details_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Case Excel Report Abstract Class For Wizard"

    def generate_xlsx_report(self, workbook, data, lines):
        print('------->', lines, data)
        format1 = workbook.add_format({'bold': True, 'align': 'center'})
        format2 = workbook.add_format({'bold': True, 'align': 'center'})

        sheet = workbook.add_worksheet('Case Excel Report')
        row = 0
        col = 0
        sheet.write(row, col, 'Case ID:', format1)
        sheet.write(row, col + 1, 'Patient Name', format1)
        sheet.write(row, col + 2, 'Patient ID', format1)
        sheet.write(row, col + 3, 'Gender', format1)
        sheet.write(row, col + 4, 'Age', format1)
        sheet.write(row, col + 5, 'Blood Group', format1)
        sheet.write(row, col + 6, 'Criticality', format1)
        sheet.write(row, col + 7, 'State', format1)
        sheet.write(row, col + 8, 'Current Illness', format1)
        sheet.write(row, col + 9, 'Previous Illness', format1)
        sheet.write(row, col + 10, 'Mobile No', format1)
        sheet.write(row, col + 11, 'Doctor Name', format1)
        sheet.write(row, col + 12, 'Doctor ID', format1)
        sheet.write(row, col + 13, 'Doctor Gender', format1)
        sheet.write(row, col + 14, 'Doctor Mobile No', format1)
        sheet.write(row, col + 15, 'Case Fees(With Tax)', format1)
        sheet.write(row, col + 16, 'Was Admitted', format1)
        sheet.write(row, col + 17, 'Admission Date', format1)
        sheet.write(row, col + 18, 'Discharge Date', format1)
        sheet.write(row, col + 19, 'Room', format1)
        sheet.write(row, col + 20, 'Duration', format1)
        sheet.write(row, col + 21, 'Room Charge (With Tax)', format1)
        sheet.write(row, col + 22, 'Medicine Total Cost', format1)
        sheet.write(row, col + 23, 'Total Cost', format1)
        sheet.write(row, col + 24, 'Progress Rate', format1)
        sheet.write(row, col + 25, 'Case Notes', format1)
        sheet.write(row, col + 26, 'Medical Notes', format1)

        sheet.set_column('A:B', 15)
        sheet.set_column('C:F', 20)
        sheet.set_column('G:AA', 40)

        for case in data['cases']:
            row += 1
            sheet.write(row, col, case['c_id'], format2)
            sheet.write(row, col + 1, case['p_name'], format2)
            sheet.write(row, col + 2, case['p_id'], format2)
            sheet.write(row, col + 3, case['p_gender'], format2)
            sheet.write(row, col + 4, case['p_age'], format2)
            sheet.write(row, col + 5, case['p_blood_group'], format2)
            sheet.write(row, col + 6, case['criticality'], format2)
            sheet.write(row, col + 7, case['state'], format2)
            sheet.write(row, col + 8, case['curr_illness'], format2)
            sheet.write(row, col + 9, case['prev_illness'], format2)
            sheet.write(row, col + 10, case['p_mob'], format2)
            sheet.write(row, col + 11, case['doctor'], format2)
            sheet.write(row, col + 12, case['d_id'], format2)
            sheet.write(row, col + 13, case['d_gender'], format2)
            sheet.write(row, col + 14, case['doc_mob'], format2)
            sheet.write(row, col + 15, case['total_fee'], format2)
            sheet.write(row, col + 16, case['is_admitted'], format2)
            sheet.write(row, col + 17, case['admission_date'], format2)
            sheet.write(row, col + 18, case['discharge_date'], format2)
            sheet.write(row, col + 19, case['room_type'], format2)
            sheet.write(row, col + 20, case['duration'], format2)
            sheet.write(row, col + 21, case['total_room_charge'], format2)
            sheet.write(row, col + 22, case['tax_total'], format2)
            sheet.write(row, col + 23, case['final_total'], format2)
            sheet.write(row, col + 24, case['progress_rate'], format2)
            sheet.write(row, col + 25, case['c_notes'], format2)
            sheet.write(row, col + 26, case['m_notes'], format2)
