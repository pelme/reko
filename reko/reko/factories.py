from __future__ import annotations

import datetime
from decimal import Decimal

import factory
from factory.django import DjangoModelFactory as ModelFactory

from .models import Location, Order, OrderProduct, Pickup, Producer, Product, Ring


class RingFactory(ModelFactory[Ring]):
    class Meta:
        model = Ring

    name = "One Ring To Rule Them All"


class ProducerFactory(ModelFactory[Producer]):
    class Meta:
        model = Producer

    display_name = "Farmer Maggot"
    company_name = "Bamfurlong"
    slug = factory.Sequence(lambda n: f"farmer-maggot-{n}")

    phone = "013129991"
    email = "maggot@bamfurlong.me"
    swish_number = "1234567890"
    address = "Bamfurlong, the Marish"

    description = "Farmer Maggot's farm is well-known in the area for his mushrooms."
    image = "https://tolkiengateway.net/w/images/c/c1/NOLANOS_-_La_Familia_del_Viejo_Maggot.jpg"

    color_palette = "orange"


class ProductFactory(ModelFactory[Product]):
    class Meta:
        model = Product

    producer = factory.SubFactory(ProducerFactory)  # type: ignore[var-annotated]

    name = "Mushroom"
    image = "https://tolkiengateway.net/w/images/8/84/Henning_Janssen_-_Harvesting_Maggots.jpg"

    price_with_vat = Decimal("12.34")
    vat_factor = Decimal("0.6")

    is_published = True

    description = "Delicious mushroom that goes well with any bean."


class LocationFactory(ModelFactory[Location]):
    class Meta:
        model = Location

    ring = factory.SubFactory(RingFactory)  # type: ignore[var-annotated]

    name = "Bucklebury Ferry"
    link = "https://tolkiengateway.net/wiki/Bucklebury_Ferry"


class PickupFactory(ModelFactory[Pickup]):
    class Meta:
        model = Pickup

    ring = factory.SubFactory(RingFactory)  # type: ignore[var-annotated]
    location = factory.SubFactory(LocationFactory)  # type: ignore[var-annotated]
    date = datetime.date(3018, 9, 25)
    start_time = datetime.time(9, 30)
    end_time = datetime.time(14)

    is_published = True


class OrderFactory(ModelFactory[Order]):
    class Meta:
        model = Order

    producer = factory.SubFactory(ProducerFactory)  # type: ignore[var-annotated]
    pickup = factory.SubFactory(PickupFactory)  # type: ignore[var-annotated]

    order_number = factory.Sequence(lambda n: n)

    name = "Mirabella Took"
    email = "mirabella@took.me"
    phone = "013129991"
    note = "No dirty mushrooms please!"


class OrderProductFactory(ModelFactory[OrderProduct]):
    class Meta:
        model = OrderProduct

    order = factory.SubFactory(OrderFactory)  # type: ignore[var-annotated]

    product = factory.SubFactory(ProductFactory)  # type: ignore[var-annotated]

    name = "Mushroom"
    amount = 14
    price_with_vat = Decimal("12.34")
    vat_factor = Decimal("0.6")
