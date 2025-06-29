# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date
import json
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import *
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal, InvalidOperation




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
def doctor_management(request):
    doctors = Doctor.objects.all()
    # Ajout de days_of_week
    days_of_week = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    context = {
        'doctors': doctors,
        'days_of_week': days_of_week # Ligne ajoutée
    }
    return render(request, 'gestion/doctors.html', context)

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

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#gestion des patients et consultations
@login_required
def patient_management(request):
    """Vue principale pour la gestion des patients"""
    patients = Patient.objects.all().order_by('-created_at')
    # Récupérer tous les utilisateurs avec le rôle 'doctor'
    doctors = Doctor.objects.select_related('user').all()
    
    context = {
        'patients': patients,
        'doctors': doctors,
    }
    return render(request, 'gestion/patients.html', context)

@csrf_exempt
@login_required
def save_patient_and_consultation(request):
    """Sauvegarde patient et consultation (nouveau patient + consultation OU modification patient)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
    
    try:
        with transaction.atomic():
            patient_id = request.POST.get('patient_id')
            
            # Données patient
            patient_data = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'phone': request.POST.get('phone', '').strip(),
                'gender': request.POST.get('gender'),
                'birth_date': request.POST.get('birth_date'),
                'address': request.POST.get('address', '').strip(),
            }
            
            # Validation des champs obligatoires
            required_fields = ['first_name', 'last_name', 'phone', 'gender', 'birth_date']
            missing_fields = [field for field in required_fields if not patient_data.get(field)]
            if missing_fields:
                return JsonResponse({
                    'success': False, 
                    'error': f'Champs obligatoires manquants: {", ".join(missing_fields)}'
                })
            
            # Validation de la date de naissance
            try:
                datetime.strptime(patient_data['birth_date'], '%Y-%m-%d')
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Format de date invalide'})
            
            # Créer ou modifier le patient
            if patient_id:  # Modification d'un patient existant
                patient = get_object_or_404(Patient, id=patient_id)
                for key, value in patient_data.items():
                    setattr(patient, key, value)
                patient.save()
                message = 'Patient modifié avec succès'
                
                # Si c'est juste une modification patient, on s'arrête là
                if not request.POST.get('symptoms'):  # Pas de données de consultation
                    return JsonResponse({'success': True, 'message': message})
            else:  # Nouveau patient
                patient = Patient.objects.create(**patient_data)
                message = 'Patient et consultation créés avec succès'
            
            # Données consultation (seulement si des symptômes sont fournis)
            symptoms = request.POST.get('symptoms', '').strip()
            if symptoms:  # Il y a des données de consultation
                doctor_id = request.POST.get('doctor')
                if not doctor_id:
                    return JsonResponse({'success': False, 'error': 'Médecin consultant requis pour la consultation'})
                
                doctor = get_object_or_404(Doctor, id=doctor_id)
                
                # Créer la consultation
                consultation_data = {
                    'patient': patient,
                    'doctor': doctor,
                    'symptoms': symptoms,
                    'diagnosis': request.POST.get('diagnosis', '').strip(),
                    'treatment': request.POST.get('treatment', '').strip(),
                    'notes': request.POST.get('notes', '').strip(),
                    'consultation_date': timezone.now(),
                }
                
                # Signes vitaux (optionnels) - conversion en Decimal pour les champs DecimalField
                vital_signs_data = {}
                
                # Champs Decimal
                decimal_fields = ['weight', 'height', 'temperature']
                for field in decimal_fields:
                    value = request.POST.get(field)
                    if value:
                        try:
                            vital_signs_data[field] = Decimal(str(value))
                        except (InvalidOperation, ValueError):
                            # Ignorer les valeurs invalides plutôt que de faire échouer toute l'opération
                            pass
                
                # Champs Integer
                integer_fields = ['blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate']
                for field in integer_fields:
                    value = request.POST.get(field)
                    if value:
                        try:
                            vital_signs_data[field] = int(value)
                        except ValueError:
                            # Ignorer les valeurs invalides
                            pass
                
                consultation_data.update(vital_signs_data)
                Consultation.objects.create(**consultation_data)
            
            return JsonResponse({'success': True, 'message': message, 'patient_id': patient.id})
            
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        print(f"Erreur lors de la sauvegarde: {e}")  # Pour le debug
        return JsonResponse({'success': False, 'error': 'Erreur interne du serveur'})

@csrf_exempt
@login_required
def add_consultation(request):
    """Ajouter une consultation à un patient existant"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
    
    try:
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor')
        symptoms = request.POST.get('symptoms', '').strip()
        
        # Validations
        if not patient_id:
            return JsonResponse({'success': False, 'error': 'ID patient manquant'})
        if not doctor_id:
            return JsonResponse({'success': False, 'error': 'Médecin consultant requis'})
        if not symptoms:
            return JsonResponse({'success': False, 'error': 'Symptômes requis'})
        
        patient = get_object_or_404(Patient, id=patient_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)
        
        # Créer la consultation
        consultation_data = {
            'patient': patient,
            'doctor': doctor,
            'symptoms': symptoms,
            'diagnosis': request.POST.get('diagnosis', '').strip(),
            'treatment': request.POST.get('treatment', '').strip(),
            'notes': request.POST.get('notes', '').strip(),
            'consultation_date': timezone.now(),
        }
        
        # Signes vitaux (optionnels)
        vital_signs_data = {}
        
        # Champs Decimal
        decimal_fields = ['weight', 'height', 'temperature']
        for field in decimal_fields:
            value = request.POST.get(field)
            if value:
                try:
                    vital_signs_data[field] = Decimal(str(value))
                except (InvalidOperation, ValueError):
                    pass
        
        # Champs Integer
        integer_fields = ['blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate']
        for field in integer_fields:
            value = request.POST.get(field)
            if value:
                try:
                    vital_signs_data[field] = int(value)
                except ValueError:
                    pass
        
        consultation_data.update(vital_signs_data)
        consultation = Consultation.objects.create(**consultation_data)
        
        return JsonResponse({
            'success': True, 
            'message': 'Consultation créée avec succès',
            'consultation_id': consultation.id
        })
        
    except Exception as e:
        print(f"Erreur lors de la création de consultation: {e}")
        return JsonResponse({'success': False, 'error': 'Erreur interne du serveur'})

