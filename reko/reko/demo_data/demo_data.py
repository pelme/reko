from __future__ import annotations

import datetime
import importlib.resources
import typing as t
from dataclasses import dataclass

from django.core.files import File
from django.utils import timezone
from django.utils.text import slugify

from reko.reko.models import Location, Pickup, PickupLocation, Producer, Product, Ring, User

if t.TYPE_CHECKING:
    from collections.abc import Iterable


def image(image_name: str) -> tuple[str, File[bytes]]:
    return (image_name, File(importlib.resources.files(__package__).joinpath("images", image_name).open("rb")))


def _save_product_with_image(product: Product, image_name: str) -> None:
    product.image.save(*image(image_name))
    product.save()


def _get_unsaved_user(email: str, **kwargs: t.Any) -> User:
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return User(
            email=email,
            is_active=True,
            **kwargs,
        )


def create_user(*, email: str, password: str, **kwargs: t.Any) -> User:
    user = _get_unsaved_user(email, **kwargs)
    user.set_password(password)
    user.save()
    return user


def generate_ring() -> Ring:
    return Ring.objects.get_or_create(
        name="Reko Linköping",
    )[0]


def generate_pickup_locations(ring: Ring) -> list[PickupLocation]:
    pickup = Pickup.objects.create(
        ring=ring,
        date=timezone.localdate() + datetime.timedelta(days=14),
        is_published=True,
    )
    return [
        PickupLocation.objects.get_or_create(
            pickup=pickup,
            defaults={
                "location": Location.objects.get_or_create(
                    name="Bogestadskolan",
                    defaults={
                        "ring": ring,
                        "address": "Hembygdsvägen",
                    },
                )[0],
                "start_time": datetime.time(17, 30),
                "end_time": datetime.time(17, 45),
            },
        )[0],
        PickupLocation.objects.get_or_create(
            pickup=pickup,
            defaults={
                "location": Location.objects.get_or_create(
                    name="Cleantechpark",
                    defaults={
                        "ring": ring,
                        "address": "Gjuterigatan",
                        "description": "Rakt bakom tågstationen.",
                        "link": "https://maps.app.goo.gl/joRn5wrnorpvnBu28",
                    },
                )[0],
                "start_time": datetime.time(17, 45),
                "end_time": datetime.time(18),
            },
        )[0],
    ]


def generate_producer(demo: DemoProducer) -> Producer:
    producer = Producer(
        display_name=demo.name,
        company_name=f"{demo.name}s Jordbruk AB",
        email=demo.email,
        slug=f"demo-{demo.slug}",
        phone="013-37 37 37",
        swish_number="1234567890",
        address=f"{demo.name} 1, 596 12 Skänninge",
        color_palette=demo.color,
        description=demo.description,
    )
    producer.image.save(*image(f"{demo.slug}.webp"))
    producer.save()

    _save_product_with_image(
        Product(
            producer=producer,
            name="Grönsakskasse",
            description="Blandade grönsaker i säsong",
            price_with_vat=130,
            vat_factor=Product.VATPercentage.six,
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
            vat_factor=Product.VATPercentage.six,
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
            vat_factor=Product.VATPercentage.six,
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
            vat_factor=Product.VATPercentage.six,
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
            vat_factor=Product.VATPercentage.twelve,
        ),
        image_name="jordgubbar.jpg",
    )

    return producer


@dataclass
class DemoProducer:
    name: str
    color: str
    description: str

    @property
    def email(self) -> str:
        return f"{self.slug}@example.com"

    @property
    def slug(self) -> str:
        return slugify(self.name)


östergården = DemoProducer(
    name="Östergården",
    color="green",
    description=(
        "Beläget i hjärtat av Östergötlands frodiga landskap, är Östergården en "
        "familjeägd gård som specialiserar sig på att odla högkvalitativ kål, potatis och "
        "majs. Med en stark förankring i traditionellt jordbruk och hållbara metoder, "
        "strävar vi efter att leverera färska, näringsrika grönsaker direkt från våra "
        "fält till ditt bord."
    ),
)
västergården = DemoProducer(
    name="Västergården",
    color="orange",
    description=(
        "På Västergården låter vi våra grödor mogna i den varma kvällssolen, "
        "vilket ger en sötma och krispighet som morgonljuset i öst sällan når. "
        "Vi nöjer oss inte med det ordinära; i våra fält samsas matiga grönsaker "
        "med solmogna bär – en mångfald som gör skillnad på tallriken. "
    ),
)


def generate_producers(ring: Ring, pickup_locations: Iterable[PickupLocation]) -> Iterable[Producer]:
    for demo in [västergården, östergården]:
        Producer.objects.filter(slug=f"demo-{demo.slug}").delete()
        producer = generate_producer(demo)
        ring.producers.add(producer)
        producer.pickup_locations.set(pickup_locations)
        yield producer


def generate_demo_data() -> Iterable[Producer]:
    ring = generate_ring()
    pickup_locations = generate_pickup_locations(ring)
    return list(generate_producers(ring, pickup_locations))
