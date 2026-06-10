from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import appointements, oil_change, repairs, vehicle
from .serializers import (
    AppointementsSerializer,
    OilChangeSerializer,
    RepairsSerializer,
    VehicleSerializer,
)


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = vehicle.objects.all()
    serializer_class = VehicleSerializer

    def _update_vehicle(self, request, partial=False):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_milleage = serializer.validated_data.get('current_milleage')
        if new_milleage is not None and new_milleage < instance.current_milleage:
            return Response(
                {
                    'current_milleage': (
                        'Updated mileage cannot be less than the current mileage '
                        f'({instance.current_milleage} km).'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_update(serializer)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        return self._update_vehicle(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        return self._update_vehicle(request, partial=True)

    @action(detail=True, methods=['get'])
    def repairs(self, request, pk=None):
        vehicle_instance = self.get_object()
        repair_records = repairs.objects.filter(vehicle=vehicle_instance).order_by('-date_changed')
        serializer = RepairsSerializer(repair_records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def oil_changes(self, request, pk=None):
        vehicle_instance = self.get_object()
        oil_change_records = oil_change.objects.filter(vehicle=vehicle_instance).order_by('-date_changed')
        serializer = OilChangeSerializer(oil_change_records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        vehicle_instance = self.get_object()
        # FIXED: Use 'time' (not 'time_slot') and order by date and time
        appointment_records = appointements.objects.filter(vehicle=vehicle_instance).order_by('-date', '-time')
        serializer = AppointementsSerializer(appointment_records, many=True)
        return Response(serializer.data)


class RepairsViewSet(viewsets.ModelViewSet):
    queryset = repairs.objects.select_related('vehicle').all().order_by('-date_changed')
    serializer_class = RepairsSerializer


class OilChangeViewSet(viewsets.ModelViewSet):
    queryset = oil_change.objects.select_related('vehicle').all().order_by('-date_changed')
    serializer_class = OilChangeSerializer

    def create(self, request, *args, **kwargs):
        vehicle_regis_number = request.data.get('vehicle')
        new_milleage = request.data.get('new_milleage')

        try:
            vehicle_instance = vehicle.objects.get(pk=vehicle_regis_number)
        except vehicle.DoesNotExist:
            return Response(
                {'vehicle': 'Vehicle not found.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_milleage_value = int(new_milleage)
        except (TypeError, ValueError):
            return Response(
                {'new_milleage': 'Mileage must be a number.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_milleage_value < vehicle_instance.current_milleage:
            return Response(
                {
                    'new_milleage': (
                        'Oil change mileage cannot be less than current mileage '
                        f'({vehicle_instance.current_milleage} km).'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class AppointementsViewSet(viewsets.ModelViewSet):
    # FIXED: Use 'time' (not 'time_slot') for ordering
    queryset = appointements.objects.select_related('vehicle').all().order_by('-date', '-time')
    serializer_class = AppointementsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment_date = serializer.validated_data['date']
        # FIXED: Use 'time' (not 'time_slot')
        appointment_time = serializer.validated_data['time']

        # FIXED: Use 'time' (not 'time_slot') in filter
        if appointements.objects.filter(date=appointment_date, time=appointment_time).exists():
            return Response(
                {'detail': 'This date and time slot is already booked. Please book next week.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)