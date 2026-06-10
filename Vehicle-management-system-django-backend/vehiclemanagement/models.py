
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class vehicle(models.Model):
    customer_name=models.CharField(max_length=100)
    customer_phone_number=models.CharField(max_length=9)
    vehicle_regis_number=models.CharField(max_length=30, primary_key=True)
    current_milleage=models.IntegerField()

    def __str__(self):
        return self.vehicle_regis_number

class repairs(models.Model):
    description=models.TextField()
    costs=models.DecimalField(max_digits=10, decimal_places=2)
    vehicle=models.ForeignKey(vehicle,on_delete=models.CASCADE)
    date_changed=models.DateTimeField(auto_now_add=True)

class oil_change(models.Model):
    new_milleage=models.IntegerField()
    vehicle=models.ForeignKey(vehicle,on_delete=models.CASCADE)
    date_changed=models.DateTimeField(auto_now_add=True)

class appointements(models.Model):
    STATUS_CHOICES=[
        ('Pending','Pending'),
        ('Confirmed','Confirmed'),
        ('Completed','Completed'),
    ]
    vehicle=models.ForeignKey(vehicle,on_delete=models.CASCADE)
    date=models.DateField()
    time=models.TimeField()
    mechanic_name=models.CharField(max_length=100, default='Unassigned')
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def clean(self):
        if self.date < date.today():
            raise ValidationError("Cannot book appointments in the past.")
