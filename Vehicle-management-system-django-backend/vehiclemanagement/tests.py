import json

from django.test import TestCase
from django.urls import reverse

from .models import appointements, oil_change, repairs, vehicle


class OilChangeMileageValidationTests(TestCase):
    def setUp(self):
        self.vehicle = vehicle.objects.create(
            customer_name='Test Customer',
            customer_phone_number='123456789',
            vehicle_regis_number='ABC-1234',
            current_milleage=50000,
        )

    def test_new_oil_change_mileage_cannot_be_less_than_current_mileage(self):
        response = self.client.post(reverse('vehiclemanagement:update_mileage'), {
            'vehicle_regis_number': self.vehicle.vehicle_regis_number,
            'new_mileage': '49999',
        })

        self.assertContains(response, 'Oil change mileage cannot be less than current mileage')
        self.assertEqual(oil_change.objects.count(), 0)

    def test_new_oil_change_mileage_can_equal_current_mileage(self):
        response = self.client.post(reverse('vehiclemanagement:update_mileage'), {
            'vehicle_regis_number': self.vehicle.vehicle_regis_number,
            'new_mileage': '50000',
        })

        self.assertContains(response, 'Oil change scheduled for mileage: 50000 km')
        self.assertEqual(oil_change.objects.count(), 1)


class RepairPageTests(TestCase):
    def setUp(self):
        self.vehicle = vehicle.objects.create(
            customer_name='Test Customer',
            customer_phone_number='123456789',
            vehicle_regis_number='ABC-1234',
            current_milleage=50000,
        )

    def test_can_add_repair_record_from_repair_page(self):
        response = self.client.post(reverse('vehiclemanagement:repairpage'), {
            'vehicle_regis_number': self.vehicle.vehicle_regis_number,
            'description': 'Changed brake pads',
            'costs': '1500.00',
        })

        self.assertContains(response, 'Repair record added successfully')
        self.assertContains(response, 'Changed brake pads')
        self.assertEqual(repairs.objects.count(), 1)


class AppointmentSlotTests(TestCase):
    def setUp(self):
        self.vehicle = vehicle.objects.create(
            customer_name='Test Customer',
            customer_phone_number='123456789',
            vehicle_regis_number='ABC-1234',
            current_milleage=50000,
        )

    def test_duplicate_appointment_slot_is_rejected(self):
        appointements.objects.create(
            vehicle=self.vehicle,
            date='2026-06-10',
            time_slot='09:00',
        )

        response = self.client.post(reverse('vehiclemanagement:appointment-list'), {
            'vehicle': self.vehicle.vehicle_regis_number,
            'date': '2026-06-10',
            'time_slot': '09:00',
        })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'already booked', status_code=400)


class VehicleMileageUpdateTests(TestCase):
    def setUp(self):
        self.vehicle = vehicle.objects.create(
            customer_name='Test Customer',
            customer_phone_number='123456789',
            vehicle_regis_number='ABC-1234',
            current_milleage=50000,
        )

    def test_vehicle_mileage_cannot_go_backwards(self):
        response = self.client.patch(
            reverse('vehiclemanagement:vehicle-detail', kwargs={'pk': self.vehicle.vehicle_regis_number}),
            data=json.dumps({'current_milleage': 49000}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'cannot be less than the current mileage', status_code=400)
