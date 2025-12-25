from __future__ import annotations

import secrets
import string
import typing as t
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core import signing
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.timezone import localdate
from imagekit.models import ImageSpecField  # type: ignore[import-untyped]
from imagekit.processors import ResizeToFill  # type: ignore[import-untyped]

from reko.reko.formatters import format_date, format_percentage, format_time_range, quantize_decimal

from .validators import SwishNumberValidator

if t.TYPE_CHECKING:
    from django.http import HttpRequest


class UserManager(BaseUserManager["User"]):
    def create_superuser(self, *, email: str, password: str, **extra_fields: t.Any) -> User:
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create(
            email=email,
            password=make_password(password),
            is_superuser=True,
            is_active=True,
        )


class User(AbstractBaseUser):
    email = models.EmailField("mejladress", unique=True)
    is_active = models.BooleanField("är aktiv")
    is_superuser = models.BooleanField("är superadmin")
    producers = models.ManyToManyField(
        "reko.Producer",
        blank=True,
        verbose_name="producenter",
    )
    rings = models.ManyToManyField(
        "reko.Ring",
        blank=True,
        verbose_name="ringar",
    )

    class Meta:
        verbose_name = "användare"
        verbose_name_plural = "användare"

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: t.ClassVar[list[str]] = []

    is_staff = True  # Allow access to admin

    def set_random_password(self) -> str:
        password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        self.set_password(password)
        return password

    def has_perm(self, perm: str, obj: models.Model | None = None) -> bool:
        assert self.is_active

        if self.is_superuser:
            return True

        valid_perms = (
            "reko.change_producer",
            "reko.view_producer",
            "reko.add_product",
            "reko.change_product",
            "reko.delete_product",
            "reko.view_product",
            "reko.add_order",
            "reko.change_order",
            "reko.delete_order",
            "reko.view_order",
            "reko.add_orderproduct",
            "reko.change_orderproduct",
            "reko.delete_orderproduct",
        )
        if perm not in valid_perms:
            return False

        return True

    def has_module_perms(self, app_label: str) -> bool:
        assert self.is_active

        if self.is_superuser:
            return True

        return app_label in ("reko",)

    objects = UserManager()

    def __str__(self) -> str:
        return self.email


class Ring(models.Model):
    name = models.CharField("namn")
    producers = models.ManyToManyField(
        "reko.Producer",
        verbose_name="producenter",
    )

    class Meta:
        verbose_name = "ring"
        verbose_name_plural = "ringar"

    def __str__(self) -> str:
        return self.name


class ProducerQuerySet(QuerySet["Producer"]):
    def filter_by_admin(self, user: User) -> t.Self:
        if user.is_superuser:
            return self.all()

        return self.filter(id__in=user.producers.all())


class Producer(models.Model):
    display_name = models.CharField("visningsnamn", max_length=100)
    company_name = models.CharField("företagsnamn", max_length=100)
    slug = models.SlugField(unique=True, help_text="Används för att generera din unika länk.")

    phone = models.CharField("telefonnummer", max_length=50)
    email = models.EmailField("mejladress")
    swish_number = models.CharField(
        "swishnummer",
        max_length=50,
        validators=[SwishNumberValidator(message="Ange ett giltigt Swishnummer.")],
    )
    address = models.CharField("adress", max_length=100)

    description = models.TextField("beskrivning")
    image = models.ImageField("bild", upload_to="producer-images")
    pickup_locations = models.ManyToManyField("reko.PickupLocation", verbose_name="utlämningsplatser", blank=True)

    color_palette = models.CharField(
        "färgpalett",
        choices=[
            ("red", "Röd"),
            ("orange", "Orange"),
            ("yellow", "Gul"),
            ("green", "Grön"),
            ("cyan", "Cyan"),
            ("blue", "Blå"),
            ("indigo", "Indigo"),
            ("purple", "Lila"),
            ("pink", "Rosa"),
            ("gray", "Grå"),
        ],
    )

    objects = ProducerQuerySet.as_manager()

    class Meta:
        verbose_name = "producent"
        verbose_name_plural = "producenter"

    def __str__(self) -> str:
        return self.display_name

    def get_shop_url(self, request: HttpRequest) -> str:
        return request.build_absolute_uri(reverse("producer-index", args=[self.slug]))

    def generate_order_number(self) -> int:
        # Take an exclusive lock on this producer to avoid duplicated numbers
        Producer.objects.filter(pk=self.pk).select_for_update()

        return 1 + (self.order_set.order_by("-order_number").values_list("order_number", flat=True)[:1].first() or 0)

    def get_upcoming_pickup_locations(self) -> models.QuerySet[PickupLocation]:
        return self.pickup_locations.filter(pickup__is_published=True, pickup__date__gte=localdate()).order_by(
            "pickup__date", "start_time"
        )


class ProductQuerySet(QuerySet["Product"]):
    def filter_by_admin(self, user: User) -> t.Self:
        if user.is_superuser:
            return self.all()

        return self.filter(producer__in=user.producers.all())


