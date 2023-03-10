# Generated by Django 3.2.6 on 2022-11-29 15:43

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20221121_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount_currency', djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3)),
                ('amount', djmoney.models.fields.MoneyField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.billingproject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BalanceTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount_currency', djmoney.models.fields.CurrencyField(choices=[('IDR', 'Indonesian Rupiah')], default='IDR', editable=False, max_length=3)),
                ('amount', djmoney.models.fields.MoneyField(decimal_places=2, max_digits=10)),
                ('action', models.CharField(choices=[('top_up', 'Top Up'), ('top_down', 'Top Down')], max_length=256)),
                ('description', models.CharField(max_length=256)),
                ('balance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.balance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
