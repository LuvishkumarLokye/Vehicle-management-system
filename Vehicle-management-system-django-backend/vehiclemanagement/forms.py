
from django import forms
from .models import vehicle, appointements

class VehicleForm(forms.ModelForm):
    class Meta:
        model=vehicle
        fields=['customer_name','customer_phone_number','vehicle_regis_number','current_milleage']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model=appointements
        fields=['vehicle','date','time','mechanic_name','status']
