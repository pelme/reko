# Generated by Django 5.0.10 on 2025-01-18 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reko', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='items_in_stock',
        ),
    ]
