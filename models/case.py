from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
import base64
import logging
from datetime import date, datetime


class HospitalCase(models.Model):
    _name = "hospital.case"
    _description = "Case Info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'c_id'
    _order = 'id desc'
    _sql_constraints = [
        ('unique_c_id', 'unique (c_id)', 'Case ID Must Be Unique!'),
        ('non_zero_fees', 'check (fees > 0.00)', "Fees Must Be Greater than Zero!")
    ]

    c_id = fields.Char(string="Case Id", required=True, tracking=True,
                       copy=False, readonly=True,
                       default=lambda self: _('New'), index=True,
                       )
    bill_id = fields.Char(string="Order Id",
                          copy=False, readonly=True,
                          default=lambda self: _('New'), index=True, )
    c_notes = fields.Text(string="Case Notes")
    m_notes = fields.Text(string="Previous Issues")
    prev_illness = fields.Char(string="Illness (Previous)", required=True)
    curr_illness = fields.Char(string="Illness (Current)", required=True)
    progress_rate = fields.Float(string='Progress Rate')
    is_admitted = fields.Boolean(string="IS Admitted", default=False)

    c_ids = fields.Many2one("hospital.patient", required=True, string="Case:")

    p_name = fields.Char(string='Patient Name', related="c_ids.name")
    p_id = fields.Char(string="Patient Id", related='c_ids.p_id')
    p_age = fields.Integer(string="Patient Age", related='c_ids.age')
    p_gender = fields.Selection(string="Gender", related='c_ids.gender')
    p_is_child = fields.Boolean(string="Is_child", related='c_ids.is_child')
    p_image = fields.Binary(string="Patient Image", related='c_ids.image')
    p_blood_group = fields.Char(string="Blood group", related="c_ids.blood_group")
    p_mob = fields.Char(string="Mobile No.", related="c_ids.mobile_no")
    p_email = fields.Char(string="Email Address:", related="c_ids.email")

    active = fields.Boolean(default=True)
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

    doctor = fields.Many2one('hospital.doctor', string="Doctor", required=True)
    d_id = fields.Char(string="Doctor Id", related='doctor.d_id')
    d_email = fields.Char(string="Doctor Email", related='doctor.d_email')
    doc_mob = fields.Char(string="Doctor Mobile No.", related='doctor.doc_mob')
    d_gender = fields.Selection(string="Gender", related='doctor.d_gender')

    prescription_ids = fields.One2many('patient.prescription', 'c_id', string="Prescription")

    admission_date = fields.Datetime(string="Admission Date", default=fields.Datetime.now,
                                     help="Enter admission date of patient.")
    discharge_date = fields.Datetime(string="Discharge Date", default=fields.Datetime.now,
                                     help="Enter discharge date of patient.")

    fees = fields.Monetary(string="Fees", currency_field="currency")
    fee_tax = fields.Monetary(string="Fee Tax", currency_field="currency")

    room_tax = fields.Monetary(string="Room Tax", currency_field="currency")
    total_fee = fields.Monetary(string="Total Fees", currency_field="currency")
    total_room_charge = fields.Monetary(string="Total Room Charge", currency_field="currency")

    currency = fields.Many2one('res.currency', string="Currency",
                               default=lambda self: self.env['res.currency'].search(
                                   [('name', '=', 'INR')]).id,
                               readonly=True)

    duration = fields.Integer(string="Duration (Days)")
    total_charge = fields.Monetary(string="Total charge", currency_field="currency")
    room_type = fields.Selection([('general', 'General'), ('semi_special', 'Semi-Special'),
                                  ('special_non', 'Special(Non AC)'),
                                  ('special_ac', 'Special (AC)'), ('delux', 'Delux')],
                                 string="Room", tracking=True)
    room_price = fields.Float(string="Room Charge (per Day)")

    total_price = fields.Monetary(string="Untaxed Amount:", compute="cal_total",
                                  currency_field='currency', store=True)
    tax = fields.Monetary(string="Tax 18%:", currency_field='currency',
                          compute="cal_total", store=True)
    tax_total = fields.Monetary(string="Total:", currency_field='currency',
                                compute="cal_total", store=True)

    final_total = fields.Monetary(string="Total Cost:", currency_field='currency')

    a_ids = fields.One2many('hospital.appointment', 'c_ids')
    state = fields.Selection([('1', 'Canceled'), ('2', 'Postponed'),
                              ('3', 'Ongoing'), ('4', 'Successful'),
                              ('5', 'Unsuccessful'), ('6', 'Completed')])

    is_paid = fields.Boolean(default=False)

    # To change the state
    def change_state(self):
        for i in self:
            if i.state != '6':
                i.state = str(int(i.state) + 1)
            else:
                i.state = '1'
            s = dict(i._fields['state'].selection).get(i.state)
            self.message_post(body=f"State has been set to {s}")

    # Archive-Unarchive function
    def archive_case_record(self):
        for i in self:
            if i.active:
                i.active = False
                i.message_post(body="Record is Archived.")
            else:
                i.active = True
                i.message_post(body="Record is Unarchived.")

    # Case ID Sequence
    @api.model
    def create(self, vals):
        if vals.get('c_id', _('New')) == _('New'):
            vals['c_id'] = self.env['ir.sequence'].next_by_code('hospital.case.sequence') or _('New')
        res = super(HospitalCase, self).create(vals)
        print(res.id, res.p_email, res.p_name, res.create_date, res.c_id, '{{{{{{{{{{{{64755')
        # x = self.mail_case()
        # x = self.send_email_with_experiment(vals)
        x = self.send_mail_on_create(res)
        print(x, '))))))))))))))))))))))))))))')
        return res

    # Send Mail on creating new case
    def send_mail_on_create(self, res):
        print("ugyugdjhvchfhegvcbhjb vjhf")
        template = self.env.ref('as_hospital.case_mail_template')
        print("trdrtfygyufu", res.c_ids, '@@@@@@@@', res.c_id,
              res.id, res.p_name, res.p_email,
              res.create_date, '---')
        email_values = {'email_to': res.p_email,
                        'email_from': self.env.user.email,
                        }
        template.send_mail(res.id, email_values=email_values, force_send=True)
        print("----------------||||||||||||||||||||||")
        return True

    # Sending mail (no attachment)
    def mail_case(self):
        print("Mailing!!!!!!!!!!!!")
        record = self.env.ref('as_hospital.case_mail_template')
        for i in self:
            print('--------------', self.p_email)
            if i.p_email:
                email_values = {
                    'email_cc': False,
                    'auto_delete': True,
                    'message_type': 'user_notification',
                    'recipient_ids': [],
                    'partner_ids': [],
                    'scheduled_date': False,
                    'email_to': i.p_email,

                }
                print(email_values, '=================')
                record.send_mail(i.id, force_send=True, email_values=email_values)
                i.message_post(body="Mail sent to patient")

    # Sending Email With attachment
    def send_email_with_attachment(self):
        report = self.env['ir.actions.report']._render_qweb_pdf("as_hospital.report_case_details_pdf", self.id)
        data_record = base64.b64encode(report[0])
        ir_values = {
            'name': "Case Report",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        template = self.env.ref('as_hospital.case_mail_template')
        template.attachment_ids = [(6, 0, [data_id.id])]
        email_values = {'email_to': self.p_email,
                        'email_from': self.env.user.email}
        template.send_mail(self.id, email_values=email_values, force_send=True)
        template.attachment_ids = [(3, data_id.id)]
        return True

    # Sending Payment Mail with Bill
    def send_payment_email_with_attachment(self):
        report = self.env['ir.actions.report']._render_qweb_pdf("as_hospital.report_bill_payment_pdf", self.id)
        data_record = base64.b64encode(report[0])
        ir_values = {
            'name': "Payment Receipt",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        template = self.env.ref('as_hospital.payment_receipt_template')
        template.attachment_ids = [(6, 0, [data_id.id])]
        email_values = {'email_to': self.p_email,
                        'email_from': self.env.user.email}
        template.send_mail(self.id, email_values=email_values, force_send=True)
        template.attachment_ids = [(3, data_id.id)]
        return True

    # Cronjob Function
    def check_state(self):
        print("Cronjob------------------------------------->")
        case_ids = self.env['hospital.case'].search([("state", '=', 6),
                                                     ('active', '=', True), ('is_paid', '!=', True)])
        print(case_ids)

        for i in case_ids:
            print(i.state, '======<=====>=======')
            i.send_payment_email_with_attachment()
            print("@@@@@@@@@@@@@@@@@@@@@")
            action = self.env.ref('as_hospital.action_hospital_case')
            print("################")
            # i.message_post(body="The Payment Is due!", subtype='mt_note')
            res = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': '%s',
                    'type': 'warning',
                    'sticky': True,
                },
                'links': [{
                    'label': _('Case Record Not Found!'),
                    'url': f'#action={action.id}&model=hospital.case',
                    'target': '_self',
                }],
            }
            print(res, '=============!!!!!!!!!!!!!!!!!!!')
            return res

    # Experimenting In couninue
    # def send_email_with_experiment(self, vals):
    #     print("3456475869")
    #     template = self.env.ref('as_hospital.case_mail_template')
    #     print("trdrtfygyufu", vals.get('c_ids'), '@@@@@@@@', vals.get('c_id'),
    #           vals.get('id'),
    #           vals.get('create_date'))
    #     cases = self.env['hospital.patient'].search([('id', '=', vals.get('c_ids'))])
    #     print(cases.name, '[[[[[[[[[[[[[[[[[[[[[[[[[[')
    #     for i in cases:
    #         print(i.email, '------------>56')
    #         email_values = {'email_to': i.email,
    #                         'email_from': i.env.user.email,
    #                         }
    #         print("((())))))))))46578697")
    #         print(i.id, '[[[[[[[[[[[[)')
    #         template.send_mail(i.id, email_values=email_values, force_send=True)
    #         print("----------------||||||||||||||||||||||")
    #         return True

    # def get_chatter_activity(self):
    #     all_messages_case = self.env['mail.message'].search(
    #         [('res_id', "=", rec.id), ('model', "=", "hospital.case"), ], order='create_date asc')

    # To get Chatter Activity
    def get_chatter_activity(self):
        chatter_messages = []
        print("=====><=======")
        chatter_activities = self.message_ids.filtered(lambda x: x.model == 'hospital.case')
        for activity in chatter_activities:
            chatter_messages.append(activity.body)
            # self.env['hospital.case'].create({'message': activity.body})
        print(chatter_messages)
        self.message_post(body="Activities has been Exported.")
        print("MMMMMMMMMMMMMMMMMMMMMMMMM")

    # PDF Report
    def print_case_report(self):
        self.message_post(body="PDF Record is printed.")
        return self.env.ref('as_hospital.report_case_details_pdf').report_action(self)

    # Bill Receipt
    def print_payment_receipt(self):
        if self.bill_id == _('New'):  # For Unique Bill ID
            self.bill_id = self.env['ir.sequence'].next_by_code('hospital.bill.sequence') or _('New')

        self.message_post(body="Receipt is printed.")
        return self.env.ref('as_hospital.report_bill_payment_pdf').report_action(self)

    # Preview Of Receipt
    def preview_payment_receipt(self):
        self.message_post(body="Receipt  has been previewed.")
        return self.env.ref('as_hospital.report_bill_payment_html').report_action(self)

    # Preview of PDF Report
    def print_case_report_preview(self):
        self.message_post(body="Record has been previewed.")
        return self.env.ref('as_hospital.report_case_details_html').report_action(self)

    def _get_report_base_filename(self):
        return self.p_name + '-' + self.c_id

    # Excel Report
    def print_case_report_xlsx(self):
        self.message_post(body="Excel Record is printed.")
        return self.env.ref('as_hospital.report_case_details_xls').report_action(self)

    def send_on_whatsapp(self):
        print("whatsapp send...........")
        if not self.p_mob:
            return {
                'action': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('There is no phone number in record!'),
                    'sticky': True,
                },
            }
        print("herr0000000000000000000000")
        msg = 'Hi %s' % self.p_name
        phone = self.p_mob
        if len(self.p_mob) > 10:
            phone = self.p_mob[-10:]
            print('phone,,,,,,,', phone)
        url = 'https://web.whatsapp.com/send?phone=%s&text=%s&app_absent=True' % (phone, msg)
        print(url, 'urlmmmmmmmmmmmmmmmmmmmmmmmmm')

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url
        }

    # Duration between
    @api.onchange('admission_date', 'discharge_date', 'duration')
    def count_days(self):
        if self.discharge_date and self.admission_date:
            duration = self.discharge_date - self.admission_date
            self.duration = duration.days

    # Room price
    @api.onchange('room_price', 'room_type')
    def room_charge(self):
        for i in self:
            if i.room_type:
                if i.room_type == 'general':
                    i.room_price = 200.00
                elif i.room_type == 'semi_special':
                    i.room_price = 230.00
                elif i.room_type == 'special_non':
                    i.room_price = 270.00
                elif i.room_type == 'special_ac':
                    i.room_price = 300.00
                elif i.room_type == 'delux':
                    i.room_price == 350.00
                else:
                    i.room_price == 500.00
        # print(self.room_price)

    # Total charge
    @api.onchange('room_price', 'total_charge', 'fees', 'duration')
    def calc_charge(self):
        for i in self:
            i.total_charge = i.room_price * i.duration + i.fees

    # To get total of medicine cost with and without  tax
    @api.depends('prescription_ids', 'tax', 'total_price', 'tax_total')
    def cal_total(self):
        for i in self:
            i.total_price = sum(prescription.total for prescription in i.prescription_ids)
            i.tax = i.total_price * 0.18
            i.tax_total = i.total_price + i.tax

    # To calculate total fee charge with and without  tax
    @api.onchange('fees', 'fee_tax', 'total_fee')
    def cal_fee(self):
        for i in self:
            i.fee_tax = i.fees * 0.18
            i.total_fee = i.fees + i.fee_tax

    # Calculate total room cost with and without  tax
    @api.onchange('total_charge', 'room_tax', 'total_room_charge')
    def cal_room_charge(self):
        for i in self:
            i.room_tax = i.total_charge * 0.18
            i.total_room_charge = i.total_charge + i.room_tax

    # To get total cost of the whole case
    @api.onchange('total_room_charge', 'tax_total', 'total_fee')
    def final_total_calc(self):
        for i in self:
            i.final_total = i.tax_total + i.total_room_charge + i.total_fee

    # To Constrain limit of Progress Bar
    @api.constrains("progress_rate")
    def _check_progress(self):
        for i in self:
            if i.progress_rate > 100:
                i.progress_rate = 100
            elif i.progress_rate < 0:
                i.progress_rate = 0

    # Progress and state correlating
    @api.onchange('progress_rate', 'state')
    def case_completion(self):
        for i in self:
            if i.progress_rate == 100 and i.state != '6':
                i.state == '6'
            elif i.state == '6' and i.progress_rate != 100:
                i.progress_rate = 100
            else:
                pass

    # Payment Verification
    def case_paid(self):
        for i in self:
            if not i.is_paid:
                i.is_paid = True
                print("xzzzzzzzzzzzzzzzzzzzzzzzzz")
                i.send_payment_email_with_attachment()
                i.message_post(body="The Payment Has Been Done.")
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Payment Verified Successfully!',
                        'type': 'rainbow_man',
                    }
                }
            else:
                i.is_paid = False

    # Rainbow Notifications
    def action_confirm_rainbow(self, message):
        print("Hello=================>P")
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man',
            }
        }

    # For Dead patient
    @api.onchange('state', 'criticality')
    def state_criticality_sync(self):
        for i in self:
            if i.criticality == 'dead':
                i.state = '6'

    # medicine validation for same name
    @api.constrains('prescription_ids')
    def _check_unique_medicine_names(self):
        for case in self:
            medicine_names = case.prescription_ids.mapped('name')
            if len(medicine_names) != len(set(medicine_names)):
                raise ValidationError("You can not add a medicine twice instead add quantity if needed!")

    # def _search_doctor(self):
    #     return [('d_id', 'ilike', 'DOC'),('doctor','not ilike','dr.')]
