from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import re
from datetime import *


class HospitalStaff(models.Model):
    _name = 'hospital.staff'
    _description = 'Hospital Staff'
    _rec_name = 'staff_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _inherit = 'hospital.doctor'
    _sql_constraints = [('id_unique', 'unique (staff_id)', 'Please Enter Unique Staff ID!')]

    staff_id = fields.Char(string='Staff ID', required=True,
                           copy=False, readonly=True,
                           default=lambda self: _('New'), index=True,
                           )
    name = fields.Char(string='Name', required=True, translate=True)
    role_id = fields.Char(string='Role ID', required=True,
                          copy=False, readonly=False,
                          default=lambda self: _('New'), index=True,
                          )
    s_age = fields.Integer(string='Age', required=True)
    s_gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
                                string="Gender", required=True)
    is_married = fields.Boolean(string="Is Married")

    currency = fields.Many2one('res.currency', string="Currency",
                               default=lambda self: self.env['res.currency'].search(
                                   [('name', '=', 'INR')]).id
                               , invisible=True)
    salary = fields.Monetary(string="Salary", currency_field='currency')
    active = fields.Boolean(default=True)
    s_dob = fields.Date(string="Date of Birth", required=True)
    s_mob = fields.Char(string='Mobile No:')
    s_email = fields.Char(string="Email:")
    s_image = fields.Binary(string="Photo")
    info = fields.Text(string='Info')
    exp = fields.Char(string="Experience", required=True)
    joining_date = fields.Datetime(string='Joining Date', required=True)
    leaving_date = fields.Datetime(string='Leaving Date')
    d_specialist = fields.Many2many("doctor.speciality")
    n_specialist = fields.Many2many("nurse.speciality")
    d_qualifications = fields.Many2one('doctor.designation')
    n_qualifications = fields.Many2one('nurse.designation')
    d_designation = fields.Selection([
        ('medical_director', 'Medical Director'), ('department_head', 'Department Head'),
        ('attending_physician', 'Attending Physician'), ('fellow', 'Fellow'),
        ('chief_resident', 'Chief Resident'), ('resident', 'Resident')
    ], string="Designation")
    n_designation = fields.Selection([
        ('RN', 'Registered Nurse'), ('LPN', 'Licensed Practical Nurse'),
        ('LVN', 'Licensed Vocational Nurse'), ('APRN', 'Advanced Practice Registered Nurse'),
        ('CNM', 'Certified Nurse Midwife'), ('CRNA', 'Certified Registered Nurse Anesthetist'),
        ('NP', 'Nurse Practitioner'), ('CN', 'Clinical Nurse'), ('APN', 'Advanced Practice Nurse')
    ], string="Designation")

    role = fields.Selection([('MedicalDoctor', 'Medical Doctor'), ('Surgeon', 'Surgeon'),
                             ('Nurse', 'Nurse'),
                             ('MedicalAssistant', 'Medical Assistant'),
                             ('Pharmacist', 'Pharmacist'),
                             ('MedicalLaboratoryTechnologist', 'Medical Laboratory Technologist'),
                             ('RadiologicTechnologist', 'Radiologic Technologist'),
                             ('PhysicalTherapist', 'Physical Therapist'),
                             ('OccupationalTherapist', 'Occupational Therapist'),
                             ('SocialWorker', 'Social Worker'),
                             ('CaseManager', 'Case Manager'), ('HospitalAdministrator',
                                                               'Hospital Administrator'),
                             ('MaintenanceStaff', 'Maintenance Staff'), ('SecurityPersonnel',
                                                                         'Security Personnel')],
                            string='Role', required=True)
    rating = fields.Selection(
        [('0', 'Very Bad'), ('1', 'Bad'), ('2', 'Average'),
         ('3', 'Good'), ('4', 'Very Good'), ('5', 'Excellent')])

    birth_day = fields.Boolean(default=False, compute="_compute_birth_day")

    password = fields.Char()
    user_id = fields.Many2one('res.users')

    # @api.onchange('role')
    # def _compute_specialties(self):
    #     for record in self:
    #         self.specialist = [(5, 0, 0)]
    #         if record.role == 'MedicalDoctor' or record.role == 'MedicalDoctor':
    #             # pass
    #             record.specialist = [(6, 0, self.env['doctor.speciality'].search([]).ids)]
    #         elif record.role == 'Nurse':
    #             record.specialist = [(6, 0, self.env['nurse.speciality'].search([]).ids)]
    #         # elif record.role == 'Pharmacist':
    #         #     record.specialist = [(6, 0, self.env['pharmacist.specialty'].search([]).ids)]

    # To check role and create in respective role
    @api.model
    def create(self, vals):
        if vals.get('role') == 'MedicalDoctor':
            if vals.get('name'):
                if vals.get('name')[:3] != 'dr.' and vals.get('name')[:3] != 'Dr.':
                    vals['name'] = 'Dr.' + vals.get('name')
            else:
                vals['name'] = ''

            if vals.get('staff_id', _('New')) == _('New'):
                vals['staff_id'] = self.env['ir.sequence'].next_by_code('hospital.staff.sequence') or _('New')

            if vals.get('role_id', _('New')) == _('New'):
                vals['role_id'] = self.env['ir.sequence'].next_by_code('hospital.doctor.sequence') or _('New')

            info = {
                'd_id': vals.get('role_id'),
                'doctor': vals.get('name'),
                'd_age': vals.get('s_age'),
                'doc_mob': vals.get('s_mob'),
                'd_email': vals.get('s_email'),
                'd_gender': vals.get('s_gender'),
                'salary': vals.get('salary'),
                'd_image': vals.get('s_image'),
                'd_dob': vals.get('s_dob'),
                'is_married': vals.get('is_married'),
                'exp': vals.get('exp'),
                'specialist': vals.get('d_specialist'),
                'qualifications': vals.get('d_qualifications'),
                'info': vals.get('info'),
                'designation': vals.get('d_designation'),
                'joining_date': vals.get('joining_date'),
                'rating': vals.get('rating')
            }

            print('1----------------------', info)
            created_staff = super(HospitalStaff, self).create(vals)
            self.env['hospital.doctor'].create(info)
            return created_staff

        elif vals.get('role') == 'Nurse':
            if vals.get('staff_id', _('New')) == _('New'):
                vals['staff_id'] = self.env['ir.sequence'].next_by_code('hospital.staff.sequence') or _('New')

            if vals.get('role_id', _('New')) == _('New'):
                vals['role_id'] = self.env['ir.sequence'].next_by_code('hospital.nurse.sequence') or _('New')
            info = {
                'n_id': vals.get('role_id'),
                'name': vals.get('name'),
                'n_age': vals.get('s_age'),
                'n_mob': vals.get('s_mob'),
                'n_email': vals.get('s_email'),
                'n_gender': vals.get('s_gender'),
                'salary': vals.get('salary'),
                'n_image': vals.get('s_image'),
                'n_dob': vals.get('s_dob'),
                'is_married': vals.get('is_married'),
                'exp': vals.get('exp'),
                'specialist': vals.get('n_specialist'),
                'qualifications': vals.get('n_qualifications'),
                'info': vals.get('info'),
                'designation': vals.get('n_designation'),
                'joining_date': vals.get('joining_date'),
                'rating': vals.get('rating')

            }

            print('2----------------------', info)
            created_staff = super(HospitalStaff, self).create(vals)
            self.env['hospital.nurse'].create(info)
            return created_staff
        else:
            return super(HospitalStaff, self).create(vals)

    # To write on existing records
    def write(self, vals):
        for staff_record in self:
            if 'active' in vals and not vals['active']:
                vals['leaving_date'] = fields.Datetime.now()
            elif 'active' in vals and vals['active']:
                vals['leaving_date'] = False
            if staff_record.role == 'MedicalDoctor':
                valid_fields = self.env['hospital.doctor']._fields.keys()
                valid_vals = {key: val for key, val in vals.items() if key in valid_fields}
                doctor_record = staff_record.env['hospital.doctor'].search([
                    ('d_id', '=', staff_record.role_id)], limit=1)
                if doctor_record:
                    doctor_record.write(valid_vals)
                    print(1, '-', valid_vals)

            elif staff_record.role == 'Nurse':
                valid_fields = self.env['hospital.nurse']._fields.keys()

                valid_vals = {key: val for key, val in vals.items() if key in valid_fields}
                nurse_record = staff_record.env['hospital.nurse'].search([
                    ('n_id', '=', staff_record.role_id)], limit=1)
                if nurse_record:
                    nurse_record.write(valid_vals)
                    print(2, '-', valid_vals)

        # Call the super method to update the staff record
        return super(HospitalStaff, self).write(vals)

    # To make delete cascade
    def unlink(self):
        for staff_record in self:
            if staff_record.role == 'MedicalDoctor':
                doctor_record = staff_record.env['hospital.doctor'].search([
                    ('d_id', '=', staff_record.role_id)], limit=1)
                if doctor_record:
                    res = doctor_record.unlink()
                    print(res)

            elif staff_record.role == 'Nurse':
                nurse_record = staff_record.env['hospital.nurse'].search([
                    ('n_id', '=', staff_record.role_id)], limit=1)
                if nurse_record:
                    res = nurse_record.unlink()
                    print(res)

        return super(HospitalStaff, self).unlink()

    # To Check Email
    @api.constrains('s_email')
    def _validate_email(self):
        for i in self:
            if i.s_email:  # if Doctor email Field is not empty
                pd = re.fullmatch(r'^[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                                  str(i.s_email))
                if pd is None:  # if Not Valid Email
                    raise ValidationError(_("Doctor Email is not valid!"))

    # To get age from date of birth
    @api.onchange('s_age', 's_dob')
    def change_age(self):
        for i in self:
            if i.s_dob:
                birth_date = fields.Date.from_string(i.s_dob)
                current_date = fields.Date.from_string(date.today())
                age_years = current_date.year - birth_date.year
                i.s_age = age_years

    # To validate Mobile No
    @api.constrains('s_mob')
    def validate_mobile_no(self):
        for i in self:
            if i.s_dob:
                r = re.fullmatch(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}",
                                 str(i.s_mob))
                if r is None:
                    raise ValidationError(_("Mobile Number Is Not Valid!"))

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
    @api.constrains('s_image')
    def check_image(self):
        for i in self:
            if i.s_image and i.convert_to_mbsize(i.with_context(bin_size=True).s_image) > 1024:
                raise UserError('Image File should be more than 1 mb')

    # @api.depends('active')
    # def _compute_leave(self):
    #     for record in self:
    #         if ((not record.active) and (not record.leaving_date)):
    #             print('------------hell', fields.Datetime.now())
    #             record.leaving_date = fields.Datetime.now()
    #         elif ((not record.active) and record.leaving_date):
    #             pass
    #         else:
    #             record.leaving_date = False

    # #Leaving Date Function
    # @api.onchange('active')
    # def compute_leave(self):
    #     for i in self:
    #         if not i.active:
    #             i.leaving_date = fields.Datetime.now()
    #         else:
    #             i.leaving_date = False

    # Checking Birthday
    @api.depends('s_dob')
    def _compute_birth_day(self):
        for i in self:
            if i.s_dob:
                today = date.today()
                if today.day == i.s_dob.day and today.month == i.s_dob.month:
                    print(i.s_dob)
                    i.birth_day = True
                else:
                    i.birth_day = False
            else:
                pass
