# Generated by Django 5.0.10 on 2025-01-18 15:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reko", "0003_alter_order_email_alter_order_name_alter_order_note_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orderproduct",
            options={"verbose_name": "produkt", "verbose_name_plural": "produkter"},
        ),
        migrations.RenameField(
            model_name="location",
            old_name="place_and_time",
            new_name="place",
        ),
    ]
