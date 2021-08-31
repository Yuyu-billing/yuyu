# Generated by Django 3.2.6 on 2021-08-28 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='created_at',
            field=models.DateTimeField(auto_created=True, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='due_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='end_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='tax',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='total',
            field=models.BigIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoiceinstance',
            name='created_at',
            field=models.DateTimeField(auto_created=True, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoiceinstance',
            name='end_date',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='invoiceinstance',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
