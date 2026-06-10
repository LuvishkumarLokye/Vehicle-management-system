from django.contrib import admin
from .models import vehicle, repairs, appointements,oil_change

# Register your models here.
admin.site.register(vehicle)
admin.site.register(repairs)
admin.site.register(appointements)
admin.site.register(oil_change)
