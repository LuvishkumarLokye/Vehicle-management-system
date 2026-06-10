from django.shortcuts import render, redirect, get_object_or_404
from .models import vehicle, repairs, appointements, oil_change
from django.http import HttpRequest, JsonResponse, FileResponse
from .forms import VehicleForm
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from decimal import Decimal
import json
import tempfile
from weasyprint import HTML
from django.template.loader import render_to_string





# Create your views here.

#displaying vehicle model in front end
def vehiclelist(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehiclemanagement:vehiclelist') 
    else:
        form = VehicleForm()

    db_vehicle = vehicle.objects.all()
    context = {
        'form': form,
        'db_vehicle': db_vehicle,
        'db_empty': not db_vehicle.exists(),
        'message': 'no customers found'
    }
    return render(request, 'vehicle_management.html', context)


#api endpoints which returns json data , takes vehicle regis from url process query and then return json data
def getoilchange(request, vehicle_regis_number):
    try:
        oilchange_instance = oil_change.objects.get(vehicle__vehicle_regis_number=vehicle_regis_number)
        vehicle_instance = oilchange_instance.vehicle
        return JsonResponse({
            'status': 'success',
            'oilchangecust': {
                'vehicle_regis_number': vehicle_instance.vehicle_regis_number,
                'current_milleage': vehicle_instance.current_milleage,
                'new_milleage': oilchange_instance.new_milleage
            }
        })
    except oil_change.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Oil change record not found for this vehicle.'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)

        }, status = 500)
    
    return JsonResponse({'status': 'error', 'message': 'Use POST request'}, status=405)


def oil_change_query_page(request):

    context ={}

    if request.method =='POST':
        vehicle_regis_number = request.POST.get('vehicle_regis_number', '').strip()

        if vehicle_regis_number:
            try:
                # Query the vehicle record
                vehicle_instance = vehicle.objects.get(vehicle_regis_number=vehicle_regis_number)
                
                # Get all oil change records for this vehicle, ordered by date
                oilchange_records = oil_change.objects.filter(vehicle=vehicle_instance).order_by('-date_changed')
                
                context['vehicle'] = vehicle_instance
                context['oilchange_records'] = oilchange_records
                
            except vehicle.DoesNotExist:
                context['error'] = f'Vehicle not found: {vehicle_regis_number}'
            except Exception as e:
                context['error'] = f'Error: {str(e)}'
    
    return render(request, 'oil-change.html', context)


def update_vehicle_mileage(request):
    if request.method == 'POST':
        vehicle_regis_number = request.POST.get('vehicle_regis_number', '').strip()
        new_mileage = request.POST.get('new_mileage', '').strip()
        
        if not vehicle_regis_number or not new_mileage:
            context = {'error': 'Please enter both vehicle registration number and new mileage'}
            return render(request, 'oil-change.html', context)

        try:
            vehicle_instance = vehicle.objects.get(vehicle_regis_number=vehicle_regis_number)
            oilchange_records = oil_change.objects.filter(vehicle=vehicle_instance).order_by('-date_changed')
            context = {
                'vehicle': vehicle_instance,
                'oilchange_records': oilchange_records,
            }

            try:
                new_mileage = int(new_mileage)
            except ValueError:
                context['error'] = 'Mileage must be a number'
                return render(request, 'oil-change.html', context)

            if new_mileage < vehicle_instance.current_milleage:
                context['error'] = (
                    'Oil change mileage cannot be less than current mileage '
                    f'({vehicle_instance.current_milleage} km)'
                )
                return render(request, 'oil-change.html', context)

            # Just log the next oil change mileage (don't update vehicle's current mileage)
            oil_change.objects.create(
                vehicle=vehicle_instance,
                new_milleage=new_mileage
            )

            context['oilchange_records'] = oil_change.objects.filter(vehicle=vehicle_instance).order_by('-date_changed')
            context['success'] = 'Oil change scheduled for mileage: ' + str(new_mileage) + ' km'
            return render(request, 'oil-change.html', context)
        except vehicle.DoesNotExist:
            context = {'error': f'Vehicle not found: {vehicle_regis_number}'}
        except Exception as e:
            context = {'error': f'Error: {str(e)}'}

        return render(request, 'oil-change.html', context)
    
    return redirect('vehiclemanagement:oil-change')

