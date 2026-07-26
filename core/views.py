from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import DatabaseError
from decimal import Decimal, InvalidOperation
from functools import wraps
from . import db_utils

MAX_SALARY = Decimal('99999999.99')  # matches DECIMAL(10,2) column limit



def login_required_applicant(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('applicant_id'):
            messages.warning(request, "Please log in first.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    if request.session.get('applicant_id'):
        return redirect('jobs_page')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        result = db_utils.call_login(email, password)
        if result == 'Success':
            applicant = db_utils.get_applicant_by_email(email)
            request.session['applicant_id'] = applicant['applicant_id']
            request.session['applicant_name'] = f"{applicant['first_name']} {applicant['last_name']}"
            return redirect('jobs_page')
        messages.error(request, "Invalid email or password.")
    return render(request, 'core/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


@login_required_applicant
def jobs_page(request):
    min_salary_raw = request.GET.get('min_salary') or None
    max_salary_raw = request.GET.get('max_salary') or None
    industry = request.GET.get('industry') or None

    min_salary, max_salary = None, None
    validation_failed = False

    for label, raw_value in [('Min salary', min_salary_raw), ('Max salary', max_salary_raw)]:
        if raw_value:
            try:
                value = Decimal(raw_value)
                if value < 0:
                    messages.error(request, f"{label} cannot be negative.")
                    validation_failed = True
                elif value > MAX_SALARY:
                    messages.error(request, f"{label} is too large. Maximum allowed is ₱{MAX_SALARY:,.2f}.")
                    validation_failed = True
                elif label == 'Min salary':
                    min_salary = value
                else:
                    max_salary = value
            except InvalidOperation:
                messages.error(request, f"{label} must be a valid number.")
                validation_failed = True

    if validation_failed:
        return render(request, 'core/jobs_page.html', {
            'jobs': [],
            'min_salary': min_salary_raw or '',
            'max_salary': max_salary_raw or '',
            'industry': industry or '',
        })

    try:
        if min_salary or max_salary or industry:
            jobs = db_utils.filter_job_postings(min_salary, max_salary, industry)
        else:
            jobs = db_utils.get_all_job_postings()
    except DatabaseError:
        messages.error(request, "There was a problem loading job postings. Please check your filter values.")
        jobs = []

    return render(request, 'core/jobs_page.html', {
        'jobs': jobs,
        'min_salary': min_salary_raw or '',
        'max_salary': max_salary_raw or '',
        'industry': industry or '',
    })

@login_required_applicant
def matches_page(request):
    applicant_id = request.session['applicant_id']
    matches = db_utils.match_jobs_by_description(applicant_id)
    return render(request, 'core/matches_page.html', {'matches': matches})


@login_required_applicant
def match_detail(request, job_id):
    applicant_id = request.session['applicant_id']
    result = db_utils.get_matching_skills(applicant_id, job_id)
    return render(request, 'core/match_detail.html', {
        'skills': result['skills'], 'summary': result['summary'], 'job_id': job_id,
    })


@login_required_applicant
def profile_dashboard(request):
    applicant_id = request.session['applicant_id']
    profile = db_utils.get_applicant_profile(applicant_id)
    skills = db_utils.get_applicant_skills(applicant_id)
    certifications = db_utils.get_applicant_certifications(applicant_id)
    all_skills = db_utils.get_all_skills()
    return render(request, 'core/profile_dashboard.html', {
        'profile': profile, 'skills': skills,
        'certifications': certifications, 'all_skills': all_skills,
    })


@login_required_applicant
def update_profile(request):
    if request.method == 'POST':
        applicant_id = request.session['applicant_id']
        password = request.POST.get('password', '')

        if len(password) < 8 or len(password) > 20:
            messages.error(request, "Password must be between 8 and 20 characters.")
            return redirect('profile_dashboard')

        result = db_utils.update_applicant(
            applicant_id,
            request.POST.get('education_id') or None,
            request.POST.get('first_name'), request.POST.get('last_name'),
            request.POST.get('middle_name'), request.POST.get('birthdate') or None,
            request.POST.get('gender'), request.POST.get('contact_number'),
            request.POST.get('email'), request.POST.get('address'),
            request.POST.get('profile_status', 'Active'),
            password,
        )
        if result and result.get('ResultStatus') == 'Success':
            messages.success(request, "Profile updated.")
        else:
            messages.error(request, (result or {}).get('ErrorDetail', 'Profile update failed.'))
    return redirect('profile_dashboard')


@login_required_applicant
def delete_profile(request):
    applicant_id = request.session['applicant_id']
    db_utils.delete_applicant(applicant_id)
    request.session.flush()
    return redirect('login')


# Applicant Skills: Add / Edit / Delete -----------------------------------

@login_required_applicant
def add_skill_view(request):
    applicant_id = request.session['applicant_id']

    if request.method == 'POST':
        skill_id = request.POST.get('skill_id')
        description = request.POST.get('description')
        result = db_utils.insert_applicant_skill(applicant_id, skill_id, description)
        if result and result.get('ResultStatus') == 'Success':
            messages.success(request, "Skill added.")
        else:
            messages.error(request, (result or {}).get('ErrorDetail', 'Could not add skill.'))
        return redirect('profile_dashboard')

    all_skills = db_utils.get_all_skills()
    return render(request, 'core/skill_form.html', {
        'mode': 'add',
        'all_skills': all_skills,
        'skill_record': None,
    })


@login_required_applicant
def edit_skill_view(request, applicant_skill_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        result = db_utils.update_applicant_skill(applicant_skill_id, description)
        if result and result.get('ResultStatus') == 'Success':
            messages.success(request, "Skill updated.")
        else:
            messages.error(request, (result or {}).get('ErrorDetail', 'Could not update skill.'))
        return redirect('profile_dashboard')

    skill_record = db_utils.get_applicant_skill_detail(applicant_skill_id)
    return render(request, 'core/skill_form.html', {
        'mode': 'edit',
        'all_skills': None,
        'skill_record': skill_record,
    })


@login_required_applicant
def delete_skill_view(request, applicant_skill_id):
    db_utils.delete_applicant_skill(applicant_skill_id)
    messages.info(request, "Skill removed.")
    return redirect('profile_dashboard')


# TESDA Certifications: Add / Edit / Delete --------------------------------

@login_required_applicant
def add_certification_view(request):
    if request.method == 'POST':
        applicant_id = request.session['applicant_id']
        db_utils.insert_tesda_certificate(
            applicant_id,
            request.POST.get('qualification_title'),
            request.POST.get('nc_level'),
            request.POST.get('date_issued') or None,
            request.POST.get('expiry_date') or None,
            request.POST.get('issuing_body'),
            request.POST.get('certificate_number'),
        )
        messages.success(request, "Certification added.")
        return redirect('profile_dashboard')

    return render(request, 'core/certification_form.html', {
        'mode': 'add',
        'cert_record': None,
    })


@login_required_applicant
def edit_certification_view(request, cert_id):
    if request.method == 'POST':
        db_utils.update_tesda_certificate(
            cert_id,
            request.POST.get('qualification_title'),
            request.POST.get('nc_level'),
            request.POST.get('date_issued') or None,
            request.POST.get('expiry_date') or None,
            request.POST.get('issuing_body'),
            request.POST.get('certificate_number'),
        )
        messages.success(request, "Certification updated.")
        return redirect('profile_dashboard')

    cert_record = db_utils.get_tesda_certificate_detail(cert_id)
    return render(request, 'core/certification_form.html', {
        'mode': 'edit',
        'cert_record': cert_record,
    })


@login_required_applicant
def delete_certification(request, cert_id):
    db_utils.delete_tesda_certificate(cert_id)
    messages.info(request, "Certification removed.")
    return redirect('profile_dashboard')


@login_required_applicant
def job_details_view(request, job_id):
    job = db_utils.get_job_details(job_id)
    return render(request, 'core/job_details.html', {'job': job})