# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import Patient, Doctor, Appointment, User
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import get_object_or_404
from django.contrib import messages

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('login-username')
        password = request.POST.get('login-password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'gestion/login.html', {
                'error': 'Nom d\'utilisateur ou mot de passe incorrect'
            })
    return render(request, 'gestion/login.html')


@login_required
def dashboard(request):
    today = date.today()
    # Ajout de days_of_week
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    context = {
        'today_appointments': Appointment.objects.filter(date=today).count(),
        'available_doctors': Doctor.objects.count(),
        'total_patients': Patient.objects.count(),
        'upcoming_appointments': Appointment.objects.filter(date__gt=today).count(),
        'upcoming_appointments_list': Appointment.objects.filter(date__gte=today)
                                         .order_by('date', 'time')[:5],
        'days_of_week': days_of_week # Ligne ajoutée
    }
    return render(request, 'gestion/dashboard.html', context)

@login_required
def patient_management(request):
    patients = Patient.objects.all()
    # Ajout de days_of_week
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    context = {
        'patients': patients,
        'days_of_week': days_of_week # Ligne ajoutée
    }
    return render(request, 'gestion/patients.html', context)






@login_required
def doctor_management(request):
    doctors = Doctor.objects.all()
    # Ajout de days_of_week
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    context = {
        'doctors': doctors,
        'days_of_week': days_of_week # Ligne ajoutée
    }
    return render(request, 'gestion/doctors.html', context)



# views.py
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Appointment, Patient, Doctor
from datetime import datetime

@login_required
def create_appointment(request):
    if request.method == "POST":
        patient_id = request.POST.get("appointment-patient")
        doctor_id = request.POST.get("appointment-doctor")
        date = request.POST.get("appointment-date")
        time_str = request.POST.get("time-slot")  # format attendu : 'HH:MM'
        reason = request.POST.get("appointment-reason")

        if all([patient_id, doctor_id, date, time_str, reason]):
            try:
                patient = Patient.objects.get(id=patient_id)
                doctor = Doctor.objects.get(id=doctor_id)
                # Conversion du créneau horaire string -> TimeField compatible
                time_obj = datetime.strptime(time_str, "%H:%M").time()

                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    date=date,
                    time=time_obj,
                    reason=reason
                )
                messages.success(request, "Rendez-vous enregistré avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur : {str(e)}")
        else:
            messages.error(request, "Tous les champs sont requis.")

    return redirect("appointment_management")  # ou le nom exact de ta vue principale




@login_required
def appointment_management(request):
    today = date.today()
    patients = Patient.objects.all()
    doctors = Doctor.objects.all()
    # Ajout de days_of_week (c'est la vue qui a généré l'erreur)
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    context = {
                      
        'doctors': doctors,   
        'patients': patients,

        'today_appointments': Appointment.objects.filter(date=today),
        'upcoming_appointments': Appointment.objects.filter(date__gt=today),
        'all_appointments': Appointment.objects.all(),
        'days_of_week': days_of_week # Ligne ajoutée
    }
    return render(request, 'gestion/appointments.html', context)

@login_required
def calendar_view(request):
    # Ajout de days_of_week
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    context = {
        'days_of_week': days_of_week # Ligne ajoutée
    }
    return render(request, 'gestion/calendar.html', context)

