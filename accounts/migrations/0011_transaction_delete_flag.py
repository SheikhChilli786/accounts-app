# Generated by Django 5.0.1 on 2024-02-10 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_party_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='delete_flag',
            field=models.IntegerField(default=0),
        ),
    ]
