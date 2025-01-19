from __future__ import annotations

import datetime
import importlib.resources

from django.core.files import File

from reko.reko.models import Location, Producer, Product


def image(image_name: str) -> tuple[str, File[bytes]]:
    return (image_name, File(importlib.resources.files(__package__).joinpath("images", image_name).open("rb")))


def _save_product_with_image(product: Product, image_name: str) -> None:
    product.image.save(*image(image_name))
    product.save()


def generate_demo_data() -> None:
    Producer.objects.filter(slug="demo").delete()

    producer = Producer(
        display_name="Östergården",
        company_name="Östergårdens Jordbruk AB",
        email="ostergarden@example.com",
        slug="demo",
        phone="013-37 37 37",
        swish_number="123 456 78 90",
        address="Östergården 1, 596 12 Skänninge",
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
            price=130,
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
            price=25,
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
            price=30,
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
            price=35,
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
            price=75,
        ),
        image_name="jordgubbar.jpg",
    )

    Location.objects.create(
        producer=producer,
        place="Bogestadskolan (Hembygdsvägen)",
        date=datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=14),
        start_time=datetime.time(17, 30),
        end_time=datetime.time(18),
        is_published=True,
    )
    Location.objects.create(
        producer=producer,
        place="Cleantechpark Gjuterigatan (rakt bakom tågstationen)",
        date=datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=14),
        start_time=datetime.time(17, 45),
        end_time=datetime.time(18, 0, 5),
        is_published=True,
    )
