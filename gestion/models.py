# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone 
from datetime import date

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrateur'),
        ('doctor', 'Médecin'),
        ('staff', 'Personnel'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
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

    def age(self):
        if not self.birth_date:
            return None # Pas de date de naissance, pas d'âge
        today = date.today()
        # Calcul simple de l'âge
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    

class Doctor(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='doctor_profile'
    )
    specialty = models.CharField(max_length=100)
    availability = models.JSONField(default=dict)

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
        return f"Dr. {self.user.last_name}"

class Consultation(models.Model):
    """Modèle pour enregistrer les consultations médicales"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations')
    
    # Signes vitaux
    weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Poids (kg)", null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taille (cm)", null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="Température (°C)", null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(verbose_name="Tension artérielle systolique", null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(verbose_name="Tension artérielle diastolique", null=True, blank=True)
    heart_rate = models.IntegerField(verbose_name="Fréquence cardiaque (bpm)", null=True, blank=True)
    
    # Informations cliniques
    symptoms = models.TextField(verbose_name="Symptômes", blank=True)
    diagnosis = models.TextField(verbose_name="Diagnostic", blank=True)
    treatment = models.TextField(verbose_name="Traitement prescrit", blank=True)
    notes = models.TextField(verbose_name="Notes additionnelles", blank=True)
    
    # Métadonnées
    consultation_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-consultation_date']
        verbose_name = "Consultation"
        verbose_name_plural = "Consultations"

    def __str__(self):
        return f"Consultation de {self.patient} avec {self.doctor} le {self.consultation_date.strftime('%d/%m/%Y')}"

    @property
    def blood_pressure(self):
        """Retourne la tension artérielle formatée"""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return "Non renseignée"

    @property
    def bmi(self):
        """Calcule l'IMC si le poids et la taille sont disponibles"""
        if self.weight and self.height:
            height_m = float(self.height) / 100  # Conversion cm -> m
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

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
    consultation = models.OneToOneField(Consultation, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rdv {self.patient} avec {self.doctor} le {self.date} à {self.time}"