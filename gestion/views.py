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

logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def add_appointment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    try:
        # Récupérer les données envoyées par le formulaire AJAX
        patient_id = request.POST.get('patient_id')
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        reason = request.POST.get('reason')

        # === LOG DE DÉBOGAGE ESSENTIEL ===
        # Ceci affichera dans votre console serveur exactement ce qui a été reçu.
        logger.info(f"Tentative d'ajout de RDV. Données reçues: {request.POST.dict()}")

        # Vérification plus stricte
        if not all([patient_id, doctor_id, date_str, time_str, reason]):
            missing_fields = [
                field for field, value in {
                    "patient_id": patient_id, "doctor": doctor_id, 
                    "date": date_str, "time": time_str, "reason": reason
                }.items() if not value
            ]
            logger.error(f"Échec de création de RDV. Champs manquants: {missing_fields}")
            # Le message d'erreur est plus précis maintenant
            return JsonResponse({
                'success': False, 
                'message': f'Champ(s) manquant(s) : {", ".join(missing_fields)}'
            }, status=400)

        # Conversion et validation des données
        doctor = get_object_or_404(Doctor, id=doctor_id)
        patient = get_object_or_404(Patient, id=patient_id)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()

        # Vérifier si le créneau est encore disponible
        if Appointment.objects.filter(doctor=doctor, date=date_obj, time=time_obj).exists():
            return JsonResponse({'success': False, 'message': 'Ce créneau est déjà réservé.'})

        # Création du rendez-vous
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date_obj,
            time=time_obj,
            reason=reason
        )
        
        logger.info("Rendez-vous créé avec succès.")
        return JsonResponse({'success': True, 'message': 'Rendez-vous enregistré avec succès'})

    except (Doctor.DoesNotExist, Patient.DoesNotExist):
        logger.error("Patient ou Médecin non trouvé.", exc_info=True)
        return JsonResponse({'success': False, 'message': 'Patient ou Médecin invalide.'}, status=404)
    except ValueError as e:
        logger.error(f"Erreur de format de date ou d'heure: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'Format de date ou d\'heure invalide.'}, status=400)
    except Exception as e:
        logger.error(f"Erreur interne lors de la création du rendez-vous: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': 'Une erreur interne est survenue.'}, status=500)
    
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
        if not availability or not availability.get('start') or not availability.get('end'):
            return JsonResponse({'slots': []})

        start_time = datetime.strptime(availability['start'], '%H:%M').time()
        end_time = datetime.strptime(availability['end'], '%H:%M').time()

        slots = []
        current = datetime.combine(date_obj, start_time)
        end = datetime.combine(date_obj, end_time)

        while current < end:
            # Créneau de 30 minutes
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
    doctors = Doctor.objects.select_related('user').all()
    context = {'patients': patients, 'doctors': doctors}
    return render(request, 'gestion/patients.html', context)
    
@login_required
def save_patient_and_consultation(request):
    """
    API: Sauvegarde un nouveau patient et sa première consultation,
    OU modifie les informations d'un patient existant.
    Répond à la requête POST de la grande modale.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)

    try:
        with transaction.atomic():
            # ... (Toute la logique de création/modification du patient reste la même)
            patient_id = request.POST.get('patient_id')
            
            birth_date_str = request.POST.get('birth_date')
            birth_date_obj = None
            if birth_date_str:
                try:
                    birth_date_obj = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({'success': False, 'message': 'Format de date de naissance invalide. Utilisez AAAA-MM-JJ.'}, status=400)

            patient_data = {
                'first_name': request.POST.get('first_name', '').strip(),
                'last_name': request.POST.get('last_name', '').strip(),
                'phone': request.POST.get('phone', '').strip(),
                'gender': request.POST.get('gender'),
                'birth_date': birth_date_obj,
                'address': request.POST.get('address', '').strip(),
            }

            if patient_id:
                patient = get_object_or_404(Patient, id=patient_id)
                for key, value in patient_data.items():
                    setattr(patient, key, value)
                patient.save()
                action_message = 'Patient modifié avec succès'
            else:
                patient = Patient.objects.create(**patient_data)
                action_message = 'Patient créé avec succès'

            # --- DÉBUT DE LA SECTION CORRIGÉE POUR LA CONSULTATION ---

            # On vérifie si une consultation doit être créée (par ex, si des symptômes sont fournis)
            symptoms = request.POST.get('symptoms', '').strip()
            if symptoms: # ou une autre condition de votre choix
                doctor_id = request.POST.get('doctor')
                if not doctor_id:
                    return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un médecin pour la consultation.'}, status=400)
                
                doctor = get_object_or_404(Doctor, id=doctor_id)

                # Fonction utilitaire pour convertir les chaînes vides en None
                def to_none(val):
                    return val if val else None

                consultation_data = {
                    'patient': patient,
                    'doctor': doctor,
                    
                    # Signes vitaux (convertir les chaînes vides en None)
                    'weight': to_none(request.POST.get('weight')),
                    'height': to_none(request.POST.get('height')),
                    'temperature': to_none(request.POST.get('temperature')),
                    'blood_pressure_systolic': to_none(request.POST.get('blood_pressure_systolic')),
                    'blood_pressure_diastolic': to_none(request.POST.get('blood_pressure_diastolic')),
                    'heart_rate': to_none(request.POST.get('heart_rate')),
                    
                    # Informations cliniques (les chaînes vides sont acceptées par `blank=True`)
                    'symptoms': symptoms,
                    'diagnosis': request.POST.get('diagnosis', '').strip(),
                    'treatment': request.POST.get('treatment', '').strip(),
                    'notes': request.POST.get('notes', '').strip(),
                    
                    # Métadonnées (gérées automatiquement ou explicitement)
                    'consultation_date': timezone.now(),
                }
                Consultation.objects.create(**consultation_data)
                action_message = 'Patient et consultation enregistrés avec succès'
            
            # --- FIN DE LA SECTION CORRIGÉE ---

            patient_json = {
                'id': patient.id,
                'first_name': patient.first_name,
                'last_name': patient.last_name,
                'phone': patient.phone,
                'gender_display': patient.get_gender_display(),
                'birth_date': patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else '',
                'address': patient.address,
            }
            return JsonResponse({'success': True, 'message': action_message, 'patient': patient_json})
            
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Le médecin sélectionné n\'existe pas.'}, status=404)
    except Exception as e:
        import logging
        logging.error(f"Erreur lors de la sauvegarde du patient/consultation: {e}", exc_info=True)
        return JsonResponse({'success': False, 'message': f'Erreur interne du serveur: {str(e)}'}, status=500)

@login_required
def add_consultation(request):
    """API: Ajouter une consultation à un patient existant."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    
    try:
        patient_id = request.POST.get('patient_id')
        if not patient_id:
            return JsonResponse({'success': False, 'message': 'ID du patient manquant.'}, status=400)
        
        doctor_id = request.POST.get('doctor')
        if not doctor_id:
            return JsonResponse({'success': False, 'message': 'Veuillez sélectionner un médecin.'}, status=400)

        patient = get_object_or_404(Patient, id=patient_id)
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Fonction utilitaire pour convertir les chaînes vides en None
        def to_none(val):
            return val if val and str(val).strip() else None

        # Créez le dictionnaire de données, comme nous l'avions fait avant
        consultation_data = {
            'patient': patient,
            'doctor': doctor,
            
            # Signes vitaux (convertir les chaînes vides en None)
            'weight': to_none(request.POST.get('weight')),
            'height': to_none(request.POST.get('height')),
            'temperature': to_none(request.POST.get('temperature')),
            'blood_pressure_systolic': to_none(request.POST.get('blood_pressure_systolic')),
            'blood_pressure_diastolic': to_none(request.POST.get('blood_pressure_diastolic')),
            'heart_rate': to_none(request.POST.get('heart_rate')),
            
            # Informations cliniques
            'symptoms': request.POST.get('symptoms', '').strip(),
            'diagnosis': request.POST.get('diagnosis', '').strip(),
            'treatment': request.POST.get('treatment', '').strip(),
            'notes': request.POST.get('notes', '').strip(),
            
            # La date est gérée par le modèle, mais il est bon d'être explicite
            'consultation_date': timezone.now(),
        }

        # Créer la consultation en utilisant le dictionnaire "nettoyé"
        Consultation.objects.create(**consultation_data)
        
        return JsonResponse({'success': True, 'message': 'Consultation enregistrée avec succès'})

    except Patient.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Le patient spécifié n\'existe pas.'}, status=404)
    except Doctor.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Le médecin sélectionné n\'existe pas.'}, status=404)
    except Exception as e:
        # Pour le débogage, il est crucial de logger l'erreur réelle
        import logging
        logging.error(f"Erreur lors de l'ajout de la consultation: {e}", exc_info=True)
        # Ne retournez pas l'erreur brute à l'utilisateur en production
        return JsonResponse({'success': False, 'message': 'Une erreur interne est survenue.'}, status=500)