def showrepairs(request):
    context = {}

    if request.method == 'POST':
        vehicle_regis_number = request.POST.get('vehicle_regis_number', '').strip()
        description = request.POST.get('description', '').strip()
        costs = request.POST.get('costs', '').strip()

        if vehicle_regis_number:
            try:
                vehicle_instance = vehicle.objects.get(vehicle_regis_number=vehicle_regis_number)

                if description or costs:
                    if not description or not costs:
                        context['error'] = 'Please enter both repair description and cost'
                    else:
                        repairs.objects.create(
                            vehicle=vehicle_instance,
                            description=description,
                            costs=costs
                        )
                        context['success'] = 'Repair record added successfully'

                context['vehicle'] = vehicle_instance
                context['repair_records'] = repairs.objects.filter(
                    vehicle=vehicle_instance
                ).order_by('-date_changed')
            except vehicle.DoesNotExist:
                context['error'] = f'Vehicle not found: {vehicle_regis_number}'
            except Exception as e:
                context['error'] = f'Error: {str(e)}'
        else:
            context['error'] = 'Please enter a vehicle registration number'

    return render(request, 'repairpage.html', context)



#Updated appointment_query view with better context
def appointment_query(request):
    appointments = appointements.objects.select_related('vehicle').all().order_by('date', 'time')
    all_vehicles = vehicle.objects.all()
    
    context = {
        'appointments': appointments,
        'all_vehicles': all_vehicles,
        'db_empty': not appointments.exists(),
        'message': 'No appointments found.' if not appointments else ''
    }
    return render(request, 'appointment.html', context)

# NEW: Create appointment view
def create_appointment(request):
    if request.method == 'POST':
        vehicle_regis_number = request.POST.get('vehicle_regis_number')
        appointment_date = request.POST.get('date')
        appointment_time = request.POST.get('time')
        
        # Validation
        if not all([vehicle_regis_number, appointment_date, appointment_time]):
            messages.error(request, 'Please fill in all fields')
            return redirect('vehiclemanagement:appointment')
        
        try:
            # Check if vehicle exists
            vehicle_instance = vehicle.objects.get(vehicle_regis_number=vehicle_regis_number)
            
            # Check for duplicate appointment
            if appointements.objects.filter(date=appointment_date, time=appointment_time).exists():
                messages.error(request, f'Time slot {appointment_time} on {appointment_date} is already booked. Please choose another time.')
                return redirect('vehiclemanagement:appointment')
            
            # Create appointment
            appointements.objects.create(
                vehicle=vehicle_instance,
                date=appointment_date,
                time=appointment_time
            )
            
            messages.success(request, f'Appointment created successfully for {vehicle_regis_number} on {appointment_date} at {appointment_time}')
            
        except vehicle.DoesNotExist:
            messages.error(request, f'Vehicle with registration number "{vehicle_regis_number}" not found')
        except Exception as e:
            messages.error(request, f'Error creating appointment: {str(e)}')
        
        return redirect('vehiclemanagement:appointment')
    
    return redirect('vehiclemanagement:appointment')

# NEW: Delete appointment view
def delete_appointment(request, appointment_id):
    if request.method == 'POST':
        appointment = get_object_or_404(appointements, id=appointment_id)
        appointment.delete()
        messages.success(request, 'Appointment cancelled successfully')
    return redirect('vehiclemanagement:appointment')


# PDF GENERATION
from django.http import HttpResponse

def generate_invoice(request, vehicle_regis_number):
    vehicle_instance = get_object_or_404(vehicle, vehicle_regis_number=vehicle_regis_number)
    repair_records = repairs.objects.filter(vehicle=vehicle_instance).order_by('-date_changed')[:4]
    next_oil_change = (
        oil_change.objects
        .filter(vehicle=vehicle_instance, new_milleage__gte=vehicle_instance.current_milleage)
        .order_by('new_milleage', '-date_changed')
        .first()
    )
    if next_oil_change is None:
        next_oil_change = (
            oil_change.objects
            .filter(vehicle=vehicle_instance)
            .order_by('-date_changed')
            .first()
        )
    oil_change_remaining = None
    oil_change_overdue_by = None
    if next_oil_change is not None:
        oil_change_remaining = next_oil_change.new_milleage - vehicle_instance.current_milleage
        if oil_change_remaining < 0:
            oil_change_overdue_by = abs(oil_change_remaining)
    
    subtotal = sum((record.costs for record in repair_records), Decimal('0.00'))
    tax_rate = Decimal('15')
    tax_amount = (subtotal * tax_rate / Decimal('100')).quantize(Decimal('0.01'))
    total_amount = (subtotal + tax_amount).quantize(Decimal('0.01'))
    
    context = {
        'vehicle': vehicle_instance,
        'repairs': repair_records,
        'next_oil_change': next_oil_change,
        'oil_change_remaining': oil_change_remaining,
        'oil_change_overdue_by': oil_change_overdue_by,
        'invoice': {
            'subtotal': subtotal,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'payment_terms': 'Due upon receipt',
            'date': timezone.localdate(),
            'number': f'INV-{vehicle_instance.vehicle_regis_number}',
            'repair_count': len(repair_records),
        }
    }
    
    html_string = render_to_string('pdf/invoice.html', context)
    
    # Create a PDF
    html = HTML(string=html_string)
    result = html.write_pdf()
    
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=invoice_{vehicle_regis_number}.pdf'
    
    return response
