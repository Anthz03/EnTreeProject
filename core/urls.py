from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('jobs/', views.jobs_page, name='jobs_page'),
    path('matches/', views.matches_page, name='matches_page'),
    path('matches/<int:job_id>/', views.match_detail, name='match_detail'),

    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('profile/certifications/add/', views.add_certification, name='add_certification'),
    path('profile/certifications/<int:cert_id>/update/', views.update_certification, name='update_certification'),
    path('profile/certifications/<int:cert_id>/delete/', views.delete_certification, name='delete_certification'),
]