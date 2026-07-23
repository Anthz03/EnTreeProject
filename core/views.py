from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from . import db_utils


def login_required_applicant(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('applicant_id'):
            messages.warning(request, "Please log in first.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
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
    min_salary = request.GET.get('min_salary') or None
    max_salary = request.GET.get('max_salary') or None
    industry = request.GET.get('industry') or None

    if min_salary or max_salary or industry:
        jobs = db_utils.filter_job_postings(min_salary, max_salary, industry)
    else:
        jobs = db_utils.get_all_job_postings()

    return render(request, 'core/jobs_page.html', {
        'jobs': jobs, 'min_salary': min_salary or '',
        'max_salary': max_salary or '', 'industry': industry or '',
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
        db_utils.update_applicant(
            applicant_id,
            request.POST.get('education_id') or None,
            request.POST.get('first_name'), request.POST.get('last_name'),
            request.POST.get('middle_name'), request.POST.get('birthdate') or None,
            request.POST.get('gender'), request.POST.get('contact_number'),
            request.POST.get('email'), request.POST.get('address'),
            request.POST.get('profile_status', 'Active'),
            request.POST.get('password'),
        )
        messages.success(request, "Profile updated.")
    return redirect('profile_dashboard')


@login_required_applicant
def delete_profile(request):
    applicant_id = request.session['applicant_id']
    db_utils.delete_applicant(applicant_id)
    request.session.flush()
    return redirect('login')


@login_required_applicant
def add_certification(request):
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


@login_required_applicant
def update_certification(request, cert_id):
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


@login_required_applicant
def delete_certification(request, cert_id):
    db_utils.delete_tesda_certificate(cert_id)
    messages.info(request, "Certification removed.")
    return redirect('profile_dashboard')