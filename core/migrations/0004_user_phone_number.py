# Generated by Django 5.0.1 on 2024-02-04 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default=0, max_length=13, unique=True),
            preserve_default=False,
        ),
    ]
