# C:\Users\HP\Desktop\ghopital2\ghopital1\hopital\scripts\create_appointments.py

import os
import sys
import django
import datetime
from datetime import timedelta # Pour faciliter l'ajout de dates

# Ajoutez le répertoire parent (la racine du projet Django) au chemin de recherche Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Configure Django pour que les modèles soient accessibles
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopital.settings')
django.setup()

# Importez vos modèles après avoir configuré Django
from gestion.models import Appointment, Patient, Doctor

def create_sample_data():
    print("--- Début de la création/mise à jour des données factices ---")

    # --- Création de Patients ---
    print("\n--- Création/Vérification des Patients ---")
    patients_data = [
        {'first_name': 'Alice', 'last_name': 'Dupont', 'phone': '0708091011', 'gender': 'F', 'birth_date': '1990-05-15', 'address': '123 Rue de la Paix, Paris'},
        {'first_name': 'Bob', 'last_name': 'Martin', 'phone': '0506070809', 'gender': 'M', 'birth_date': '1985-11-22', 'address': '456 Avenue des Roses, Lyon'},
        {'first_name': 'Clara', 'last_name': 'Bernard', 'phone': '0612345678', 'gender': 'F', 'birth_date': '1995-03-10', 'address': '789 Boulevard des Fleurs, Marseille'},
        {'first_name': 'David', 'last_name': 'Dubois', 'phone': '0723456789', 'gender': 'M', 'birth_date': '1978-08-01', 'address': '10 Rue du Soleil, Toulouse'},
        {'first_name': 'Emma', 'last_name': 'Petit', 'phone': '0534567890', 'gender': 'F', 'birth_date': '2000-01-20', 'address': '22 Avenue de la Liberté, Nice'},
    ]

    patients = {}
    for data in patients_data:
        # Utilisez get_or_create pour ne pas créer de doublons si le patient existe déjà
        patient, created = Patient.objects.get_or_create(
            phone=data['phone'], # Utilise le numéro de téléphone comme clé unique
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'gender': data['gender'],
                'birth_date': datetime.datetime.strptime(data['birth_date'], '%Y-%m-%d').date(),
                'address': data['address']
            }
        )
        patients[data['last_name'].lower()] = patient # Stocke par nom de famille pour un accès facile
        if created:
            print(f"Patient créé : {patient}")
        else:
            print(f"Patient existant : {patient}")

    # --- Création de Médecins ---
    print("\n--- Création/Vérification des Médecins ---")
    doctors_data = [
        {'first_name': 'Sophie', 'last_name': 'Lefevre', 'specialty': 'Cardiologie', 'phone': '0123456789', 'availability': {"Lundi": "09:00-17:00", "Mardi": "09:00-12:00", "Jeudi": "13:00-18:00"}},
        {'first_name': 'Jean', 'last_name': 'Durand', 'specialty': 'Pédiatrie', 'phone': '0698765432', 'availability': {"Mercredi": "10:00-16:00", "Vendredi": "09:00-17:00"}},
        {'first_name': 'Marc', 'last_name': 'Garcia', 'specialty': 'Généraliste', 'phone': '0234567890', 'availability': {"Lundi": "08:30-12:00", "Mardi": "14:00-18:00", "Jeudi": "09:00-17:00"}},
        {'first_name': 'Laura', 'last_name': 'Moreau', 'specialty': 'Dermatologie', 'phone': '0789012345', 'availability': {"Mardi": "09:00-17:00", "Mercredi": "09:00-12:00", "Vendredi": "13:00-17:00"}},
    ]

    doctors = {}
    for data in doctors_data:
        doctor, created = Doctor.objects.get_or_create(
            last_name=data['last_name'], # Utilise le nom de famille comme clé unique (attention si plusieurs ont le même nom)
            first_name=data['first_name'], # Ajoute first_name pour éviter les conflits si plusieurs médecins ont le même nom de famille
            defaults={
                'specialty': data['specialty'],
                'phone': data['phone'],
                'availability': data['availability']
            }
        )
        doctors[data['last_name'].lower()] = doctor
        if created:
            print(f"Médecin créé : {doctor}")
        else:
            print(f"Médecin existant : {doctor}")

    # --- Création de Rendez-vous ---
    print("\n--- Création/Vérification des Rendez-vous ---")
    today = datetime.date.today() # Date d'aujourd'hui

    appointments_data = [
        # Rendez-vous Passé
        {'patient': patients.get('dupont'), 'doctor': doctors.get('lefevre'), 'date_offset': -30, 'time': '10:30', 'reason': 'Contrôle annuel (passé)', 'status': 'Terminé'},
        # Rendez-vous Aujourd'hui
        {'patient': patients.get('bernard'), 'doctor': doctors.get('garcia'), 'date_offset': 0, 'time': '11:00', 'reason': 'Consultation générale', 'status': 'Prévu'},
        # Rendez-vous Futur (dans 7 jours)
        {'patient': patients.get('dubois'), 'doctor': doctors.get('durand'), 'date_offset': 7, 'time': '14:00', 'reason': 'Suivi pédiatrique', 'status': 'Prévu'},
        # Autre Rendez-vous Futur (dans 15 jours)
        {'patient': patients.get('petit'), 'doctor': doctors.get('moreau'), 'date_offset': 15, 'time': '09:00', 'reason': 'Problème de peau', 'status': 'Prévu'},
        # Un autre rendez-vous pour Alice
        {'patient': patients.get('dupont'), 'doctor': doctors.get('garcia'), 'date_offset': 5, 'time': '15:00', 'reason': 'Renouvellement ordonnance', 'status': 'Prévu'},
        # Un rendez-vous annulé
        {'patient': patients.get('martin'), 'doctor': doctors.get('moreau'), 'date_offset': 2, 'time': '10:00', 'reason': 'Rendez-vous annulé', 'status': 'Annulé'},
    ]

    for data in appointments_data:
        patient = data['patient']
        doctor = data['doctor']
        appt_date = today + timedelta(days=data['date_offset']) # Calculer la date

        if patient and doctor:
            try:
                appointment, created = Appointment.objects.get_or_create(
                    patient=patient,
                    doctor=doctor,
                    date=appt_date,
                    time=data['time'],
                    defaults={
                        'reason': data['reason'],
                        'status': data['status']
                    }
                )
                if created:
                    print(f"Rendez-vous créé : {appointment}")
                else:
                    print(f"Rendez-vous existant : {appointment}")
            except Exception as e:
                print(f"Erreur lors de la création du rendez-vous ({data['reason']}) : {e}")
        else:
            print(f"Impossible de créer le rendez-vous '{data['reason']}': patient ou médecin manquant.")

    print("\n--- Fin de la création/mise à jour des données factices ---")

if __name__ == '__main__':
    create_sample_data()