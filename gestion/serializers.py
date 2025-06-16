# gestion/serializers.py
from rest_framework import serializers
from .models import Patient, Doctor, Appointment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    patient_first_name = serializers.CharField(source='patient.first_name', read_only=True)
    patient_last_name = serializers.CharField(source='patient.last_name', read_only=True)
    doctor_first_name = serializers.CharField(source='doctor.first_name', read_only=True)
    doctor_last_name = serializers.CharField(source='doctor.last_name', read_only=True)
    doctor_specialty = serializers.CharField(source='doctor.specialty', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__' # Include all fields including the ones from related models
        # Make sure 'patient' and 'doctor' are writeable when creating/updating
        read_only_fields = ['created_at']