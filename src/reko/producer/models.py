from django.db import models

from .constants import PAYMENT_OPTIONS


class Category(models.Model):
    name = models.CharField("namn", max_length=100)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.name


class Producer(models.Model):
    name = models.CharField("namn", max_length=100)
    company_name = models.CharField("företagsnamn", max_length=100)
    organisation_number = models.CharField("organisationsnummer", max_length=100)

    slug = models.SlugField(unique=True)
    product_description = models.CharField("kort produktbeskrivning", max_length=100)
    description = models.TextField("beskrivning")

    image = models.ImageField(upload_to="producer-images")

    categories = models.ManyToManyField(Category)

    def __str__(self) -> str:
        return self.name


class PaymentOption(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    payment_option = models.CharField(max_length=100, choices=PAYMENT_OPTIONS)


class Product(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    image = models.ImageField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name
