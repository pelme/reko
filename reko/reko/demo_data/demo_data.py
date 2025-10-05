from __future__ import annotations

import datetime
import importlib.resources
import typing as t
from decimal import Decimal

from django.core.files import File

from reko.reko.models import Pickup, Producer, Product, Ring, User


def image(image_name: str) -> tuple[str, File[bytes]]:
    return (image_name, File(importlib.resources.files(__package__).joinpath("images", image_name).open("rb")))


def _save_product_with_image(product: Product, image_name: str) -> None:
    product.image.save(*image(image_name))
    product.save()


def create_user(*, email: str, **kwargs: t.Any) -> User:
    user = User(
        email=email,
        is_active=True,
        **kwargs,
    )
    user.set_password("password")
    user.save()
    return user


def generate_demo_data() -> None:
    ring = Ring.objects.create(
        name="Reko Linköping",
    )

    pickup_bogestad = Pickup.objects.create(
        ring=ring,
        place="Bogestadskolan (Hembygdsvägen)",
        date=datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=14),
        start_time=datetime.time(17, 30),
        end_time=datetime.time(18),
        is_published=True,
    )
    pickup_cleantech = Pickup.objects.create(
        ring=ring,
        place="Cleantechpark Gjuterigatan (rakt bakom tågstationen)",
        date=datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=14),
        start_time=datetime.time(17, 45),
        end_time=datetime.time(18, 0, 5),
        is_published=True,
    )

    Producer.objects.filter(slug="demo").delete()

    producer = Producer(
        display_name="Östergården",
        company_name="Östergårdens Jordbruk AB",
        email="ostergarden@example.com",
        slug="demo",
        phone="013-37 37 37",
        swish_number="123 456 78 90",
        address="Östergården 1, 596 12 Skänninge",
        color_palette="green",
        description=(
            "Beläget i hjärtat av Östergötlands frodiga landskap, är Östergården en "
            "familjeägd gård som specialiserar sig på att odla högkvalitativ kål, potatis och "
            "majs. Med en stark förankring i traditionellt jordbruk och hållbara metoder, "
            "strävar vi efter att leverera färska, näringsrika grönsaker direkt från våra "
            "fält till ditt bord."
        ),
    )
    producer.image.save(*image("ostergarden.webp"))
    producer.save()

    _save_product_with_image(
        Product(
            producer=producer,
            name="Grönsakskasse",
            description="Blandade grönsaker i säsong",
            price_with_vat=130,
            vat_factor=Decimal("0.06"),
        ),
        # "Organic Vegetable Boxes" by AndyRobertsPhotos is licensed under CC BY
        # 2.0. To view a copy of this license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image_name="gronsakskasse.webp",
    )

    _save_product_with_image(
        Product(
            producer=producer,
            name="Rödbetor",
            description="Rödbetor i knippe. Storleken varierar.",
            price_with_vat=25,
            vat_factor=Decimal("0.06"),
        ),
        # "Beetroot - Kew Horticultural Society Summer Show" by Annie Mole is
        # licensed under CC BY 2.0. To view a copy of this license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image_name="rodbetor.jpg",
    )

    _save_product_with_image(
        Product(
            producer=producer,
            name="Grönkål",
            description="Grönkål i knippe. God till sallad eller smoothie.",
            price_with_vat=30,
            vat_factor=Decimal("0.06"),
        ),
        # "Kale and banana smoothie" by Mervi Emilia is licensed under CC BY
        # 2.0. To view a copy of this license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image_name="gronkal.jpg",
    )

    _save_product_with_image(
        Product(
            producer=producer,
            name="Knippe Gullök",
            description="Gullök i knippe. Passar utmärkt i matlagning.",
            price_with_vat=35,
            vat_factor=Decimal("0.06"),
        ),
        # "Onions" by srqpix is licensed under CC BY 2.0. To view a copy of this
        # license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image_name="lok.jpg",
    )

    _save_product_with_image(
        Product(
            producer=producer,
            name="Jordgubbar, 1 liter",
            description="Färska jordgubbar av sorten Sweet Delight. Små, söta och saftiga.",
            price_with_vat=75,
            vat_factor=Decimal("0.12"),
        ),
        image_name="jordgubbar.jpg",
    )

    ring.producers.add(producer)
    producer.pickups.add(pickup_bogestad)
    producer.pickups.add(pickup_cleantech)
