from rest_framework import serializers

from .models import appointements, oil_change, repairs, vehicle


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = vehicle
        fields = '__all__'


class RepairsSerializer(serializers.ModelSerializer):
    class Meta:
        model = repairs
        fields = '__all__'


class OilChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = oil_change
        fields = '__all__'


class AppointementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = appointements
        fields = '__all__'