@login_required
def delete_patient(request, patient_id):
    """API: Supprimer un patient. Attend une méthode DELETE."""
    # Note: On change la méthode attendue de POST à DELETE pour être plus correct
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'message': 'Méthode DELETE requise'}, status=405)
    
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        patient.delete()
        return JsonResponse({'success': True, 'message': 'Patient supprimé avec succès'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
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
    
@login_required
def get_doctor_availability_dates(request, doctor_id):
    """
    API: Renvoie une liste de dates disponibles pour un médecin donné
    pour les 90 prochains jours.
    """
    try:
        doctor = get_object_or_404(Doctor, id=doctor_id)
        availability_data = doctor.availability or {}
        
        # Mappage des noms de jours français aux numéros de jour de la semaine de Python (lundi=0)
        day_mapping = {
            'Lundi': 0, 'Mardi': 1, 'Mercredi': 2, 'Jeudi': 3, 
            'Vendredi': 4, 'Samedi': 5, 'Dimanche': 6
        }
        
        # Obtenir les numéros des jours où le médecin travaille
        available_weekdays = [day_mapping[day] for day in availability_data.keys() if day in day_mapping]
        
        if not available_weekdays:
            return JsonResponse({'available_dates': []})

        available_dates = []
        today = date.today()
        # On vérifie sur une période de 90 jours
        for i in range(90):
            current_date = today + timedelta(days=i)
            if current_date.weekday() in available_weekdays:
                available_dates.append(current_date.strftime('%Y-%m-%d'))
                
        return JsonResponse({'success': True, 'available_dates': available_dates})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@login_required
def get_patient_data_for_edit(request, patient_id):
    """API: Récupérer les données d'un patient pour pré-remplir le formulaire de modification."""
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

@login_required
def get_patient_details(request, patient_id):
    """API: Récupérer les détails complets d'un patient et son historique de consultations."""
    patient = get_object_or_404(Patient, id=patient_id)
    consultations = Consultation.objects.filter(patient=patient).select_related('doctor__user').order_by('-consultation_date')
    
    consultations_list = [{
        'date': c.consultation_date.strftime('%d/%m/%Y %H:%M'),
        'doctor_name': f"{c.doctor.user.first_name} {c.doctor.user.last_name}",
        'symptoms': c.symptoms,
        'diagnosis': c.diagnosis,
        # Ajoutez d'autres champs si nécessaire
    } for c in consultations]
    
    data = {
        'first_name': patient.first_name,
        'last_name': patient.last_name,
        'phone': patient.phone,
        'gender_display': patient.get_gender_display(),
        'birth_date': patient.birth_date.strftime('%d/%m/%Y'),
        'age': patient.age(), # Assurez-vous d'avoir une méthode age() dans votre modèle Patient
        'address': patient.address,
        'consultations': consultations_list
    }
    return JsonResponse({'success': True, 'data': data})

