import os
import django
import sys
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialisation de Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hopital.settings")
django.setup()

from gestion.models import User, Doctor, Patient, Appointment

fake = Faker(locale='fr_FR')

# Nettoyage (optionnel pour les tests)
# User.objects.all().delete()
# Doctor.objects.all().delete()
# Patient.objects.all().delete()
# Appointment.objects.all().delete()

def create_doctors(n=5):
    doctors = []
    for i in range(n):
        username = f"medecin{i}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "phone": fake.phone_number(),
                "role": "doctor",
                "email": fake.email(),
                "password": "password"
            }
        )
        if created:
            user.set_password("password")
            user.save()
        doctor, _ = Doctor.objects.get_or_create(
            user=user,
            defaults={"specialty": fake.job(), "availability": {}}
        )
        doctors.append(doctor)
    return doctors

def create_patients(n=20):
    patients = []
    for _ in range(n):
        patient = Patient.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            phone=fake.phone_number(),
            gender=random.choice(['M', 'F']),
            birth_date=fake.date_of_birth(minimum_age=1, maximum_age=90),
            address=fake.address()
        )
        patients.append(patient)
    return patients

def create_appointments(patients, doctors, n=30):
    for _ in range(n):
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        date = datetime.now().date() + timedelta(days=random.randint(0, 30))
        time = (datetime.min + timedelta(minutes=random.randint(480, 1080))).time()  # entre 8h et 18h
        Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            date=date,
            time=time,
            reason=fake.text(max_nb_chars=50),
            status=random.choice(['scheduled', 'completed', 'cancelled']),
        )

def populate_all():
    print("Création des médecins...")
    doctors = create_doctors(5)
    print("Création des patients...")
    patients = create_patients(20)
    print("Création des rendez-vous...")
    create_appointments(patients, doctors, 30)
    print("Données insérées avec succès.")

if __name__ == "__main__":
    populate_all()
