# appointments/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Home Page
    path('', views.home, name='home'),

    # User's Portal (Visitor's End)
    path('create_appointment/', views.create_appointment, name='create_appointment'),
    path('departments/', views.department_list, name='department_list'),

    # Hospital's Portal (Admin's End)
    path('appointments/', views.appointment_list, name='appointment_list'),
     path('get_doctors/<int:department_id>/', views.get_doctors, name='get_doctors'),
     path('success/<int:token_number>/', views.appointment_success, name='appointment_success'),  # URL pattern accepts token_number
]