@csrf_exempt
@login_required
def add_patient(request):
    # Log des données reçues pour debug
    print("POST data received:", dict(request.POST))

    if request.method == 'POST':
        try:
            patient = Patient.objects.create(
                first_name=request.POST.get('patient-firstname'),
                last_name=request.POST.get('patient-lastname'),
                phone=request.POST.get('patient-phone'),
                gender=request.POST.get('patient-gender'),
                birth_date=request.POST.get('patient-birthdate'),
                address=request.POST.get('patient-address')
            )
            return JsonResponse({'success': True, 'patient_id': patient.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
@login_required
def add_doctor(request):
    if request.method == 'POST':
        try:
            logger.info("POST data received for add_doctor: %s", dict(request.POST))
            # Créer l'utilisateur d'abord
            username = f"{request.POST.get('doctor-firstname').lower()}.{request.POST.get('doctor-lastname').lower()}"
            logger.info("Username generated: %s", username)
            user = User.objects.create_user(
                username=username,
                password='defaultpassword',
                first_name=request.POST.get('doctor-firstname'),
                last_name=request.POST.get('doctor-lastname'),
                phone=request.POST.get('doctor-phone'),
                role='doctor'
            )
            logger.info("User created with id: %s", user.id)

            # Extraire les disponibilités
            availability = {}
            days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
            for day in days:
                if request.POST.get(f'avail-{day}') == 'on':
                    start_time = request.POST.get(f'{day}-start')
                    end_time = request.POST.get(f'{day}-end')
                    availability[day.capitalize()] = {"start": start_time, "end": end_time}
            logger.info("Availability parsed: %s", availability)

            doctor = Doctor.objects.create(
                user=user,
                specialty=request.POST.get('doctor-specialty'),
                availability=availability
            )
            logger.info("Doctor created with id: %s", doctor.id)
            return JsonResponse({'success': True, 'doctor_id': doctor.id})
        except Exception as e:
            logger.error("Erreur lors de l'ajout du médecin: %s", str(e), exc_info=True)
            return JsonResponse({'success': False, 'error': str(e)})
    logger.warning("Méthode non autorisée pour add_doctor: %s", request.method)
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@csrf_exempt
@login_required
def add_appointment(request):
    if request.method == 'POST':
        try:
            patient_id = request.POST.get('appointment-patient')
            doctor_id = request.POST.get('appointment-doctor')
            date_str = request.POST.get('appointment-date')
            time_str = request.POST.get('time-slot')

            time_obj = datetime.strptime(time_str, '%H:%M').time()

            appointment = Appointment.objects.create(
                patient_id=patient_id,
                doctor_id=doctor_id,
                date=date_str,
                time=time_obj,
                reason=request.POST.get('appointment-reason')
            )
            return JsonResponse({'success': True, 'appointment_id': appointment.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
def get_available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    try:
        doctor = Doctor.objects.get(id=doctor_id)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        weekday = date_obj.weekday()
        days_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        day_name = days_fr[weekday]

        availability = doctor.availability.get(day_name)
        if not availability:
            return JsonResponse({'slots': []})

        start_time = datetime.strptime(availability['start'], '%H:%M').time()
        end_time = datetime.strptime(availability['end'], '%H:%M').time()

        slots = []
        current = datetime.combine(date_obj, start_time)
        end = datetime.combine(date_obj, end_time)

        while current < end:
            if not Appointment.objects.filter(
                doctor=doctor,
                date=date_obj,
                time=current.time()
            ).exists():
                slots.append(current.strftime('%H:%M'))

            current += timedelta(minutes=30)

        return JsonResponse({'slots': slots})

    except Exception as e:
        return JsonResponse({'slots': [], 'error': str(e)})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def get_patients(request):
    patients = list(Patient.objects.values('id', 'first_name', 'last_name'))
    return JsonResponse(patients, safe=False)

@login_required
def get_doctors(request):
    doctors = list(Doctor.objects.values('id', 'user__first_name', 'user__last_name', 'specialty'))
    return JsonResponse(doctors, safe=False)


@csrf_exempt
@login_required
def delete_appointment(request, appointment_id):
    if request.method == 'POST':
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@login_required
def get_appointment_details(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        return JsonResponse({
            'success': True,
            'patient_id': appointment.patient.id,
            'doctor_id': appointment.doctor.id,
            'date': appointment.date.strftime('%Y-%m-%d'),
            'time': appointment.time.strftime('%H:%M'),
            'reason': appointment.reason
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def update_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False, 
                'errors': form.errors.as_json()
            }, status=400)
    
    # Préparation des données pour la modale
    appointment_data = {
        'id': appointment.id,
        'patient_id': appointment.patient.id,
        'doctor_id': appointment.doctor.id,
        'date': appointment.date.strftime('%Y-%m-%d'),
        'time': appointment.time.strftime('%H:%M'),
        'reason': appointment.reason,
    }
    
    return JsonResponse({'success': True, 'appointment': appointment_data})