from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import *
import string, secrets
from odoo.osv import expression


# doctor class
class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Doctor List"
    _rec_name = "doctor"
    _sql_constraints = [
        ('unique_d_id', 'unique (d_id)', 'Doctor ID Must Be Unique!'),
        ('check_salary', 'check (salary > 20000.00)', "Salary Must Be Greater than 10000!")
    ]

    doctor = fields.Char(string="Name", required=True, tracking=True,
                         search="_search_doctor", translate=True)
    d_id = fields.Char(string="Doctor Id", required=True, tracking=True,
                       copy=False, readonly=True,
                       default=lambda self: _('New'), index=True,
                       )
    d_gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
                                string='Gender', required=True)
    d_email = fields.Char(string="Email")
    doc_mob = fields.Char(string="Mobile No.")
    d_image = fields.Binary(string="Photo")
    patient_ids = fields.Many2many('hospital.patient', 'patient_doctor_relation',
                                   string="Patients")
    specialist = fields.Many2many("doctor.speciality", 'doctor_speciality_rel', string="Specialist")
    exp = fields.Char(string="Experience", required=True)
    d_age = fields.Integer(string="Age")
    qualifications = fields.Many2one('doctor.designation', string="Qualification")
    designation = fields.Selection([
        ('medical_director', 'Medical Director'), ('department_head', 'Department Head'),
        ('attending_physician', 'Attending Physician'), ('fellow', 'Fellow'),
        ('chief_resident', 'Chief Resident'), ('resident', 'Resident')
    ])
    info = fields.Text(string="Info")
    is_married = fields.Boolean(string="Is_married")
    d_dob = fields.Date(string="Date of Birth", required=True)
    currency = fields.Many2one('res.currency', string="Currency",
                               default=lambda self: self.env['res.currency'].search(
                                   [('name', '=', 'INR')]).id
                               , invisible=True)
    salary = fields.Monetary(string="Salary", currency_field='currency')
    active = fields.Boolean(default=True)

    joining_date = fields.Datetime(string='Joining Date')
    leaving_date = fields.Datetime(string='Leaving Date')
    rating = fields.Selection(
        [('0', 'Very Bad'), ('1', 'Bad'), ('2', 'Average'),
         ('3', 'Good'), ('4', 'Very Good'), ('5', 'Excellent')])
    case_count = fields.Integer(string='Case Count', compute='count_case')
    appointment_count = fields.Integer(string='Appointment Count', compute='count_appointment')
    user_id = fields.Many2one('res.users')
    password = fields.Char()

    # Compute Case Count
    def count_case(self):
        for i in self:
            case_count = self.env['hospital.case'].search_count([('doctor', '=', i.id)])
            i.case_count = case_count

    def count_appointment(self):
        for i in self:
            appointment_count = self.env['hospital.appointment'].search_count([('c_ids.doctor', '=', i.id)])
            i.appointment_count = appointment_count

    # To Check Email
    @api.constrains('d_email')
    def _validate_email(self):
        for i in self:
            if i.d_email:  # if Doctor email Field is not empty
                pd = re.fullmatch(r'^[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(i.d_email))
                print(i.d_email)
                if pd is None:  # if Not Valid Email
                    raise ValidationError(_("Doctor Email is not valid!"))

    # Print PDF Record
    def print_doctor_report(self):
        return self.env.ref('as_hospital.report_doctor_details_pdf').report_action(self)

    def generate_password(self, length=12):
        """Generate a random password with the specified length."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def create_user(self, vals):
        password = self.generate_password()
        print(password)
        """Method to create a new user based on project team member details."""
        user_vals = {
            'name': vals.get('doctor'),  # Use appropriate fields from your model
            'login': vals.get('d_email'),  # Assuming email is used for login
            'password': password,  # Set initial password
            'groups_id': [(6, 0, [self.env.ref('as_hospital.group_hospital_doctor').id])],
        }
        res = self.env['res.users'].sudo().create(user_vals)
        print("LLLLLLLLLLLLLLLLL")
        return user_vals['password'], res

    # Send Mail on creating new case
    def send_mail_on_create(self, res):
        print("ugyugdjhvchfhegvcbhjb vjhf")
        template = self.env.ref('as_hospital.doctor_mail_template')
        print("trdrtfygyufu",
              res.id, res.doctor, res.d_email,
              res.create_date, '---')
        email_values = {'email_to': res.d_email,
                        'email_from': self.env.user.email,
                        }
        template.send_mail(res.id, email_values=email_values, force_send=True)
        print("----------------||||||||||||||||||||||")
        return True

    # Doctor ID Sequence
    @api.model
    def create(self, vals):
        if vals.get('d_id', _('New')) == _('New'):
            vals['d_id'] = self.env['ir.sequence'].next_by_code('hospital.doctor.sequence') or _('New')
        res = super(HospitalDoctor, self).create(vals)
        password, x = self.create_user(vals)
        print("III", password, x)
        res.write({'user_id': x, 'password': password})
        print("ccccccccccccccccccc")
        self.send_mail_on_create(res)
        print("OOOOOOOOO")
        print("PPPPPPPPPPPPPPPP", res)
        return res

    # To get age from date of birth
    @api.onchange('d_age', 'd_dob')
    def change_age(self):
        for i in self:
            if i.d_dob:
                birth_date = fields.Date.from_string(i.d_dob)
                current_date = fields.Date.from_string(date.today())
                age_years = current_date.year - birth_date.year
                i.d_age = age_years

    # Check doctor name
    @api.onchange('doctor')
    def compute_doctor_name(self):
        for i in self:
            if i.doctor:
                if i.doctor[:3] != 'dr.' and i.doctor[:3] != 'Dr.':
                    i.doctor = 'Dr.' + i.doctor

            else:
                i.doctor = ''

    # To validate Mobile No
    @api.constrains('doc_mob')
    def validate_mobile_no(self):
        for i in self:
            if i.doc_mob:
                r = re.fullmatch(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}", i.doc_mob)
                if r is None:
                    raise ValidationError(_("Mobile Number Is Not Valid!"))

    def _get_report_base_filename(self):
        return self.doctor

    # File Size Conversion
    def convert_to_mbsize(self, binary_file_size):
        match_file = re.match(r'(\d+(?:\.\d+)?)\s*([KMG]?)B?$', binary_file_size.decode('utf-8'), re.IGNORECASE)
        if not match_file:
            match_file = re.match(r'(\d+(?:\.\d+)?)\s*(bytes)$', binary_file_size.dcode('utf-8'), re.IGNORECASE)
        file_size = float(match_file.group(1))
        file_extension = match_file.group(2)
        if file_extension == 'K':
            file_size /= 1024
        elif file_extension == 'M':
            file_size *= 1024
        elif file_extension == 'G':
            file_size *= 1024
        else:
            file_size /= 1024 ** 2
        return file_size

    # Image Size Validation
    @api.constrains('d_image')
    def check_image(self):
        for i in self:
            if i.d_image and i.convert_to_mbsize(i.with_context(bin_size=True).d_image) > 1024:
                raise UserError('Image File should be more than 1 mb')

    @api.model
    def _name_search(self, name=_rec_name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        print("hello.........search?????")
        if operator != 'ilike' or (name or '').strip():
            criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
            name_domain = criteria_operator + [('d_id', 'ilike', name + '%'), ('doctor', operator, name)]
            domain = expression.AND([name_domain, domain])
        print(domain, 'dddddddddddddddddddddddddddomain')
        return self._search(domain, limit=limit, order=order)

    def _search_doctor(self, operator, value):
        print("sssssssssssssssearching")
        if operator not in ("ilike", "like") or not isinstance(value, str):
            print("I am hereeeeeeeeeeeeeeee!")
            return ['|', ('d_email', operator, value), ('d_id', operator, value)]
        print("is ilke .........................")
        return [('d_email', operator, HospitalDoctor._parse_name_search(value))]


# Speciality Class
class DoctorSpeciality(models.Model):
    _name = "doctor.speciality"
    _description = "Doctor speciality"

    name = fields.Char(string="Specialization", required=True, translate=True)


# Designation class
class DoctorDesignation(models.Model):
    _name = 'doctor.designation'
    _description = 'doctor designation'

    name = fields.Char(string="Designations", required=True, translate=True)
