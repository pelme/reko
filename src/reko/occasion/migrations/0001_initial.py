# Generated by Django 3.2.6 on 2021-08-22 18:18

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("producer", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=10)),
                ("time_start", models.TimeField()),
                ("time_end", models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name="Occasion",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("is_published", models.BooleanField()),
                ("locations", models.ManyToManyField(to="occasion.Location")),
                ("producers", models.ManyToManyField(to="producer.Producer")),
            ],
        ),
    ]
