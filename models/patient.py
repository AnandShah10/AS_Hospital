from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re, base64
from datetime import date, datetime
import string
import secrets
from odoo.addons.base.models.res_users import check_identity


# Patient class
class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Patient Records"
    _rec_name = "name"
    _sql_constraints = [
        ('unique_p_id', 'unique (p_id)', 'Patient ID Must Be Unique!')
    ]

    name = fields.Char(string='Name', required=True, tracking=True,
                       index=True, translate=True, search='_search_patient')
    dob = fields.Date(string="Date of Birth")
    age = fields.Integer(string='Age')
    is_child = fields.Boolean(string='Is Child')
    is_married = fields.Boolean(string="Is married")
    has_rare_blood_type = fields.Boolean(string="Has Rare Blood Type")
    notes = fields.Text(string="Notes", translate=True)
    email = fields.Char(string='email', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')],
                              string="Gender")
    capitalized_name = fields.Char(string='Capitalized Name',
                                   compute="compute_capitalized_name",
                                   inverse='inverse_compute_capitalized_name',
                                   store=True, precompute=True)  # compute_sudo=True)
    address = fields.Text("Address", help='Enter Your address here.', translate=True)
    p_id = fields.Char(string="Patient Id", required=True, copy=False, readonly=True,
                       default=lambda self: _('New'), index=True, )

    has_disability = fields.Boolean(string="Has Disability")
    is_abnormal = fields.Boolean(string="Has Abnormality")
    image = fields.Binary("Image")
    mobile_no = fields.Char(string="Mobile Number")
    blood_group = fields.Char(string="Blood Group")
    other_info = fields.Text(string="Info")
    doctor_ids = fields.Many2many('hospital.doctor', 'patient_doctor_relation',
                                  string="Doctors")
    # nurse_ids = fields.Many2many('hospital.nurse', string="Nurses")
    c_ids = fields.One2many('hospital.case', 'c_ids')
    case_count = fields.Integer(string='Case Count', compute='count_case')
    appointment_count = fields.Integer(default=0, compute='count_appointment')
    password = fields.Char()
    user_id = fields.Many2one('res.users')
    # Things to do:
    #               making button visible on chatter ?,
    #               implement room full in settings (due),
    #               implement rooms in module (due),
    #               implement inventory and pharma (due),
    #               settings building(due),
    #               appointment rescheduling email(due),-----|
    #               rescheduling code fix ?,-------------|
    #               same doctor must not have a same appointment date time (due),----|
    #               Alert should be on case or on patient for appointment (due),
    #               state and country filter in website form (due)?,
    #               add one2many field in website form (due)?,
    #               reflecting un-archiving from staff (due)?,
    #               creating menu dropdown (due)?
    #               using speciality and search togather ?,
    #               searching functionality like shop ?,
    #               search,sort from one view to another (due)?,
    #               designation grouping (due)?,
    #               create case option on patient view (due),
    #               group by (due),
    #               payment Option (due),
    #               checkbox filter (due),
    #               value bar filter (due),
    #               record verification (due),
    #               if doctor's designation is for women illness the gender of patient should be female

    guardian_name = fields.Char(string='Guardian Name', translate=True)
    maiden_name = fields.Char(string='Maiden Name')
    mother_name = fields.Char(string='Mother Name', translate=True)
    father_name = fields.Char(string='Father Name', translate=True)
    f_name = fields.Char(string="First Name")
    m_name = fields.Char(string="Middle Name")
    l_name = fields.Char(string="Last Name")

    # Compute Case Count
    def count_case(self):
        for i in self:
            case_count = self.env['hospital.case'].search_count([('c_ids', '=', i.id)])
            i.case_count = case_count

    # Compute Appointment Count
    @api.depends('c_ids.a_ids')
    def count_appointment(self):
        for i in self:
            appointment_count = 0
            for case in i.c_ids:
                appointment_count += len(case.a_ids)
            i.appointment_count = appointment_count

    # Convert File Size
    @api.model
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
    @api.constrains('image')
    def check_image(self):
        for i in self:
            if i.image and i.convert_to_mbsize(i.with_context(bin_size=True).image) > 1024:
                raise UserError('Image File should be more than 1 mb')

    # To create address
    @api.onchange('addr1', 'addr2', 'country', 'p_state', 'zip', 'city', 'address', 'house_no')
    def make_address(self):
        for i in self:
            if i.addr1 and i.country and i.p_state and i.house_no and i.city and i.zip:
                i.address = str(str(i.house_no) + ',' + '\r\n' +
                                str(i.addr1) + ',' + '\r\n' +
                                str(i.addr2) + ',' + '\r\n' +
                                str(i.city.name) + ' - ' + str(i.zip) +
                                ',' + '\r\n' + str(i.p_state.name) +
                                ',' + str(i.country.name) +
                                '.')

            else:

                i.address = ''

    # Giving first and middle name
    @api.onchange('f_name', 'l_name', 'm_name', 'father_name', 'name')
    def give_names(self):
        for i in self:
            if i.father_name:
                i.m_name = i.father_name
            else:
                i.m_name = ''
            if i.name and (i.name[:3] not in ('Mr ', 'Ms ', 'Mrs')) and i.name[:6] != 'Master':
                i.f_name = i.name
            elif str(i.name)[:3] in ('Mr ', 'Ms ', 'Mrs'):
                i.f_name = i.name[3:]
            elif str(i.name)[:6] == 'Master':
                i.f_name = i.name[6:]
            else:
                i.f_name = ''

    # To add doctor names
    @api.onchange('c_ids', 'doctor_ids')
    def _add_doctor_name(self):
        for i in self:
            for j in i.c_ids:
                if j.doctor not in i.doctor_ids:
                    i.doctor_ids |= j.doctor
                    # i.write({'doctor_ids': [(4, 'c_ids.doctor.id')]})

    def _get_report_base_filename(self):
        return self.name

    # Sending Email with PDF attachment
    def send_email_with_attachment(self):
        report = self.env['ir.actions.report']._render_qweb_pdf("as_hospital.report_patient_details_with_cases_pdf",
                                                                self.id)
        print("hhhhhhhhelllllllllo")
        data_record = base64.b64encode(report[0])
        ir_values = {
            'name': "Patient Report",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        print("CReated,,,,,,,,,,,,,,,,,,,,,,,,")
        template = self.env.ref('as_hospital.patient_mail_template')
        print('Fetched Template.....................')
        template.attachment_ids = [(6, 0, [data_id.id])]
        print("?????????????????????")
        email_values = {'email_to': self.email,
                        'email_from': self.env.user.email}
        template.send_mail(self.id, email_values=email_values, force_send=True)
        print("Sending22222222222222222222222!")
        template.attachment_ids = [(3, data_id.id)]
        print("Eamil Sended !!!!!!!!!!!!!!!!!!!!!!!")
        return True

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
            'name': vals.get('name'),  # Use appropriate fields from your model
            'login': vals.get('email'),  # Assuming email is used for login
            'password': password,  # Set initial password
            'groups_id': [(6, 0, [self.env.ref('as_hospital.group_hospital_patient').id])],
        }
        res = self.env['res.users'].sudo().create(user_vals)
        print("LLLLLLLLLLLLLLLLL")
        return user_vals['password'], res

    # Send Mail on creating new case
    def send_mail_on_create(self, res):
        print("ugyugdjhvchfhegvcbhjb vjhf")
        template = self.env.ref('as_hospital.patient_mail_template')
        print("trdrtfygyufu",
              res.id, res.name, res.email,
              res.create_date, '---', res.password)
        email_values = {'email_to': res.email,
                        'email_from': self.env.user.email,
                        }
        template.send_mail(res.id, email_values=email_values, force_send=True)
        print("----------------||||||||||||||||||||||")
        return True

    # Overriding create method
    # Patient ID Sequence
    @api.model
    def create(self, vals):
        if vals.get('p_id', _('New')) == _('New'):
            vals['p_id'] = self.env['ir.sequence'].next_by_code('hospital.patient.sequence') or _('New')

        res = super(HospitalPatient, self).create(vals)
        password, x = self.create_user(vals)
        print("III", password, x)
        res.write({'user_id': x, 'password': x.password})
        print("ccccccccccccccccccc")
        self.send_mail_on_create(res)
        print("OOOOOOOOO")
        print("PPPPPPPPPPPPPPPP", res)
        return res

        # if (vals.get('name')[:4] not in ['Mr', 'Ms', 'Mrs']):
        #     if (vals.get('gender') == 'male' and vals.get('age') > 10):
        #         res['name'] = "Mr " + res['name'].capitalize()
        #         print(res['name'])
        #     elif (vals.get('gender') == 'female' and vals.get('age') > 10 and vals.get('is_married')):
        #         res['name'] = "Mrs " + res['name'].capitalize()
        #         print(res['name'])
        #     elif (vals.get('gender') == 'female' and (not vals.get('is_married'))
        #           and vals.get('age') > 10):
        #         res['name'] = "Ms " + res['name'].capitalize()
        #         print(res['name'])
        #     elif (vals.get('gender') == 'male' and vals.get('age') <= 10):
        #         res['name'] = "Master " + res['name'].capitalize()
        #         print(res['name'])
        #     elif (vals.get('gender') == 'female' and vals.get('age') <= 10):
        #         res['name'] = "Miss " + res['name'].capitalize()
        #         print(res['name'])
        #     elif (vals.get('gender') == 'others' and vals.get('age') > 10):
        #         res['name'] = "Mr " + res['name'].capitalize()
        #         print(res['name'])
        #     elif (vals.get('gender') == 'others' and vals.get('age') <= 10):
        #         res['name'] = "Master " + res['name'].capitalize()
        #         print(res['name'])
        #     else:
        #         pass
        #
        #     print('res---', res, 'self---', self, 'vals---', vals)
        #     return res

    # Overriding write method
    def write(self, vals):
        res = super(HospitalPatient, self).write(vals)
        print('written')
        print(self._context)
        return res

    # Overriding unlink method
    @check_identity
    def unlink(self):
        for i in self:
            if i.gender:
                if i.gender == "male":
                    res = super(HospitalPatient, i).unlink()
                    print(res)
                    return res
                else:
                    raise ValidationError(_("Can not delete the Record!"))

    # #read_group method
    # def demo_group_by(self):
    #     obj = self.env['hospital.patient'].read_group([], fields=['name', 'age', 'gender'],
    #                                                   groupby=['doctor'],
    #                                                   orderby='age desc', limit=2, offset=1)
    #     print(obj)

    # Age validation
    @api.constrains('is_child', 'age')
    def _check_child_age(self):
        for i in self:
            # if i.is_child and i.age == 0:
            #     raise ValidationError(_('Age has to be recorded!'))
            if i.age < 0:
                raise ValidationError(_("Age should be Greater than zero!"))

    # To give full name
    @api.depends('f_name', 'l_name', 'm_name')
    def compute_capitalized_name(self):
        for i in self:
            if i.l_name and i.m_name:
                i.capitalized_name = (str(i.f_name) + ' ' + str(i.m_name) + ' ' + str(i.l_name)).upper()
            elif i.m_name:
                i.capitalized_name = (str(i.f_name) + ' ' + str(i.m_name)).upper()
            elif i.f_name:
                i.capitalized_name = str(i.f_name).upper()
            else:
                i.capitalized_name = ''

    # To get all names
    @api.depends('capitalized_name')
    def inverse_compute_capitalized_name(self):
        for i in self:
            if i.capitalized_name:
                l = list(map(str, i.capitalized_name.lower().split(' ')))
                if len(l) == 3:
                    i.f_name, i.m_name, i.l_name = l
            else:
                pass

    @api.depends('name')
    def _search_patient(self, operator, value):
        print("iiiiiiiiiiiiiiiiiiii,search method??????????????")
        if operator not in ("ilike", "like") or not isinstance(value, str):
            print('is it here????????????????????????????')
            return [('name', operator, value)]
        print("really here???????????????????????????????")
        return ['|', ('name', operator, HospitalPatient._parse_name_search(value)),
                ('email', operator, value)]

    # Is_child and age auto
    @api.onchange('age', 'is_child')
    def _onchange_age(self):
        if self.age <= 10:
            self.is_child = True
        else:
            self.is_child = False

    # To Check and Handle Name Field
    @api.constrains('name')
    def _check_name(self):
        for i in self:
            if i.name:
                if not (re.fullmatch('[A-Za-z]+\s*[A-Za-z]*', i.name)):
                    raise ValidationError(_("Name must be alphabetical!"))

    # Email validation
    @api.constrains('email')
    def _validate_email(self):
        for i in self:
            if i.email:  # if Doctor email Field is not empty
                pd = re.fullmatch(r'^[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(i.email))
                if pd is None:  # if Not Valid Email
                    raise ValidationError(_("Email is not valid!"))

    # Age calculation
    @api.onchange('age', 'dob')
    def change_age(self):
        for i in self:
            if i.dob:
                birth_date = fields.Date.from_string(i.dob)
                current_date = fields.Date.from_string(date.today())
                age_years = current_date.year - birth_date.year
                i.age = age_years

    # To validate blood group
    @api.constrains('blood_group', 'has_rare_blood_type')
    def valid_blood_group(self):
        for i in self:
            if not i.has_rare_blood_type:
                if i.blood_group not in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
                    raise ValidationError(_('Not a valid blood group!'))

    # To validate Mobile No
    @api.constrains('mobile_no')
    def validate_mobile_no(self):
        for i in self:
            if i.mobile_no:
                r = re.fullmatch(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}", i.mobile_no)
                if r is None:
                    raise ValidationError(_("Mobile Number Is Not Valid!"))

    def action_open_case(self):
        print("fdrtrdtrdtyu0898779778[[[[[[[[[[[[[")
        return {
            'name': 'case',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hospital.case',
            'domain': [('c_ids', '=', self.id)],
            'target': 'current',
        }

    def send_on_whatsapp(self):
        print("whatsapp send...........")
        if not self.mobile_no:
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
        msg = 'Hi %s' % self.name
        phone = self.mobile_no
        if len(self.mobile_no) > 10:
            phone = self.mobile_no[-10:]
            print('phone,,,,,,,', phone)
        url = 'https://web.whatsapp.com/send?phone=%s&text=%s&app_absent=True' % (phone, msg)
        print(url, 'urlmmmmmmmmmmmmmmmmmmmmmmmmm')

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': url
        }


class PatientAddress(models.AbstractModel):
    _inherit = 'hospital.patient'
    house_no = fields.Char()
    addr1 = fields.Char()
    addr2 = fields.Char()
    zip = fields.Integer()
    country = fields.Many2one('res.country')
    p_state = fields.Many2one('res.country.state')
    city = fields.Many2one('state.city', string='City')
