from django.contrib import admin
from .models import Patient, Doctor, Appointment, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'phone')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('role',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'gender', 'birth_date')
    search_fields = ('first_name', 'last_name', 'phone')
    list_filter = ('gender',)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    # Utilisez les propriétés définies dans le modèle
    list_display = ('get_first_name', 'get_last_name', 'specialty', 'get_phone')
    search_fields = ('user__first_name', 'user__last_name', 'specialty')
    
    # Définissez des méthodes pour accéder aux propriétés
    def get_first_name(self, obj):
        return obj.first_name
    get_first_name.short_description = 'Prénom'
    get_first_name.admin_order_field = 'user__first_name'
    
    def get_last_name(self, obj):
        return obj.last_name
    get_last_name.short_description = 'Nom'
    get_last_name.admin_order_field = 'user__last_name'
    
    def get_phone(self, obj):
        return obj.phone
    get_phone.short_description = 'Téléphone'
    get_phone.admin_order_field = 'user__phone'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__first_name', 'patient__last_name', 'doctor__user__last_name')
    date_hierarchy = 'date'