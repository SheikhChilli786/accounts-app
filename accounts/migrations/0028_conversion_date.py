# Generated by Django 5.0.2 on 2024-08-26 04:52

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_conversion_user_alter_conversion_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversion',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
