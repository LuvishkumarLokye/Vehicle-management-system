import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiclemanagement', '0002_oil_change_date_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='repairs',
            name='date_repaired',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