@csrf_exempt
@login_required
def delete_patient(request, patient_id):
    """Supprimer un patient et toutes ses consultations"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        patient_name = f"{patient.first_name} {patient.last_name}"
        
        # Django supprimera automatiquement les consultations liées grâce aux foreign keys
        patient.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Patient {patient_name} supprimé avec succès'
        })
        
    except Exception as e:
        print(f"Erreur lors de la suppression: {e}")
        return JsonResponse({'success': False, 'error': 'Erreur lors de la suppression'})

# Vue optionnelle pour récupérer les détails d'un patient (si besoin)
@login_required
def get_patient_details(request, patient_id):
    """Récupérer les détails d'un patient en JSON"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        data = {
            'id': patient.id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'phone': patient.phone,
            'gender': patient.gender,
            'birth_date': patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else '',
            'address': patient.address,
        }
        return JsonResponse({'success': True, 'patient': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Vue pour récupérer l'historique des consultations d'un patient
@login_required
def patient_consultations(request, patient_id):
    """Récupérer l'historique des consultations d'un patient"""
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        consultations = Consultation.objects.filter(patient=patient).select_related('doctor__user').order_by('-consultation_date')
        
        consultations_data = []
        for consultation in consultations:
            consultations_data.append({
                'id': consultation.id,
                'date': consultation.consultation_date.strftime('%Y-%m-%d %H:%M'),
                'doctor': f"Dr. {consultation.doctor.user.first_name} {consultation.doctor.user.last_name}",
                'specialty': consultation.doctor.specialty,
                'symptoms': consultation.symptoms,
                'diagnosis': consultation.diagnosis,
                'treatment': consultation.treatment,
                'weight': str(consultation.weight) if consultation.weight else None,
                'height': str(consultation.height) if consultation.height else None,
                'temperature': str(consultation.temperature) if consultation.temperature else None,
                'blood_pressure': consultation.blood_pressure,
                'heart_rate': consultation.heart_rate,
                'bmi': consultation.bmi,
            })
        
        return JsonResponse({
            'success': True, 
            'patient': f"{patient.first_name} {patient.last_name}",
            'consultations': consultations_data
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Vue pour obtenir la liste des médecins (utile pour les select AJAX)
@login_required
def get_doctors_list(request):
    """Récupérer la liste des médecins disponibles"""
    try:
        doctors = Doctor.objects.select_related('user').all()
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'id': doctor.id,
                'name': f"Dr. {doctor.user.first_name} {doctor.user.last_name}",
                'specialty': doctor.specialty,
                'phone': doctor.user.phone,
            })
        
        return JsonResponse({
            'success': True,
            'doctors': doctors_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})