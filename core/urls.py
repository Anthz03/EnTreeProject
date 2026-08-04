from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('jobs/', views.jobs_page, name='jobs_page'),
    path('jobs/<int:job_id>/', views.job_details_view, name='job_details'),
    path('matches/', views.matches_page, name='matches_page'),
    path('matches/<int:job_id>/', views.match_detail, name='match_detail'),

    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),

    path('profile/certifications/add/', views.add_certification_view, name='add_certification'),
    path('profile/certifications/<int:cert_id>/edit/', views.edit_certification_view, name='edit_certification'),
    path('profile/certifications/<int:cert_id>/delete/', views.delete_certification, name='delete_certification'),

    path('profile/skills/add/', views.add_skill_view, name='add_skill'),
    path('profile/skills/<int:applicant_skill_id>/edit/', views.edit_skill_view, name='edit_skill'),
    path('profile/skills/<int:applicant_skill_id>/delete/', views.delete_skill_view, name='delete_skill'),
]