# forms.py
from django import forms
from .models import Appointment, Patient, Consultation, Doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'reason']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['time'].widget = forms.TimeInput(attrs={'type': 'time'})

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'phone', 'gender', 'birth_date', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = [
            'doctor', 'weight', 'height', 'temperature', 
            'blood_pressure_systolic', 'blood_pressure_diastolic', 
            'heart_rate', 'symptoms', 'diagnosis', 'treatment', 'notes'
        ]
        widgets = {
            'symptoms': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Décrivez les symptômes du patient...'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Diagnostic médical...'}),
            'treatment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Traitement prescrit...'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Notes additionnelles...'}),
            'weight': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'ex: 70.5'}),
            'height': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'ex: 175.0'}),
            'temperature': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'ex: 37.2'}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'placeholder': 'ex: 120'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'placeholder': 'ex: 80'}),
            'heart_rate': forms.NumberInput(attrs={'placeholder': 'ex: 72'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Améliorer les labels
        self.fields['doctor'].label = "Médecin consultant"
        self.fields['weight'].label = "Poids (kg)"
        self.fields['height'].label = "Taille (cm)"
        self.fields['temperature'].label = "Température (°C)"
        self.fields['blood_pressure_systolic'].label = "Tension systolique"
        self.fields['blood_pressure_diastolic'].label = "Tension diastolique"
        self.fields['heart_rate'].label = "Fréquence cardiaque (bpm)"
        self.fields['symptoms'].label = "Symptômes"
        self.fields['diagnosis'].label = "Diagnostic"
        self.fields['treatment'].label = "Traitement"
        self.fields['notes'].label = "Notes"
        
        # Rendre certains champs optionnels visuellement
        for field_name in ['weight', 'height', 'temperature', 'blood_pressure_systolic', 
                          'blood_pressure_diastolic', 'heart_rate', 'notes']:
            self.fields[field_name].required = False