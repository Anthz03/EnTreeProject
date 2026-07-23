from django.db import models


class ApplicantsProfile(models.Model):
    applicant_id = models.AutoField(primary_key=True)
    education_id = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    contact_number = models.CharField(max_length=11, null=True, blank=True)
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)
    profile_status = models.CharField(max_length=10, default='Active')
    password = models.CharField(max_length=20)
    date_registered = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Applicants_Profile'


class Skill(models.Model):
    skill_id = models.AutoField(primary_key=True)
    skill_name = models.CharField(max_length=100)
    skill_type = models.CharField(max_length=20, null=True, blank=True)
    category = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Skills'


class ApplicantSkill(models.Model):
    applicant_skill_id = models.AutoField(primary_key=True)
    applicant_id = models.IntegerField()
    description = models.CharField(max_length=255, null=True, blank=True)
    skill_id = models.IntegerField()
    date_added = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Applicant_Skills'


class JobPosting(models.Model):
    job_id = models.AutoField(primary_key=True)
    employer_id = models.IntegerField()
    job_title = models.CharField(max_length=150)
    job_description = models.TextField(null=True, blank=True)
    education_required = models.CharField(max_length=15, null=True, blank=True)
    strand_required = models.CharField(max_length=50, null=True, blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=15, null=True, blank=True)
    status = models.CharField(max_length=10, default='Open')
    date_posted = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'Job_Postings'