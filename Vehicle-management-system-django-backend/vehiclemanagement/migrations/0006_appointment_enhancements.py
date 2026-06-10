
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('vehiclemanagement', '0005_rename_time_slot_appointements_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointements',
            name='mechanic_name',
            field=models.CharField(max_length=100, default='Unassigned'),
        ),
        migrations.AddField(
            model_name='appointements',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('Pending', 'Pending'),
                    ('Confirmed', 'Confirmed'),
                    ('Completed', 'Completed'),
                ],
                default='Pending'
            ),
        ),
    ]
