# Generated by Django 4.2.23 on 2025-08-02 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productsubscription',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
