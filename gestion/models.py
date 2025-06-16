from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('doctor', 'Médecin'),
        ('staff', 'Personnel'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Ajoutez ces propriétés pour faciliter l'accès
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre'),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField()
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# gestion/models.py
class Doctor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile',
        # Remove: null=True, 
        # Remove: blank=True 
    )
    specialty = models.CharField(max_length=100)
    availability = models.JSONField(default=dict)

    # Vos propriétés @property peuvent rester telles quelles car self.user sera toujours présent
    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def phone(self):
        return self.user.phone

    @property
    def email(self):
        return self.user.email

    def __str__(self):
        # Plus besoin de vérification ici car self.user ne sera jamais None
        return f"Dr. {self.user.last_name}"




class Appointment(models.Model):
    STATUS_CHOICES = (
        ('scheduled', 'Programmé'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rdv {self.patient} avec {self.doctor} le {self.date} à {self.time}"