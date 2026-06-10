from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views, views

app_name = 'vehiclemanagement'

#apis
router = DefaultRouter()
router.register('vehicles', api_views.VehicleViewSet, basename='vehicle')
router.register('repairs', api_views.RepairsViewSet, basename='repair')
router.register('oil-changes', api_views.OilChangeViewSet, basename='oil-change-api')
router.register('appointments', api_views.AppointementsViewSet, basename='appointment')

urlpatterns = [
    path('', views.vehiclelist, name='vehiclelist'),
    path('invoice/<str:vehicle_regis_number>/', views.generate_invoice, name='generate_invoice'),
    path('oil-change/', views.oil_change_query_page, name='oil-change'),
    path('oil-change/update-mileage/', views.update_vehicle_mileage, name='update_mileage'),
    path('api/oil-change/<str:vehicle_regis_number>/', views.getoilchange, name='getoilchange'),
    path('api/', include(router.urls)),
    path('repairpage/', views.showrepairs, name='repairpage'),
    path('appointment/', views.appointment_query, name='appointment'),
    
    # NEW appointment URLs
    path('appointment/create/', views.create_appointment, name='create_appointment'),
    path('appointment/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    
]
