# Generated migration for adding date_changed field to oil_change model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vehiclemanagement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='oil_change',
            name='date_changed',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
