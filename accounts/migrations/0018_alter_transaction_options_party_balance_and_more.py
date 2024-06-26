# Generated by Django 5.0.2 on 2024-06-08 09:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_alter_transaction_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'permissions': (('can_manage_transactions', 'Can Manage Transactions'), ('can_manage_sales', 'Can Manage Sales'), ('can_manage_purchase', 'Can Manage Purchase'), ('can_manage_s_p', 'Can Manage Sale/Purchase'))},
        ),
        migrations.AddField(
            model_name='party',
            name='balance',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='bill_number',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='charges',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='discount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_sales',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('quantity', models.PositiveIntegerField()),
                ('delete_flag', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'name')},
            },
        ),
        migrations.CreateModel(
            name='TradeItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.PositiveIntegerField()),
                ('delete_flag', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.product')),
                ('trade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trade_items', to='accounts.transaction')),
            ],
        ),
    ]
