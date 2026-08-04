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



def get_job_details(job_id):
    """EXEC uspViewJobDetails -- full job posting + employer details."""
    with connection.cursor() as cursor:
        cursor.execute("EXEC uspViewJobDetails @JobID=%s", [job_id])
        return _dictfetchone(cursor)

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
        return _dictfetchone(cursor)


def insert_applicant_skill(applicant_id, skill_id, description):
    """EXEC usp_ManageApplicantSkill @Action='INSERT'"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            EXEC usp_ManageApplicantSkill
                @Action='INSERT', @ApplicantID=%s, @SkillID=%s, @Description=%s
            """,
            [applicant_id, skill_id, description]
        )
        return _dictfetchone(cursor)


def update_applicant_skill(applicant_skill_id, description):
    """EXEC usp_ManageApplicantSkill @Action='UPDATE'"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            EXEC usp_ManageApplicantSkill
                @Action='UPDATE', @ApplicantSkillID=%s, @Description=%s
            """,
            [applicant_skill_id, description]
        )
        return _dictfetchone(cursor)


def delete_applicant_skill(applicant_skill_id):
    """EXEC usp_ManageApplicantSkill @Action='DELETE'"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC usp_ManageApplicantSkill @Action='DELETE', @ApplicantSkillID=%s",
            [applicant_skill_id]
        )
        return _dictfetchone(cursor)


def get_applicant_profile(applicant_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Applicants_Profile WHERE applicant_id = %s", [applicant_id])
        return _dictfetchone(cursor)


def get_applicant_skills(applicant_id):
    """EXEC usp_GetApplicantSkills"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC uspGetApplicantSkills @ApplicantID = %s",
            [applicant_id]
        )
        return _dictfetchall(cursor)


def get_all_skills():
    with connection.cursor() as cursor:
        cursor.execute("SELECT skill_id, skill_name, skill_type, category FROM Skills ORDER BY category, skill_name")
        return _dictfetchall(cursor)


def get_applicant_skill_detail(applicant_skill_id):
    """EXEC usp_GetApplicantSkillDetail -- pre-fills the Edit Skill page."""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC usp_GetApplicantSkillDetail @ApplicantSkillID=%s",
            [applicant_skill_id]
        )
        return _dictfetchone(cursor)


# TESDA Certifications ---------------------------------------------------

def get_tesda_certificate_detail(cert_id):
    """EXEC usp_GetTesdaCertificationDetail -- pre-fills the Edit Certificate page."""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC usp_GetTesdaCertificationDetail @CertID=%s",
            [cert_id]
        )
        return _dictfetchone(cursor)


def insert_tesda_certificate(applicant_id, qualification_title, nc_level,
                              date_issued, expiry_date, issuing_body, certificate_number):
    """EXEC usp_ManageTesdaCertification @Action='INSERT'"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            EXEC usp_ManageTesdaCertification
                @Action='INSERT', @ApplicantID=%s, @QualificationTitle=%s, @NCLevel=%s,
                @DateIssued=%s, @ExpiryDate=%s, @IssuingBody=%s, @CertificateNumber=%s
            """,
            [applicant_id, qualification_title, nc_level, date_issued,
             expiry_date, issuing_body, certificate_number]
        )
        return _dictfetchone(cursor)


def update_tesda_certificate(cert_id, qualification_title, nc_level,
                              date_issued, expiry_date, issuing_body, certificate_number):
    """EXEC usp_ManageTesdaCertification @Action='UPDATE'"""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            EXEC usp_ManageTesdaCertification
                @Action='UPDATE', @CertID=%s, @QualificationTitle=%s, @NCLevel=%s,
                @DateIssued=%s, @ExpiryDate=%s, @IssuingBody=%s, @CertificateNumber=%s
            """,
            [cert_id, qualification_title, nc_level, date_issued,
             expiry_date, issuing_body, certificate_number]
        )
        return _dictfetchone(cursor)


def delete_tesda_certificate(cert_id):
    """EXEC usp_ManageTesdaCertification @Action='DELETE'"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC usp_ManageTesdaCertification @Action='DELETE', @CertID=%s",
            [cert_id]
        )
        return _dictfetchone(cursor)


def get_applicant_certifications(applicant_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM TESDA_Certification_Ownerships WHERE applicant_id = %s",
            [applicant_id]
        )
        return _dictfetchall(cursor)



