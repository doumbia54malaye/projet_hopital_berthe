from django.urls import path
from gestion import views
from .views import *
 
urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
     # Gestion des patients et consultations
    path('patients/', views.patient_management, name='patients'),
    path('patients/save/', views.save_patient_and_consultation, name='save_patient_and_consultation'),
    path('consultations/add/', views.add_consultation, name='add_consultation'),
    path('patients/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),
    
    # URLs optionnelles pour des fonctionnalités avancées
    path('patients/<int:patient_id>/details/', views.get_patient_details, name='get_patient_details'),
    path('patients/<int:patient_id>/consultations/', views.patient_consultations, name='patient_consultations'),
    path('api/doctors/', views.get_doctors_list, name='get_doctors_list'),
    path('doctors/', views.doctor_management, name='doctors'),
    path('appointments/', views.appointment_management, name='appointments'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('add-appointment/', views.add_appointment, name='add_appointment'),
    path('get-slots/', views.get_available_slots, name='get_slots'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
# urls.py
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/get/<int:appointment_id>/', views.get_appointment_details, name='get_appointment_details'),
    path('appointments/update/<int:appointment_id>/', views.update_appointment, name='update_appointment'),

]