class Product(models.Model):
    class VATPercentage(Decimal, models.Choices):
        zero = "0.0000", f"{format_percentage(Decimal(0))} (momsfri)"
        six = "0.0600", format_percentage(Decimal("0.06"))
        twelve = "0.1200", format_percentage(Decimal("0.12"))
        twentyfive = "0.2500", format_percentage(Decimal("0.25"))

    producer = models.ForeignKey("Producer", on_delete=models.CASCADE, verbose_name="producent")

    name = models.CharField("namn", max_length=100)
    image = models.ImageField("bild")

    price_with_vat = models.DecimalField(
        "pris",
        max_digits=10,
        decimal_places=2,
        help_text="Ange priset inklusive moms.",
        validators=[MinValueValidator(0)],
    )
    vat_factor = models.DecimalField("momssats", max_digits=5, decimal_places=4, choices=VATPercentage.choices)

    is_published = models.BooleanField("är publicerad", default=True)

    description = models.TextField("beskrivning")

    card_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(600, 400)],
        format="webp",
        options={"quality": 75},
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = "produkt"
        verbose_name_plural = "produkter"

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    ring = models.ForeignKey("reko.Ring", on_delete=models.PROTECT)

    name = models.CharField("namn", max_length=50)
    address = models.CharField("adress", max_length=100, blank=True)

    description = models.TextField("beskrivning", blank=True)
    link = models.URLField("länk till plats", blank=True)

    class Meta:
        verbose_name = "plats"
        verbose_name_plural = "platser"

    def __str__(self) -> str:
        return self.name


class Pickup(models.Model):
    ring = models.ForeignKey("reko.Ring", on_delete=models.PROTECT)

    date = models.DateField("datum")
    is_published = models.BooleanField("är publicerad")

    class Meta:
        verbose_name = "utlämning"
        verbose_name_plural = "utlämningar"

    def __str__(self) -> str:
        return " ".join([self.ring.name, format_date(self.date)])


class PickupLocation(models.Model):
    pickup = models.ForeignKey(Pickup, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, verbose_name="plats", on_delete=models.CASCADE)

    start_time = models.TimeField("starttid")
    end_time = models.TimeField("sluttid")

    class Meta:
        verbose_name = "utlämningsplats"
        verbose_name_plural = "utlämningsplatser"

    def __str__(self) -> str:
        return " ".join([self.location.name, format_time_range(self.start_time, self.end_time)])


class OrderQuerySet(models.QuerySet["Order"]):
    def filter_order_secret(self, producer: Producer, order_secret: str) -> t.Self:
        try:
            order_number = signer.unsign(order_secret)
        except signing.BadSignature:
            return self.none()

        return self.filter(producer=producer, order_number=order_number)

    def filter_by_admin(self, user: User) -> t.Self:
        if user.is_superuser:
            return self.all()

        return self.filter(producer__in=user.producers.all())


signer = signing.Signer()


class Order(models.Model):
    producer = models.ForeignKey("Producer", on_delete=models.CASCADE, verbose_name="producent")
    pickup_location = models.ForeignKey("PickupLocation", on_delete=models.CASCADE, verbose_name="utlämning")

    order_number = models.PositiveIntegerField("#")

    name = models.CharField("namn", max_length=100)
    email = models.EmailField("mejladress")
    phone = models.CharField("telefonnummer", max_length=50)
    note = models.TextField("anteckning", blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = "beställning"
        verbose_name_plural = "beställningar"
        unique_together = ["producer", "order_number"]

    def __str__(self) -> str:
        return f"Beställning {self.order_number}"

    def total_price_with_vat(self) -> Decimal:
        return quantize_decimal(
            sum(
                (order_product.total_price_with_vat() for order_product in self.orderproduct_set.all()),
                Decimal(),
            )
        )

    def order_secret(self) -> str:
        return signer.sign(str(self.order_number))

    def confirmation_email(self, request: HttpRequest) -> EmailMessage:
        from . import components

        assert self.email
        html = str(
            components.order_confirmation_email(
                request=request,
                order=self,
            )
        )

        email = EmailMessage(
            subject="Orderbekräftelse",
            body=html,
            from_email=f"{self.producer.display_name} (via handlareko.se) <noreply@handlareko.se>",
            reply_to=[f"{self.producer.display_name} <{self.producer.email}>"],
            to=[self.email],
        )
        email.content_subtype = "html"

        return email

    def order_summary_url(self, request: HttpRequest) -> str:
        return request.build_absolute_uri(
            reverse(
                "order-summary",
                kwargs={
                    "producer_slug": self.producer.slug,
                    "order_secret": self.order_secret(),
                },
            )
        )


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    product = models.ForeignKey("Product", on_delete=models.PROTECT, verbose_name="produkt")

    name = models.CharField("namn", max_length=100)
    amount = models.DecimalField("antal", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    price_with_vat = models.DecimalField("pris", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    vat_factor = models.DecimalField("momssats", max_digits=5, decimal_places=4)

    class Meta:
        verbose_name = "produkt"
        verbose_name_plural = "produkter"

    def __str__(self) -> str:
        # Ugly but easy way to hide the default implementation in admin inlines.
        return ""

    def total_price_with_vat(self) -> Decimal:
        return self.amount * self.price_with_vat
