# Generated by Django 5.0.2 on 2024-04-07 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_alter_party_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'permissions': (('can_manage_transactions', 'Can Manage Transactions'),)},
        ),
    ]