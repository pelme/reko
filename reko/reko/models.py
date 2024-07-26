from decimal import Decimal

from django.core import signing
from django.db import models
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.timezone import localdate
from imagekit.models import ImageSpecField  # type: ignore[import-untyped]
from imagekit.processors import ResizeToFill  # type: ignore[import-untyped]


class Producer(models.Model):
    name = models.CharField("namn", max_length=100)
    slug = models.SlugField(unique=True, help_text="Används för att generera din unika länk.")

    phone = models.CharField("telefonnummer", max_length=50)
    email = models.EmailField("e-postadress")
    swish_number = models.CharField("swishnummer", max_length=50)
    address = models.CharField("adress", max_length=100)

    description = models.TextField("beskrivning")
    image = models.ImageField("bild", upload_to="producer-images")

    class Meta:
        verbose_name = "producent"
        verbose_name_plural = "producenter"

    def __str__(self) -> str:
        return self.name

    def get_shop_url(self, request: HttpRequest) -> str:
        return request.build_absolute_uri(reverse("producer-index", args=[self.slug]))

    def generate_order_number(self) -> int:
        # Take an exclusive lock on this producer to avoid duplicated numbers
        Producer.objects.filter(pk=self.pk).select_for_update()

        return 1 + (self.order_set.order_by("-order_number").values_list("order_number", flat=True)[:1].first() or 0)

    def get_upcoming_locations(self) -> models.QuerySet["Location"]:
        return self.location_set.filter(is_published=True, date__gte=localdate()).order_by("date")


class Product(models.Model):
    producer = models.ForeignKey("Producer", on_delete=models.CASCADE)

    name = models.CharField("namn", max_length=100)
    image = models.ImageField("bild")

    price = models.DecimalField("pris", max_digits=10, decimal_places=2)
    items_in_stock = models.PositiveIntegerField("antal i lager")

    is_published = models.BooleanField("är publicerad", default=True)

    description = models.TextField("beskrivning")

    card_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(600, 400)],
        format="webp",
        options={"quality": 75},
    )

    class Meta:
        verbose_name = "produkt"
        verbose_name_plural = "produkter"

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    producer = models.ForeignKey("Producer", verbose_name="producent", on_delete=models.CASCADE)

    place_and_time = models.CharField("plats och tid", max_length=100)
    date = models.DateField("datum")
    link = models.URLField("länk till utlämningsplats", blank=True)

    is_published = models.BooleanField()

    class Meta:
        verbose_name = "utlämningsplats"
        verbose_name_plural = "utlämningsplatser"

    def __str__(self) -> str:
        return self.place_and_time


class OrderManager(models.Manager["Order"]):
    def filter_order_secret(self, producer: Producer, order_secret: str) -> QuerySet["Order"]:
        try:
            order_number = signer.unsign(order_secret)
        except signing.BadSignature:
            return self.none()

        return self.filter(producer=producer, order_number=order_number)


signer = signing.Signer()


class Order(models.Model):
    producer = models.ForeignKey("Producer", on_delete=models.CASCADE, verbose_name="producent")
    location = models.ForeignKey("Location", on_delete=models.CASCADE, verbose_name="utlämningsplats")

    order_number = models.PositiveIntegerField()

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    note = models.TextField(blank=True)

    objects = OrderManager()

    class Meta:
        verbose_name = "beställning"
        verbose_name_plural = "beställningar"
        unique_together = ["producer", "order_number"]

    def __str__(self) -> str:
        return f"Order #{self.order_number}"

    def total_price(self) -> Decimal:
        return sum(
            (order_product.amount * order_product.price for order_product in self.orderproduct_set.all()),
            Decimal(),
        )

    def order_secret(self) -> str:
        return signer.sign(str(self.order_number))


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey("Product", on_delete=models.PROTECT)

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self) -> Decimal:
        return self.amount * self.price
