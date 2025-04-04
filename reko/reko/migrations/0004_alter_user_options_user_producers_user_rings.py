# Generated by Django 5.0.10 on 2025-01-25 15:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reko", "0003_ring"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name": "användare", "verbose_name_plural": "användare"},
        ),
        migrations.AddField(
            model_name="user",
            name="producers",
            field=models.ManyToManyField(blank=True, to="reko.producer", verbose_name="producenter"),
        ),
        migrations.AddField(
            model_name="user",
            name="rings",
            field=models.ManyToManyField(blank=True, to="reko.ring", verbose_name="ringar"),
        ),
    ]
