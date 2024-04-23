from odoo import http
from odoo.http import content_disposition, Controller, request, route
import base64
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.website.controllers.main import QueryURL
import re


# from fuzzywuzzy import process


# from odoo.addons.website.models.website import Website

# from werkzeug.exceptions import Forbidden, NotFound


class Hospital(http.Controller):

    @http.route(['/hospital/patients', '/hospital/patients/page/<int:page>',
                 '/hospital/patients/<string:sortby>',
                 '/hospital/patients/page/<int:page>/<string:sortby>',
                 '/hospital/patients/<string:list_view>',
                 '/hospital/patients/<string:list_view>/page/<int:page>',
                 ], website=True, auth='public', cors='*', methods=['GET'], csrf=True,
                save_session=False, sitemap=False, multilang=True, websocket=False)
    def hospital_patient(self, page=0, search='', list_view='', sortby='id asc', **kw):
        print("######################", search)
        order = 'id asc'
        if list_view:
            kw['list_view'] = list_view
        # fuzzy_search_term = search
        if sortby == 'name_asc':
            order = 'name asc'
        elif sortby == 'create_date_asc':
            order = 'create_date asc'
        elif sortby == 'create_date_desc':
            order = 'create_date desc'
        elif sortby == 'age_asc':
            order = 'age asc'
        elif sortby == 'age_desc':
            order = 'age desc'
        else:
            order = 'id asc'

        domain = []
        if search:
            kw['search'] = search
            domain = ['|', ('name', 'ilike', search), ('p_id', 'ilike', search)]
        print("PPPPPPP", domain)
        total_patients = request.env['hospital.patient'].search(domain, order='id')
        total_count = len(total_patients)
        per_page = 10
        print("111111111111111", total_patients)
        if sortby:
            kw['sortby'] = sortby
        else:
            kw['sortby'] = None
        base_url = f'/hospital/patients/{list_view}'
        if not list_view:
            base_url = '/hospital/patients'
        pager = request.website.pager(url=base_url, total=total_count, page=page,
                                      step=per_page, scope=3, url_args=kw)
        print("{{{{{{{", pager)
        patients = request.env['hospital.patient'].search(domain, limit=per_page,
                                                          offset=pager['offset'],
                                                          order=order)
        print("QQQQQQQQQQQQQQQ", patients)
        # if not patients:
        #     # raise NotFound
        #     return request.render('as_hospital.record_not_found', {})
        values = {
            'patients': patients,
            'pager': pager,
            'search': search,
            'search_count': total_count,
        }
        return request.render('as_hospital.patients_page', values)

    @http.route(['/hospital/cases', '/hospital/cases/page/<int:page>',
                 '/hospital/cases/<string:sortby>',
                 '/hospital/cases/page/<int:page>/<string:sortby>',
                 '/hospital/cases/<string:list_view>',
                 '/hospital/cases/<string:list_view>/page/<int:page>',
                 ], website=True, auth='public', cors='*', methods=['GET'], csrf=False)
    def hospital_case(self, page=0, search='', list_view='', sortby='id asc', **kw):
        print("######################", search)
        order = 'id asc'
        if list_view:
            kw['list_view'] = list_view
        # fuzzy_search_term = search
        if sortby == 'name_asc':
            order = 'p_name asc'
        elif sortby == 'create_date_asc':
            order = 'create_date asc'
        elif sortby == 'create_date_desc':
            order = 'create_date desc'
        elif sortby == 'age_asc':
            order = 'p_age asc'
        elif sortby == 'age_desc':
            order = 'p_age desc'
        elif sortby == 'total_asc':
            order = 'final_total asc'
        elif sortby == 'total_desc':
            order = 'final_total desc'
        elif sortby == 'progress_asc':
            order = 'progress_rate asc'
        elif sortby == 'progress_desc':
            order = 'progress_rate desc'
        else:
            order = 'id asc'
        domain = []
        if search:
            kw['search'] = search
            domain = ['|', ('p_name', 'ilike', search), ('c_id', 'ilike', search)]
        print("PPPPPPP", domain)
        total_cases = request.env['hospital.case'].search(domain, order='id')
        total_count = len(total_cases)
        per_page = 10
        print("111111111111111", total_cases)
        if sortby:
            kw['sortby'] = sortby
        else:
            kw['sortby'] = None
        base_url = f'/hospital/cases/{list_view}'
        if not list_view:
            base_url = '/hospital/cases'
        pager = request.website.pager(url=base_url, total=total_count, page=page,
                                      step=per_page, scope=3, url_args=kw)
        print("{{{{{{{", pager)
        cases = request.env['hospital.case'].search(domain, limit=per_page,
                                                    offset=pager['offset'], order=order)
        print("QQQQQQQQQQQQQQQ", cases)
        values = {
            'cases': cases,
            'pager': pager,
            'search': search,
            'search_count': total_count,
        }
        return request.render('as_hospital.cases_page', values)

    @http.route(['/hospital/doctors', '/hospital/doctors/page/<int:page>',
                 '/hospital/doctors/<string:list_view>',
                 '/hospital/doctors/<string:sortby>',
                 # '/hospital/doctors/<string:designation>',
                 '/hospital/doctors/page/<int:page>/<string:sortby>',
                 '/hospital/doctors/<string:list_view>/page/<int:page>',
                 '/hospital/doctors/speciality/<model("doctor.speciality"):speciality>',
                 '/hospital/doctors/speciality/<model("doctor.speciality"):speciality>/page/<int:page>',
                 '/hospital/doctors/speciality/<model("doctor.speciality"):speciality>/<string:list_view>',
                 '/hospital/doctors/speciality/<model("doctor.speciality"):speciality>/<string:list_view>/page/<int:page>',
                 ],
                website=True, auth='public', cors='*', methods=['GET'], csrf=False)
    def hospital_doctor(self, page=0, search='', sortby='id asc', list_view='', designation=None, speciality=None,
                        **kw):
        print("$$$$$$$$$$$$$$$$$$$$$", speciality)
        print("%%%%%%%%%%", designation)
        order = 'id asc'
        if list_view:
            kw['list_view'] = list_view
        # fuzzy_search_term = search
        if sortby == 'name_asc':
            order = 'doctor asc'
        elif sortby == 'create_date_asc':
            order = 'create_date asc'
        elif sortby == 'create_date_desc':
            order = 'create_date desc'
        elif sortby == 'salary_asc':
            order = 'salary asc'
        elif sortby == 'salary_desc':
            order = 'salary desc'
        elif sortby == 'age_asc':
            order = 'd_age asc'
        elif sortby == 'age_desc':
            order = 'd_age desc'
        elif sortby == 'rating_desc':
            order = 'rating desc'
        elif sortby == 'rating_asc':
            order = 'rating asc'
        else:
            order = 'id asc'

        # designations = [
        #     ('medical_director', 'Medical Director'), ('department_head', 'Department Head'),
        #     ('attending_physician', 'Attending Physician'), ('fellow', 'Fellow'),
        #     ('chief_resident', 'Chief Resident'), ('resident', 'Resident')
        # ]
        des_key = ['medical_director', 'department_head', 'attending_physician', 'fellow',
                   'chief_resident', 'resident']
        des_val = ['Medical Director', 'Department Head', 'Attending Physician', 'Fellow',
                   'Chief Resident', 'Resident']

        # sorted_list = {
        #     'id': {"label": _('Oldest'), 'order': 'id asc'},
        #     'create_date': {'label': _('Recent'), 'order': 'create_date'},
        #     'doctor': {'label': _('Name'), 'order': 'doctor'},
        #     'd_id': {'label': _('ID (Asc)'), 'order': 'd_id asc'},
        #     'salary': {'label': _('Salary (Highest To Lowest)'), 'order': 'salary asc'},
        #     'salary2': {'label': _('Salary (Lowest To Highest)'), 'order': 'salary desc'}
        #
        # }
        # default_order_by = sorted_list[sortby]['order']
        # kw['order'] = sortby
        domain = []
        # fuzzy_domain = []
        # website = request.env['website'].get_current_website()
        if search:
            kw['search'] = search
            print("PPPPPPPPPPPPPPPPPPPP@@@@@@", kw['search'])
            domain = ['|', ('doctor', 'ilike', search), ('d_id', 'ilike', search)]
            # fuzzy_domain = ['|', ('doctor', 'ilike', '%' + fuzzy_search_term + '%'),
            #                 ('d_id', 'ilike', '%' + fuzzy_search_term + '%')]
        else:
            kw['search'] = ''

        if designation:
            kw['designation'] = designation
            domain.append([('designation', '=', designation)])
        else:
            kw['designation'] = ''

        if speciality:
            kw['speciality'] = speciality.id
            # domain.insert(0, '|')
            domain.append(('specialist', '=', speciality.id))
            # fuzzy_domain.append(('specialist', '=', speciality.id))
        else:
            kw['speciality'] = None

        print("PPPPPPP", domain)
        total_doctors = request.env['hospital.doctor'].search(domain)
        # if not total_doctors:
        #     total_doctors = request.env['hospital.doctor'].search(fuzzy_domain)
        total_count = len(total_doctors)
        per_page = 5
        print("111111111111111", total_doctors)

        # options = {
        #     'displayDescription': True,
        #     'displayDetail': True,
        #     'displayExtraDetail': True,
        #     'displayExtraLink': True,
        #     'displayImage': True,
        #     'allowFuzzy': not kw.get('noFuzzy'),
        #     'speciality': str(speciality.id) if speciality else None,
        #     # 'tags': tags,
        #     # 'min_price': min_price / conversion_rate,
        #     # 'max_price': max_price / conversion_rate,
        #     # 'attrib_values': attrib_values,
        #     # 'display_currency': post.get('display_currency'),
        # }
        # print(options, 'lllllllllllll')
        # print(search and fuzzy_search_term)
        #####
        # count, details, fuzzy_search_term = website._search_with_fuzzy("doctors_only", search,
        #                                                                limit=None,
        #                                                                order=kw.get('order', ''),
        #                                                                options=options)
        # print("aaaaaaaaa", fuzzy_search_term)
        # search_result = details[0].get('results', request.env['hospital.doctor']).with_context(bin_size=True)
        # print(search_result,'jjjjjjjjjjjjjjj')
        print('oi', type(list_view), 'kkkkkk')
        if sortby:
            kw['sortby'] = sortby
        else:
            kw['sortby'] = None
        base_url = f'/hospital/doctors/{list_view}'
        if not list_view:
            base_url = '/hospital/doctors'
        if speciality and search:
            base_url = f'/hospital/doctors/speciality/{speciality.name}-{speciality.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count, page=page,
                                          step=per_page, scope=3,
                                          url_args=kw)
        elif search:
            print(kw, 'oooooooooooooooo')
            pager = request.website.pager(url=base_url, total=total_count, page=page,
                                          step=per_page, scope=3, url_args=kw)
        elif speciality:
            base_url = f'/hospital/doctors/speciality/{speciality.name}-{speciality.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count,
                                          page=page,
                                          step=per_page, scope=3, url_args=kw)
        else:
            pager = request.website.pager(url=base_url, total=total_count, page=page,
                                          step=per_page, scope=3, url_args=kw)
        print("{{{{{{{", pager)
        doctors = request.env['hospital.doctor'].search(domain, limit=per_page,
                                                        offset=pager['offset'],
                                                        order=order)
        # if speciality:
        #     # doctors = doctors.filtered(lambda i: speciality.id in i.specialist.ids)
        #     doctors = doctors.search([('specialist', 'in', [speciality.id])])

        groups = request.env['doctor.speciality'].search([])
        print("iiiiiiiii", groups)
        if not speciality:
            speciality = request.env['doctor.speciality']
        print("QQQQQQQQQQQQQQQ", doctors)
        # if not doctors:
        #     # raise NotFound
        #     return request.render('as_hospital.record_not_found', {})
        return request.render('as_hospital.doctors_page', {
            'doctors': doctors,
            'pager': pager,
            'groups': groups,
            'speciality': speciality,
            'search': search,
            'designations': des_key,
            'des_val': des_val,
            # 'search': fuzzy_search_term or search,
            # 'original_search': fuzzy_search_term and search,
            'search_count': total_count,
            # 'sort_by': sortby,
            # 'searchbar_sortings': sorted_list,
        })

    @http.route(['/hospital/staff', '/hospital/staff/page/<int:page>',
                 '/hospital/staff/speciality/<model("doctor.speciality"):speciality>',
                 '/hospital/staff/speciality/<model("doctor.speciality"):speciality>/page/<int:page>',
                 '/hospital/staff/speciality/<model("nurse.speciality"):speciality2>',
                 '/hospital/staff/speciality/<model("nurse.speciality"):speciality2>/page/<int:page>',
                 '/hospital/staff/<string:list_view>',
                 '/hospital/staff/<string:list_view>/page/<int:page>',
                 '/hospital/staff/<string:sortby>',
                 '/hospital/doctors/page/<int:page>/<string:sortby>',
                 '/hospital/staff/speciality/<model("doctor.speciality"):speciality>/<string:list_view>',
                 '/hospital/staff/speciality/<model("doctor.speciality"):speciality>/<string:list_view>/page/<int:page>',
                 '/hospital/staff/speciality/<model("nurse.speciality"):speciality2>/<string:list_view>',
                 '/hospital/staff/speciality/<model("nurse.speciality"):speciality2>/<string:list_view>/page/<int:page>',
                 ],
                website=True, auth='public', cors='*', methods=['GET'], csrf=False)
    def hospital_staff(self, page=0, search='', speciality=None, speciality2=None, list_view='', sortby='id asc', **kw):
        domain = []
        order = 'id asc'
        if list_view:
            kw['list_view'] = list_view
        if sortby == 'name_asc':
            order = 'name asc'
        elif sortby == 'create_date_asc':
            order = 'create_date asc'
        elif sortby == 'create_date_desc':
            order = 'create_date desc'
        elif sortby == 'salary_asc':
            order = 'salary asc'
        elif sortby == 'salary_desc':
            order = 'salary desc'
        elif sortby == 'age_asc':
            order = 's_age asc'
        elif sortby == 'age_desc':
            order = 's_age desc'
        elif sortby == 'rating_desc':
            order = 'rating desc'
        elif sortby == 'rating_asc':
            order = 'rating asc'
        else:
            order = 'id asc'
        if search:
            domain = ['|', '|', ('name', 'ilike', search), ('staff_id', 'ilike', search),
                      ('role_id', '=', search)]
            kw['search'] = search

        if speciality:
            kw['speciality'] = speciality.id
            domain.append(('d_specialist', '=', speciality.id))

        if speciality2:
            kw['speciality2'] = speciality2.id
            domain.append(('n_specialist', '=', speciality2.id))

        print("PPPPPPP", domain)
        total_staff = request.env['hospital.staff'].search(domain)
        total_count = len(total_staff)
        per_page = 5
        print("111111111111111", total_staff)
        if sortby:
            kw['sortby'] = sortby
        else:
            kw['sortby'] = None

        base_url = f'/hospital/staff/{list_view}'
        if not list_view:
            base_url = '/hospital/staff'
        if speciality and search:
            base_url = f'/hospital/staff/speciality/{speciality.name}-{speciality.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count, page=page,
                                          step=per_page, scope=3,
                                          url_args=kw)
        elif speciality2 and search:
            base_url = f'/hospital/staff/speciality/{speciality2.name}-{speciality2.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count, page=page,
                                          step=per_page, scope=3,
                                          url_args=kw)
        elif search:
            pager = request.website.pager(url=base_url, total=total_count, page=page,
                                          step=per_page, scope=3, url_args=kw)
        elif speciality:
            base_url = f'/hospital/staff/speciality/{speciality.name}-{speciality.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count,
                                          page=page,
                                          step=per_page, scope=3, url_args=kw)
        elif speciality2:
            base_url = f'/hospital/staff/speciality/{speciality2.name}-{speciality2.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count,
                                          page=page,
                                          step=per_page, scope=3, url_args=kw)
        else:
            pager = request.website.pager(url=base_url, total=total_count, page=page,
                                          step=per_page, scope=3, url_args=kw)

        # pager = request.website.pager(url=base_url, total=total_count, page=page,
        #                               step=per_page, scope=3, url_args=None)
        print("{{{{{{{", pager)
        staff = request.env['hospital.staff'].search(domain, limit=per_page,
                                                     offset=pager['offset'], order=order)
        if speciality:
            staff = staff.search([('d_specialist', 'in', [speciality.id])])
            print("hhhhh__d", staff)
        if speciality2:
            staff = staff.search([('n_specialist', 'in', [speciality2.id])])
            print("hhhhh__n", staff)

        groups = request.env['doctor.speciality'].search([])
        groups2 = request.env['nurse.speciality'].search([])

        print("iiiiiiiii", groups, groups2)
        if not speciality and not speciality2:
            speciality = request.env['doctor.speciality']
            speciality2 = request.env['nurse.speciality']

        print("QQQQQQQQQQQQQQQ", staff)
        # if not doctors:
        #     # raise NotFound
        #     return request.render('as_hospital.record_not_found', {})
        return request.render('as_hospital.staff_page', {
            'staff_member': staff,
            'search': search,
            'search_count': total_count,
            'pager': pager,
            'groups': groups,
            'speciality': speciality,
            'groups2': groups2,
            'speciality2': speciality2,
        })

    @http.route(['/hospital/nurses', '/hospital/nurses/page/<int:page>',
                 '/hospital/nurses/speciality/<model("nurse.speciality"):speciality>',
                 '/hospital/nurses/speciality/<model("nurse.speciality"):speciality>/page/<int:page>',
                 '/hospital/nurses/<string:list_view>',
                 '/hospital/nurses/<string:list_view>/page/<int:page>',
                 '/hospital/nurses/<string:sortby>',
                 '/hospital/nurses/page/<int:page>/<string:sortby>',
                 '/hospital/nurses/speciality/<model("nurse.speciality"):speciality>/<string:list_view>',
                 '/hospital/nurses/speciality/<model("nurse.speciality"):speciality>/<string:list_view>/page/<int:page>',
                 ],
                website=True, auth='public', cors='*', methods=['GET'], csrf=False)
    def hospital_nurse(self, page=0, search='', speciality=None, list_view='', sortby='id asc', **kw):
        print("$$$$$$$$$$$$$$$$$$$$$", speciality)
        order = 'id asc'
        if list_view:
            kw['list_view'] = list_view
        # fuzzy_search_term = search
        if sortby == 'name_asc':
            order = 'name asc'
        elif sortby == 'create_date_asc':
            order = 'create_date asc'
        elif sortby == 'create_date_desc':
            order = 'create_date desc'
        elif sortby == 'salary_asc':
            order = 'salary asc'
        elif sortby == 'salary_desc':
            order = 'salary desc'
        elif sortby == 'age_asc':
            order = 'n_age asc'
        elif sortby == 'age_desc':
            order = 'n_age desc'
        elif sortby == 'rating_desc':
            order = 'rating desc'
        elif sortby == 'rating_asc':
            order = 'rating asc'
        else:
            order = 'id asc'
        domain = []
        if search:
            kw['search'] = search
            domain = ['|', ('name', 'ilike', search), ('n_id', 'ilike', search)]
        if speciality:
            kw['speciality'] = speciality.id
            domain.append(('specialist', '=', speciality.id))
        print("PPPPPPP", domain)
        total_nurses = request.env['hospital.nurse'].search(domain)
        total_count = len(total_nurses)
        per_page = 5
        print("111111111111111", total_nurses)
        if sortby:
            kw['sortby'] = sortby
        else:
            kw['sortby'] = None
        base_url = f'/hospital/nurses/{list_view}'
        if not list_view:
            base_url = '/hospital/nurses'
        if speciality and search:
            base_url = f'/hospital/nurses/speciality/{speciality.name}-{speciality.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count, page=page,
                                          step=per_page, scope=3,
                                          url_args=kw)
        elif search:
            pager = request.website.pager(url=base_url, total=total_count, page=page,
                                          step=per_page, scope=3, url_args=kw)
        elif speciality:
            base_url = f'/hospital/nurses/speciality/{speciality.name}-{speciality.id}/{list_view}'
            pager = request.website.pager(url=base_url,
                                          total=total_count,
                                          page=page,
                                          step=per_page, scope=3, url_args=kw)
        else:
            pager = request.website.pager(url=base_url, total=total_count, page=page,
                                          step=per_page, scope=3, url_args=kw)
        # pager = request.website.pager(url='/hospital/nurses', total=total_count, page=page,
        #                               step=per_page, scope=3, url_args=None)
        print("{{{{{{{", pager)
        nurses = request.env['hospital.nurse'].search(domain, limit=per_page,
                                                      offset=pager['offset'], order=order)
        if speciality:
            nurses = nurses.search([('specialist', 'in', [speciality.id])])

        groups = request.env['nurse.speciality'].search([])
        print("iiiiiiiii", groups)
        if not speciality:
            speciality = request.env['nurse.speciality']
        print("QQQQQQQQQQQQQQQ", nurses)

        return request.render('as_hospital.nurses_page', {
            'nurses': nurses,
            'pager': pager,
            'groups': groups,
            'speciality': speciality,
            'search': search,
            'search_count': total_count,
        })

    @http.route(['/create_patient_form'], website=True, auth='user', cors='*', methods=['GET', 'POST'], csrf=False)
    def patient_create_form(self, **kw):
        print("%%%%%%%%%%%%%%%%%%%%%%%%")
        city = request.env['res.state.city'].search([])
        state = request.env['res.country.state'].search([])
        country = request.env['res.country'].search([])
        print(country, 'ooooooooooooooo')

        return request.render('as_hospital.create_patient_form', {
            'city_rec': city, 'state_rec': state,
            'country_rec': country,
        })

    @http.route(['/create_patient'], website=True, auth='user')
    def hospital_patient_create(self, **kw):
        print("yyyyyyyyyyyyyyyyyyyy")
        image = kw.get('image')
        if image:
            print(type(image), '***********')
            image_data = image.read() if image else None
            print(type(image_data), '77777777777')
            print(type(base64.b64encode(image_data)), '{}{}{}{}{}')
            kw.update({
                'image': base64.b64encode(image_data) if image else False
            })
        patients = request.env['hospital.patient'].create(kw)
        print("^^^^^^^^^^^", patients)
        return request.render('as_hospital.patient_submit_success', {})

    @http.route(["/hospital/patients/details/<model('hospital.patient'):patient>"], website=True, type='http',
                auth='user')
    def view_patient_details(self, patient):
        values = {'patient': patient}
        return request.render('as_hospital.patient_details', values)

    @http.route(["/hospital/cases/details/<model('hospital.case'):case>"], website=True, type='http',
                auth='user')
    def view_case_details(self, case):
        values = {'case': case}
        return request.render('as_hospital.case_details', values)

    @http.route(["/hospital/doctors/details/<model('hospital.doctor'):doctor>"], website=True, type='http',
                auth='user')
    def view_doctor_details(self, doctor):
        values = {'doctor': doctor}
        return request.render('as_hospital.doctor_details', values)

    @http.route(["/hospital/staff/details/<model('hospital.staff'):staff>"], website=True, type='http',
                auth='user')
    def view_staff_details(self, staff):
        values = {'staff': staff}
        return request.render('as_hospital.staff_details', values)

    @http.route(["/hospital/nurses/details/<model('hospital.nurse'):nurse>"], website=True, type='http',
                auth='user')
    def view_nurse_details(self, nurse):
        values = {'nurse': nurse}
        return request.render('as_hospital.nurse_details', values)

    @http.route(["/hospital/patients/print/<model('hospital.patient'):patient_id>"],
                website=True, type='http', auth='user')
    def patient_print(self, patient_id):
        print("ftydtytyftyftyftyy", patient_id)
        # active_ids = request.context.get('active_ids', [])
        # print(active_ids,'88888888888888888')
        return self._show_report(model=patient_id, report_type='pdf',
                                 report_ref='as_hospital.report_patient_details_with_cases_pdf',
                                 download=True)

    def _show_report(self, model, report_type, report_ref, download=False):
        if report_type not in ('html', 'pdf', 'text'):
            raise UserError(_("Invalid report type: %s", report_type))
        ReportAction = request.env['ir.actions.report'].sudo()
        method_name = '_render_qweb_%s' % (report_type)
        report = getattr(ReportAction, method_name)(report_ref, list(model.ids), data={'report_type': report_type})[0]
        headers = {
            'Content-Type': 'application/pdf' if report_type == 'pdf' else 'text/html',
            'Content-Length': len(report),
        }
        if report_type == 'pdf' and download:
            try:
                filename = "%s.pdf" % (re.sub('\W+', '-', model._get_report_base_filename()))
            except:
                filename = "all_records.pdf"

            headers['Content-Disposition'] = content_disposition(filename)
        return request.make_response(report, headers=list(headers.items()))

    @http.route(["/hospital/patients/print_all/<string:patient_ids>"],
                website=True, type='http', auth='user')
    def print_all_patients(self, patient_ids=None):
        print("ftydtytyftyftyftyy", patient_ids)
        if patient_ids:
            patient_ids = list(map(int, patient_ids.split(',')))
            print(patient_ids, 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            patient_ids = request.env['hospital.patient'].browse(patient_ids)
            print(patient_ids, 'ooooooooooooooooooooooooooooooooooooooo')
            return self._show_report(model=patient_ids, report_type='pdf',
                                     report_ref='as_hospital.report_patient_details_with_cases_pdf',
                                     download=True)
        else:
            return request.redirect('/hospital/patients/page/<int:page>')

    @http.route(["/hospital/cases/print_all/<string:case_ids>"],
                website=True, type='http', auth='user')
    def print_all_cases(self, case_ids=None):
        print("ftydtytyftyftyftyy", case_ids)
        if case_ids:
            case_ids = list(map(int, case_ids.split(',')))
            print(case_ids, 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            case_ids = request.env['hospital.case'].browse(case_ids)
            print(case_ids, 'ooooooooooooooooooooooooooooooooooooooo')
            return self._show_report(model=case_ids, report_type='pdf',
                                     report_ref='as_hospital.report_case_details_pdf',
                                     download=True)
        else:
            return request.redirect('/hospital/cases/page/<int:page>')

    @http.route(["/hospital/doctors/print_all/<string:doctor_ids>"],
                website=True, type='http', auth='user')
    def print_all_doctors(self, doctor_ids=None):
        print("ftydtytyftyftyftyy", doctor_ids)
        if doctor_ids:
            doctor_ids = list(map(int, doctor_ids.split(',')))
            print(doctor_ids, 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            doctor_ids = request.env['hospital.doctor'].browse(doctor_ids)
            print(doctor_ids, 'ooooooooooooooooooooooooooooooooooooooo')
            return self._show_report(model=doctor_ids, report_type='pdf',
                                     report_ref='as_hospital.report_doctor_details_pdf',
                                     download=True)
        else:
            return request.redirect(
                '/hospital/doctors/speciality/<model("doctor.speciality"):speciality>/<string:list_view>/page/<int:page>')

    @http.route(["/hospital/nurses/print_all/<string:nurse_ids>"],
                website=True, type='http', auth='user')
    def print_all_nurses(self, nurse_ids=None):
        print("ftydtytyftyftyftyy", nurse_ids)
        if nurse_ids:
            nurse_ids = list(map(int, nurse_ids.split(',')))
            print(nurse_ids, 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
            nurse_ids = request.env['hospital.nurse'].browse(nurse_ids)
            print(nurse_ids, 'ooooooooooooooooooooooooooooooooooooooo')
            return self._show_report(model=nurse_ids, report_type='pdf',
                                     report_ref='as_hospital.report_nurse_details_pdf',
                                     download=True)
        else:
            return request.redirect(
                '/hospital/nurses/speciality/<model("nurse.speciality"):speciality>/<string:list_view>/page/<int:page>')

    @http.route(["/hospital/doctors/print/<model('hospital.doctor'):doctor_id>"],
                website=True, type='http', auth='user')
    def doctor_print(self, doctor_id):
        print("ftydtytyftyftyftyy", doctor_id)
        return self._show_report(model=doctor_id, report_type='pdf',
                                 report_ref='as_hospital.report_doctor_details_with_case_pdf',
                                 download=True)

    @http.route(["/hospital/nurses/print/<model('hospital.nurse'):nurse_id>"],
                website=True, type='http', auth='user')
    def nurse_print(self, nurse_id):
        print("ftydtytyftyftyftyy", nurse_id)
        return self._show_report(model=nurse_id, report_type='pdf',
                                 report_ref='as_hospital.report_nurse_details_pdf',
                                 download=True)

    @http.route(["/hospital/cases/print/<model('hospital.case'):case_id>"],
                website=True, type='http', auth='user')
    def case_print(self, case_id):
        print("ftydtytyftyftyftyy", case_id)
        return self._show_report(model=case_id, report_type='pdf',
                                 report_ref='as_hospital.report_case_details_pdf',
                                 download=True)

    @http.route(["/hospital/cases/print_payment/<model('hospital.case'):case_id>"],
                website=True, type='http', auth='user')
    def case_payment_print(self, case_id):
        print("ftydtytyftyftyftyy", case_id)
        return self._show_report(model=case_id, report_type='pdf',
                                 report_ref='as_hospital.report_bill_payment_pdf',
                                 download=True)


class WebsiteSaleInherit(WebsiteSale):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        print("$$$$##########!!!!!!!!!!!!!Shop")

        res = super(WebsiteSaleInherit, self).shop(page, category, search, min_price, max_price,
                                                   ppg, **post)
        print("%%%%", res)
        print('@@@@', res.qcontext)
        print("context....", request.env.context)
        print("session............", request.session.uid)
        res.qcontext['uid'] = request.session.uid
        print('new context', res.qcontext)
        return res
