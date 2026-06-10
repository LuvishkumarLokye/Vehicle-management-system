import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiclemanagement', '0003_repairs_date_repaired'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointements',
            name='time_slot',
            field=models.TimeField(default=datetime.time(9, 0)),
            preserve_default=False,
        ),
    ]
