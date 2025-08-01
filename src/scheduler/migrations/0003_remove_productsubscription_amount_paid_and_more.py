# Generated by Django 4.2.23 on 2025-08-02 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0002_alter_productsubscription_amount_paid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productsubscription',
            name='amount_paid',
        ),
        migrations.AddField(
            model_name='productsubscription',
            name='eligible_for_delivery',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productsubscription',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productsubscription',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='productsubscription',
            name='remarks',
            field=models.TextField(blank=True, verbose_name='Remarks'),
        ),
    ]
