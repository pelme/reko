from django.db import models

from .constants import PAYMENT_OPTIONS, PRICING_SCHEMES


class Category(models.Model):
    name = models.CharField("namn", max_length=100)

    def __str__(self) -> str:
        return self.name


class Seller(models.Model):
    name = models.CharField("namn", max_length=100)
    description = models.TextField("beskrivning")

    categories = models.ManyToManyField(Category)

    def __str__(self) -> str:
        return self.name


class PaymentOption(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    payment_option = models.CharField(max_length=100, choices=PAYMENT_OPTIONS)


class SellerImage(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="seller-images")
    caption = models.TextField()


class Product(models.Model):
    name = models.CharField(max_length=100)
    pricing_scheme = models.CharField(max_length=100, choices=PRICING_SCHEMES)


class ProductImage(models.Model):
    description = models.TextField()
    image = models.ImageField()


class ProductPriceList(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    lower = models.DecimalField(max_digits=10, decimal_places=2)
    upper = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
