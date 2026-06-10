[README.md](https://github.com/user-attachments/files/28788261/README.md)
# Vehicle Management System

A Django-based vehicle service management system for tracking customers, vehicles, repairs, oil-change schedules, appointments, and invoice generation. The project also exposes a Django REST Framework API that can be consumed by a separate Flet desktop/mobile app.

## Project Overview

This system is designed for a vehicle workshop or service center. It helps manage customer vehicle records, log repair work, schedule oil changes, book appointments, and generate PDF invoices for the latest repair history.

The Django web app provides the main browser interface, while the REST API allows external clients such as a Flet app to read and manage the same data.

## Main Features

- Vehicle/customer registration
- Vehicle list page with customer contact and mileage information
- Repair record management
- Oil-change mileage scheduling
- Appointment booking and cancellation
- Duplicate appointment slot validation
- Mileage validation to prevent backward mileage updates
- PDF invoice generation using WeasyPrint
- Invoice includes:
  - Customer details
  - Vehicle details
  - Current mileage
  - Next oil-change information
  - Latest 4 repair records
  - Subtotal, VAT, and total amount in `Rs`
- REST API using Django REST Framework
- Companion Flet app support through API consumption

## Tech Stack

- Python
- Django 6
- Django REST Framework
- SQLite
- WeasyPrint
- HTML/CSS templates
- Flet client app consuming the Django API

## Project Structure

```text
vehicle-management-system/
+--/
|   +-- manage.py
|   +-- db.sqlite3
|   +-- vehiclemanagement/
|   |   +-- models.py
|   |   +-- views.py
|   |   +-- api_views.py
|   |   +-- serializers.py
|   |   +-- urls.py
|   |   +-- tests.py
|   |   +-- forms.py
|   |   +-- templates/
|   |       +-- base.html
|   |       +-- vehicle_management.html
|   |       +-- repairpage.html
|   |       +-- oil-change.html
|   |       +-- appointment.html
|   |       +-- pdf/
|   |           +-- invoice.html
|   +-- vehiclemanagementsystem/
|       +-- settings.py
|       +-- urls.py
|       +-- asgi.py
|       +-- wsgi.py
+-- linkedin/
+-- README.md
```

## Database Models

The project currently includes these main models:

- `vehicle`: stores customer name, phone number, vehicle registration number, and current mileage.
- `repairs`: stores repair descriptions, repair costs, linked vehicle, and repair date.
- `oil_change`: stores scheduled oil-change mileage for a vehicle.
- `appointements`: stores appointment date, time, mechanic name, and appointment status.

## Web Pages

| Page | URL | Purpose |
| --- | --- | --- |
| Vehicle list | `/` | Add and view vehicles |
| Repairs | `/repairpage/` | Search vehicle and add repair records |
| Oil change | `/oil-change/` | Search vehicle and record next oil-change mileage |
| Appointments | `/appointment/` | View and manage appointments |
| Create appointment | `/appointment/create/` | Create a new appointment |
| Delete appointment | `/appointment/delete/<appointment_id>/` | Delete an appointment |
| Invoice PDF | `/invoice/<vehicle_regis_number>/` | Generate PDF invoice for a vehicle |

## API Endpoints

The API is available under:

```text
/api/
```

Main API routes:

| Endpoint | Purpose |
| --- | --- |
| `/api/vehicles/` | List, create, update, and delete vehicles |
| `/api/vehicles/<vehicle_regis_number>/` | Retrieve, update, or delete one vehicle |
| `/api/vehicles/<vehicle_regis_number>/repairs/` | Get repairs for one vehicle |
| `/api/vehicles/<vehicle_regis_number>/oil_changes/` | Get oil-change records for one vehicle |
| `/api/vehicles/<vehicle_regis_number>/appointments/` | Get appointments for one vehicle |
| `/api/repairs/` | List, create, update, and delete repair records |
| `/api/oil-changes/` | List, create, update, and delete oil-change records |
| `/api/appointments/` | List, create, update, and delete appointments |
| `/api/oil-change/<vehicle_regis_number>/` | Return oil-change data for a vehicle as JSON |

## API Example Payloads

Create a vehicle:

```json
{
  "customer_name": "John Doe",
  "customer_phone_number": "123456789",
  "vehicle_regis_number": "2411 NV 27",
  "current_milleage": 52000
}
```

Create a repair:

```json
{
  "description": "Changed brake pads",
  "costs": "2500.00",
  "vehicle": "2411 NV 27"
}
```

Create an oil-change schedule:

```json
{
  "new_milleage": 57000,
  "vehicle": "2411 NV 27"
}
```

Create an appointment:

```json
{
  "vehicle": "2411 NV 27",
  "date": "2026-06-20",
  "time": "09:00:00",
  "mechanic_name": "Technician 1",
  "status": "Pending"
}
```

## Flet App Integration

This project is also designed to work with a Flet app. The Flet app acts as a desktop/mobile client and communicates with the Django backend through the REST API.

Typical flow:

1. Start the Django server.
2. The Flet app sends HTTP requests to the Django API.
3. The API returns vehicle, repair, oil-change, and appointment data as JSON.
4. The Flet app displays and manages that data in its own interface.

Example API base URL for local development:

```text
http://127.0.0.1:8000/api/
```

Example Flet-side request:

```python
import requests

API_BASE_URL = "http://127.0.0.1:8000/api"

response = requests.get(f"{API_BASE_URL}/vehicles/")
vehicles = response.json()
```

If the Flet app runs on another device, replace `127.0.0.1` with the IP address of the computer running the Django server.

## Installation

Clone the project:

```bash
git clone <your-repository-url>
cd vehicle-management-system
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install django djangorestframework weasyprint
```

Apply migrations:

```bash
cd appointments
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

Open the app:

```text
http://127.0.0.1:8000/
```

## Running Tests

From the `appointments` directory:

```bash
python manage.py test
```

The tests cover important business rules such as:

- Oil-change mileage cannot be lower than current mileage.
- Vehicle mileage cannot be updated backwards through the API.
- Repair records can be created.
- Duplicate appointment slots are rejected.

## Invoice Generation

Invoices are generated as PDF files using WeasyPrint.

Invoice URL format:

```text
http://127.0.0.1:8000/invoice/<vehicle_regis_number>/
```

Example:

```text
http://127.0.0.1:8000/invoice/2411%20NV%2027/
```

The invoice includes the latest 4 repair records and uses `Rs` as the currency symbol.

## Notes For Development

- The project currently uses SQLite for local development.
- `DEBUG=True` is enabled in development.
- For production, update `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, database settings, static file handling, and deployment configuration.
- The model name `appointements` and field name `current_milleage` are currently spelled that way in the codebase. Keep those names consistent unless you plan a migration/refactor.

## Future Improvements

- Add authentication and role-based access.
- Add dashboard statistics.
- Add search and filtering for appointments.
- Improve appointment editing.
- Add payment status to invoices.
- Export reports to Excel or PDF.
- Package the Flet app for desktop/mobile distribution.
- Deploy the Django API online so the Flet app can connect remotely.


