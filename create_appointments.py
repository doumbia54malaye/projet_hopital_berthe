# C:\Users\HP\Desktop\ghopital2\ghopital1\hopital\scripts\create_appointments.py

# Importations nécessaires
import os
import django
import datetime

# Configure Django pour que les modèles soient accessibles
# Ceci est nécessaire si vous exécutez le script en dehors de python manage.py shell
# ou python manage.py runscript
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hopital.settings')
django.setup()

# Importez vos modèles après avoir configuré Django
from gestion.models import Appointment, Patient, Doctor

def create_sample_appointments():
    print("--- Début de la création des rendez-vous factices ---")

    # Récupérez les patients et les médecins existants.
    # Assurez-vous qu'ils existent via l'admin ou en les créant dans le shell/un script précédent.
    try:
        # Pour Alice Dupont (vous avez déjà dû le créer)
        patient_alice = Patient.objects.get(phone='0708091011')
        print(f"Patient trouvé: {patient_alice}")
    except Patient.DoesNotExist:
        print("Le patient Alice Dupont (0708091011) n'existe pas. Veuillez le créer d'abord.")
        patient_alice = None

    try:
        # Pour Dr. Sophie Lefevre (vous avez déjà dû le créer)
        doctor_sophie = Doctor.objects.get(last_name='Lefevre')
        print(f"Médecin trouvé: {doctor_sophie}")
    except Doctor.DoesNotExist:
        print("Le médecin Dr. Sophie Lefevre n'existe pas. Veuillez le créer d'abord.")
        doctor_sophie = None

    if patient_alice and doctor_sophie:
        try:
            # Utilise get_or_create pour éviter les doublons si le script est exécuté plusieurs fois
            appointment1, created = Appointment.objects.get_or_create(
                patient=patient_alice,
                doctor=doctor_sophie,
                date=datetime.date(2025, 6, 18), # Date future
                time='10:30',
                defaults={ # Valeurs si le rendez-vous est créé
                    'reason': 'Contrôle annuel',
                    'status': 'Prévu'
                }
            )
            if created:
                print(f"Rendez-vous 1 créé : {appointment1}")
            else:
                print(f"Rendez-vous 1 existait déjà : {appointment1}")
        except Exception as e:
            print(f"Erreur lors de la création du rendez-vous 1 : {e}")
    else:
        print("Impossible de créer le rendez-vous 1: patient ou médecin manquant.")


    # --- Deuxième exemple de rendez-vous ---
    try:
        patient_bob = Patient.objects.get(phone='0506070809')
        print(f"Patient trouvé: {patient_bob}")
    except Patient.DoesNotExist:
        print("Le patient Bob Martin (0506070809) n'existe pas. Veuillez le créer d'abord.")
        patient_bob = None

    try:
        doctor_jean = Doctor.objects.get(last_name='Durand')
        print(f"Médecin trouvé: {doctor_jean}")
    except Doctor.DoesNotExist:
        print("Le médecin Dr. Jean Durand n'existe pas. Veuillez le créer d'abord.")
        doctor_jean = None

    if patient_bob and doctor_jean:
        try:
            appointment2, created = Appointment.objects.get_or_create(
                patient=patient_bob,
                doctor=doctor_jean,
                date=datetime.date(2025, 6, 20),
                time='14:00',
                defaults={
                    'reason': 'Consultation pédiatrique',
                    'status': 'Prévu'
                }
            )
            if created:
                print(f"Rendez-vous 2 créé : {appointment2}")
            else:
                print(f"Rendez-vous 2 existait déjà : {appointment2}")
        except Exception as e:
            print(f"Erreur lors de la création du rendez-vous 2 : {e}")
    else:
        print("Impossible de créer le rendez-vous 2: patient ou médecin manquant.")

    print("--- Fin de la création des rendez-vous factices ---")

# Appelle la fonction lorsque le script est exécuté
if __name__ == '__main__':
    create_sample_appointments()