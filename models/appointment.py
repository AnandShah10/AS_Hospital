from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import date, datetime
import base64


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _description = "Appointment Info"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'a_id'
    _order = 'appointment_date'
    _sql_constraints = [
        ('unique_appointment_id', 'unique (a_id)', 'Appointment ID Must Be Unique!'),
    ]

    a_id = fields.Char(string="Appointment ID", tracking=True, required=True,
                       copy=False, readonly=True,
                       default=lambda self: _('New'), index=True,
                       )
    appointment_date = fields.Datetime(string="Appointment Date", tracking=True, required=True)
    # appointment_time = fields.Float(string="Appointment Time")
    c_ids = fields.Many2one("hospital.case", ondelete='cascade')
    active = fields.Boolean(default=True)
    appointment_today = fields.Boolean(default=False, compute='check_appointment')

    # Mail Function
    def mail_appointment(self):
        print("Mailing!!!!!!!!!!!!")
        record = self.env.ref('as_hospital.appointment_mail_template')
        print("333333333333333")
        for i in self:
            print("@@@@@@@@@@@@")
            if i.c_ids.p_email:
                email_values = {
                    'email_cc': False,
                    'auto_delete': True,
                    'message_type': 'user_notification',
                    'recipient_ids': [],
                    'partner_ids': [],
                    'scheduled_date': False,
                }
                record.send_mail(i.id, force_send=True, email_values=email_values)
                i.message_post(body="Mail sent to patient")
                print("##########")

    # Mailing Appointment Reminder
    def mail_appointment_reminder(self):
        print("Mailing!!!!!!!!!!!!")
        record = self.env.ref('as_hospital.appointment_reminder_mail_template')
        print("333333333333333")
        for i in self:
            print("@@@@@@@@@@@@")
            if i.c_ids.p_email:
                email_values = {
                    'email_cc': False,
                    'auto_delete': True,
                    'message_type': 'user_notification',
                    'recipient_ids': [],
                    'partner_ids': [],
                    'scheduled_date': False,
                }
                record.send_mail(i.id, force_send=True, email_values=email_values)
                i.message_post(body="Mail sent to patient")
                print("##########")

    # Cronjob Function
    def check_date(self):
        print("Cronjob>>>>>>>>>>>>>>>>>>>")
        appointment_ids = self.env['hospital.appointment'].search([])
        print(appointment_ids, '--------------22222')
        for i in appointment_ids:
            print(i.appointment_date.date(), '======<=====>=======', datetime.today().date())
            if i.appointment_date.date() == datetime.today().date():
                i.mail_appointment_reminder()
                # i.appointment_today = True
                print("@@@@@@@@@@@@@@@@@@@@@")

    @api.depends('appointment_date')
    def check_appointment(self):
        print('>>>>>>')
        for i in self:
            if i.appointment_date:
                print(i.appointment_date.date())
                if i.appointment_date.date() == datetime.today().date():
                    print("@@@@@@@@!!!!!!!!!!!!")
                    # i.mail_appointment_reminder()
                    # i.env.user.message_notify(
                    #     body="Your appointment is scheduled for today.",
                    #     subject="Appointment Reminder"
                    # )
                    i.appointment_today = True
                else:
                    print("$$$$$$$$$$$$")
                    i.appointment_today = False
            else:
                print("&&&&&&&&&")
                i.appointment_date = False

    # Appointment Rescheduling
    def appointment_reschedule(self, curr_date):
        appointments = self.env['hospital.appointment'].search([], order='appointment_date', )
        print(appointments)
        for i in range(len(appointments)):
            if i + 1 < len(appointments):
                first = appointments[i]
                second = appointments[i + 1]
                print('hello')
                print(first.c_ids.doctor.d_id, second.c_ids.doctor.d_id)
                if first.c_ids.doctor.d_id == second.c_ids.doctor.d_id:
                    if first.appointment_date <= second.appointment_date:
                        temp = first.appointment_date
                        first.appointment_date = curr_date
                        curr_date = temp
            else:
                last_prev = appointments[i - 1]
                last = appointments[i]
                print('hi')
                print(last_prev.c_ids.doctor.d_id, last.c_ids.doctor.d_id)
                if last_prev.c_ids.doctor.d_id == last.c_ids.doctor.d_id:
                    if last_prev.appointment_date <= last.appointment_date:
                        last.appointment_date = curr_date

    # Appointment ID Sequence
    @api.model
    def create(self, vals):
        if vals.get('a_id', _('New')) == _('New'):
            vals['a_id'] = self.env['ir.sequence'].next_by_code('hospital.appointment.sequence') or _('New')
        res = super(HospitalAppointment, self).create(vals)
        # self.mail_appointment()
        # self.send_email_with_experiment(vals)
        if res.appointment_date:
            res._create_activity()

        self.send_mail_on_create(res)
        return res

    def write(self, vals):
        result = super(HospitalAppointment, self).write(vals)
        if 'appointment_date' in vals:
            for record in self:
                if record.appointment_date:
                    record._create_activity()

        return result

    # To send mail on creating new appointment
    def send_mail_on_create(self, res):
        print("ugyugdjhvchfhegvcbhjb vjhf")
        template = self.env.ref('as_hospital.appointment_mail_template')
        print("trdrtfygyufu", res.c_ids, '@@@@@@@@', res.c_ids.c_id,
              res.id, res.c_ids.p_name, res.c_ids.p_email,
              res.create_date, '---')
        email_values = {'email_to': res.c_ids.p_email,
                        'email_from': self.env.user.email,
                        }
        template.send_mail(res.id, email_values=email_values, force_send=True)
        print("----------------||||||||||||||||||||||")
        return True

    # Unlink Overloading
    def unlink(self):
        for i in self:
            appointment_date = i.appointment_date
            print(appointment_date)
            res = super(HospitalAppointment, i).unlink()
            i.appointment_reschedule(appointment_date)
            print(res)
            return res

    # Handling Archive
    @api.onchange('active', 'appointment_date')
    def handle_archive(self):
        for i in self:
            if i.active == False:
                appointment_date = i.appointment_date
                print(appointment_date)
                i.appointment_reschedule(appointment_date)
                print(appointment_date)

    # Copy Override
    def copy(self, default=None):
        for i in self:
            if default is None:
                default = {}
            if not default.get('a_id'):
                default['a_id'] = '%s(copy)' % (i.a_id)
                res = super(HospitalAppointment, i).copy(default=default)
                return res

    def _create_activity(self):
        for record in self:
            activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
            date_deadline = record.appointment_date
            record.activity_schedule(
                activity_type_id=activity_type_id,
                summary='Appointment Reminder',
                note='Appointment scheduled for this date.',
                date_deadline=date_deadline,
            )

    def send_on_whatsapp(self):
        print("whatsapp send...........")
        if not self.c_ids.p_mob:
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
        msg = 'Hi %s,Your *appointmnet* with reference %s is scheduled on %s ' % (
        self.c_ids.p_name, self.a_id,self.appointment_date)

        phone = self.c_ids.p_mob
        if len(self.c_ids.p_mob) > 10:
            phone = self.c_ids.p_mob[-10:]
            print('phone,,,,,,,', phone)
        url = 'https://web.whatsapp.com/send?phone=%s&text=%s&app_absent=True' % (phone, msg)
        print(url, 'urlmmmmmmmmmmmmmmmmmmmmmmmmm')

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url
        }
