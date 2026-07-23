from django.db import connection


def _dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _dictfetchone(cursor):
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# 1. Applicant Login Session -------------------------------------------

def call_login(email, password):
    """EXEC uspLogin -- returns 'Success' or 'Fail'."""
    with connection.cursor() as cursor:
        cursor.execute("EXEC uspLogin @Email = %s, @Password = %s", [email, password])
        row = cursor.fetchone()
        return row[0] if row else 'Fail'


def get_applicant_by_email(email):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT applicant_id, first_name, last_name, email "
            "FROM Applicants_Profile WHERE email = %s", [email]
        )
        return _dictfetchone(cursor)


# 2. Jobs Page, Matching Engine & Salary Filtering ----------------------

def get_all_job_postings():
    """SELECT * FROM vwJobPostings"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vwJobPostings")
        return _dictfetchall(cursor)


def filter_job_postings(min_salary=None, max_salary=None, industry=None):
    """SELECT * FROM udfFilterJobPostings(...)"""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM udfFilterJobPostings(%s, %s, %s)",
            [min_salary, max_salary, industry]
        )
        return _dictfetchall(cursor)


def create_job_post(employer_id, job_title, job_description, education_required,
                     strand_required, salary_min, salary_max, job_type,
                     skill_ids_csv, is_required='Required'):
    """EXEC uspCreateJobPost"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            EXEC uspCreateJobPost
                @EmployerID=%s, @JobTitle=%s, @JobDescription=%s,
                @EducationRequired=%s, @StrandRequired=%s,
                @SalaryMin=%s, @SalaryMax=%s, @JobType=%s,
                @SkillIDs=%s, @IsRequired=%s
            """,
            [employer_id, job_title, job_description, education_required,
             strand_required, salary_min, salary_max, job_type,
             skill_ids_csv, is_required]
        )
        return _dictfetchone(cursor)  # ResultStatus, JobID


def get_matching_skills(applicant_id, job_id):
    """EXEC uspViewMatchingSkills -- two result sets: skills + summary."""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspViewMatchingSkills @ApplicantID=%s, @JobID=%s",
            [applicant_id, job_id]
        )
        skills = _dictfetchall(cursor)
        summary = None
        if cursor.nextset():
            summary = _dictfetchone(cursor)
        return {'skills': skills, 'summary': summary}


def match_jobs_by_description(applicant_id):
    """EXEC uspMatchJobsByDescription"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspMatchJobsByDescription @ApplicantID=%s",
            [applicant_id]
        )
        return _dictfetchall(cursor)


# 3. Profile Management Dashboard ---------------------------------------

def insert_applicant(education_id, first_name, last_name, middle_name, birthdate,
                      gender, contact_number, email, address, profile_status, password):
    """EXEC uspInsertApplicant"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspInsertApplicant %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s",
            [education_id, first_name, last_name, middle_name, birthdate,
             gender, contact_number, email, address, profile_status, password]
        )


def update_applicant(applicant_id, education_id, first_name, last_name, middle_name,
                      birthdate, gender, contact_number, email, address,
                      profile_status, password):
    """EXEC uspUpdateApplicant"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspUpdateApplicant %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s",
            [applicant_id, education_id, first_name, last_name, middle_name,
             birthdate, gender, contact_number, email, address,
             profile_status, password]
        )


def delete_applicant(applicant_id):
    """EXEC uspDeleteApplicant"""
    with connection.cursor() as cursor:
        cursor.execute("EXEC uspDeleteApplicant %s", [applicant_id])


def get_applicant_profile(applicant_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Applicants_Profile WHERE applicant_id = %s", [applicant_id])
        return _dictfetchone(cursor)


def get_applicant_skills(applicant_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT aps.applicant_skill_id, aps.description, aps.date_added,
                   s.skill_id, s.skill_name, s.skill_type, s.category
            FROM Applicant_Skills aps
            INNER JOIN Skills s ON aps.skill_id = s.skill_id
            WHERE aps.applicant_id = %s
            """, [applicant_id]
        )
        return _dictfetchall(cursor)


def get_all_skills():
    with connection.cursor() as cursor:
        cursor.execute("SELECT skill_id, skill_name, skill_type, category FROM Skills ORDER BY category, skill_name")
        return _dictfetchall(cursor)


# TESDA Certifications ---------------------------------------------------

def insert_tesda_certificate(applicant_id, qualification_title, nc_level,
                              date_issued, expiry_date, issuing_body, certificate_number):
    """EXEC uspInsertTESDACertificate"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspInsertTESDACertificate %s, %s, %s, %s, %s, %s, %s",
            [applicant_id, qualification_title, nc_level, date_issued,
             expiry_date, issuing_body, certificate_number]
        )


def update_tesda_certificate(cert_id, qualification_title, nc_level,
                              date_issued, expiry_date, issuing_body, certificate_number):
    """EXEC uspUpdateTESDACertificate"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspUpdateTESDACertificate %s, %s, %s, %s, %s, %s, %s",
            [cert_id, qualification_title, nc_level, date_issued,
             expiry_date, issuing_body, certificate_number]
        )


def delete_tesda_certificate(cert_id):
    """EXEC uspDeleteTESDACertificate"""
    with connection.cursor() as cursor:
        cursor.execute("EXEC uspDeleteTESDACertificate %s", [cert_id])


def get_applicant_certifications(applicant_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM TESDA_Certification_Ownerships WHERE applicant_id = %s",
            [applicant_id]
        )
        return _dictfetchall(cursor)