# Generated by Django 5.0.10 on 2025-01-18 15:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reko", "0004_alter_orderproduct_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="place",
            field=models.CharField(max_length=100, verbose_name="plats"),
        ),
    ]
