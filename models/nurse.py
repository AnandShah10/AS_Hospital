from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import *
import string, secrets


# doctor class
class HospitalNurse(models.Model):
    _name = "hospital.nurse"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Nurse List"
    # _rec_name = "name"
    _sql_constraints = [
        ('unique_n_id', 'unique (n_id)', 'Nurse ID Must Be Unique!'),
        ('check_salary', 'check (salary > 0.00)', "Salary Must Be Greater than 0!")
    ]

    name = fields.Char(string="Name", required=True, translate=True)
    n_id = fields.Char(string="Id", required=True,
                       copy=False, readonly=True,
                       default=lambda self: _('New'), index=True,
                       )
    n_gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
                                string='Gender', required=True)
    n_email = fields.Char(string="Email")
    n_mob = fields.Char(string="Mobile No.")
    n_image = fields.Binary(string="Photo")
    # patient_ids = fields.Many2many('hospital.patient', 'patient_doctor_relation',
    #                                string="Patients")
    specialist = fields.Many2many("nurse.speciality", 'nurse_speciality_rel', string="Specialist")
    exp = fields.Char(string="Experience", required=True)
    n_age = fields.Integer(string="Age")
    designation = fields.Selection([
        ('RN', 'Registered Nurse'), ('LPN', 'Licensed Practical Nurse'),
        ('LVN', 'Licensed Vocational Nurse'), ('APRN', 'Advanced Practice Registered Nurse'),
        ('CNM', 'Certified Nurse Midwife'), ('CRNA', 'Certified Registered Nurse Anesthetist'),
        ('NP', 'Nurse Practitioner'), ('CN', 'Clinical Nurse'), ('APN', 'Advanced Practice Nurse')
    ])
    rating = fields.Selection(
        [('0', 'Very Bad'), ('1', 'Bad'), ('2', 'Average'), ('3', 'Good'),
         ('4', 'Very Good'), ('5', 'Excellent')])

    qualifications = fields.Many2one('nurse.designation', string='Qualification')
    info = fields.Text(string="Info")
    is_married = fields.Boolean(string="Is_married")
    n_dob = fields.Date(string="Date of Birth", required=True)
    currency = fields.Many2one('res.currency', string="Currency",
                               default=lambda self: self.env['res.currency'].search(
                                   [('name', '=', 'INR')]).id
                               , invisible=True)
    salary = fields.Monetary(string="Salary", currency_field='currency')
    active = fields.Boolean(default=True)

    joining_date = fields.Datetime(string='Joining Date')
    leaving_date = fields.Datetime(string='Leaving Date')

    password = fields.Char()
    user_id = fields.Many2one('res.users')

    # To Check Email
    @api.constrains('n_email')
    def _validate_email(self):
        for i in self:
            if i.n_email:  # if Doctor email Field is not empty
                pd = re.fullmatch(r'^[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                                  str(i.n_email))

                if pd is None:  # if Not Valid Email
                    raise ValidationError(_("Doctor Email is not valid!"))

    # To get age from date of birth
    @api.onchange('n_age', 'n_dob')
    def change_age(self):
        for i in self:
            if i.n_dob:
                birth_date = fields.Date.from_string(i.n_dob)
                current_date = fields.Date.from_string(date.today())
                age_years = current_date.year - birth_date.year
                i.n_age = age_years

    def generate_password(self, length=12):
        """Generate a random password with the specified length."""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def _get_report_base_filename(self):
        return self.name

    def create_user(self, vals):
        password = self.generate_password()
        print(password)
        """Method to create a new user based on project team member details."""
        user_vals = {
            'name': vals.get('name'),  # Use appropriate fields from your model
            'login': vals.get('n_email'),  # Assuming email is used for login
            'password': password,  # Set initial password
            'groups_id': [(6, 0, [self.env.ref('as_hospital.group_hospital_nurse').id])],  # Assign to the portal group
        }
        res = self.env['res.users'].sudo().create(user_vals)
        print("LLLLLLLLLLLLLLLLL")
        return user_vals['password'], res

    # Send Mail on creating new case
    def send_mail_on_create(self, res):
        print("ugyugdjhvchfhegvcbhjb vjhf")
        template = self.env.ref('as_hospital.nurse_mail_template')
        print("trdrtfygyufu",
              res.id, res.name, res.n_email,
              res.create_date, '---')
        email_values = {'email_to': res.n_email,
                        'email_from': self.env.user.email,
                        }
        template.send_mail(res.id, email_values=email_values, force_send=True)
        print("----------------||||||||||||||||||||||")
        return True

    # Nurse ID Sequence
    @api.model
    def create(self, vals):
        if vals.get('n_id', _('New')) == _('New'):
            vals['n_id'] = self.env['ir.sequence'].next_by_code('hospital.nurse.sequence') or _('New')
        res = super(HospitalNurse, self).create(vals)
        password, x = self.create_user(vals)
        print("III", password, x)
        res.write({'user_id': x, 'password': password})
        print("ccccccccccccccccccc")
        self.send_mail_on_create(res)
        print("OOOOOOOOO")
        print("PPPPPPPPPPPPPPPP", res)
        return res

    # To validate Mobile No
    @api.constrains('n_mob')
    def validate_mobile_no(self):
        for i in self:
            if i.n_mob:
                r = re.fullmatch(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}",
                                 i.n_mob)
                if r is None:
                    raise ValidationError(_("Mobile Number Is Not Valid!"))

    # Convert File Size
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
    @api.constrains('n_image')
    def check_image(self):
        for i in self:
            if i.n_image and i.convert_to_mbsize(i.with_context(bin_size=True).n_image) > 1024:
                raise UserError('Image File should be more than 1 mb')


# Speciality Class
class NurseSpeciality(models.Model):
    _name = "nurse.speciality"
    _description = "Nurse speciality"

    name = fields.Char(string="Specialization", required=True, translate=True)


# Designation class
class NurseDesignation(models.Model):
    _name = 'nurse.designation'
    _description = 'nurse designation'

    name = fields.Char(string="Designations", required=True, translate=True)
