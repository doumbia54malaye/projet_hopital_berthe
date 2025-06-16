from django.urls import path
from gestion import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patients/', views.patient_management, name='patients'),
    path('doctors/', views.doctor_management, name='doctors'),
    path('appointments/', views.appointment_management, name='appointments'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('add-appointment/', views.add_appointment, name='add_appointment'),
    path('get-slots/', views.get_available_slots, name='get_slots'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
# urls.py
    path('appointments/create/', views.create_appointment, name='create_appointment'),

]
