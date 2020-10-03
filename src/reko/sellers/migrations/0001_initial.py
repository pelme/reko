# Generated by Django 3.0.8 on 2020-07-31 20:47
from typing import Any, List

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies: List[Any] = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100, verbose_name="namn")),
            ],
        ),
        migrations.CreateModel(
            name="Product",
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
                ("image", models.ImageField(upload_to="")),
                ("description", models.TextField()),
                (
                    "pricing_scheme",
                    models.CharField(
                        choices=[("weight", "Vikt"), ("unit", "Styck")], max_length=100
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductImage",
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
                ("description", models.TextField()),
                ("image", models.ImageField(upload_to="")),
            ],
        ),
        migrations.CreateModel(
            name="Seller",
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
                ("name", models.CharField(max_length=100, verbose_name="namn")),
                ("description", models.TextField(verbose_name="beskrivning")),
                ("image", models.ImageField(upload_to="seller-images")),
                ("categories", models.ManyToManyField(to="sellers.Category")),
            ],
        ),
        migrations.CreateModel(
            name="ProductPriceList",
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
                ("lower", models.DecimalField(decimal_places=2, max_digits=10)),
                ("upper", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "price_per_unit",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sellers.Product",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="product",
            name="seller",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="sellers.Seller"
            ),
        ),
        migrations.CreateModel(
            name="PaymentOption",
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
                (
                    "payment_option",
                    models.CharField(
                        choices=[
                            ("swish", "Swish"),
                            ("card", "Kortbetalning"),
                            ("cash", "Kontant"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "seller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="sellers.Seller"
                    ),
                ),
            ],
        ),
    ]
