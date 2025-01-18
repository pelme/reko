# ruff: noqa: E402
import datetime
import os
import shutil

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reko.settings.dev")
django.setup()

from django.conf import settings
from django.contrib.auth.models import User

from reko.reko.models import Location, Producer, Product


def main() -> None:
    User.objects.create_superuser(username="admin", password="admin")

    producer = Producer.objects.create(
        name="Östergården",
        slug="ostergarden",
        phone="013-37 37 37",
        swish_number="123 456 78 90",
        address="Östergården 1, 596 12 Skänninge",
        image="producer-images/ostergarden.webp",
        description=(
            "Beläget i hjärtat av Östergötlands frodiga landskap, är Östergården en "
            "familjeägd gård som specialiserar sig på att odla högkvalitativ kål, potatis och "
            "majs. Med en stark förankring i traditionellt jordbruk och hållbara metoder, "
            "strävar vi efter att leverera färska, näringsrika grönsaker direkt från våra "
            "fält till ditt bord."
        ),
    )

    Product.objects.create(
        producer=producer,
        # "Organic Vegetable Boxes" by AndyRobertsPhotos is licensed under CC BY
        # 2.0. To view a copy of this license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image="producer-images/gronsakskasse.webp",
        name="Grönsakskasse",
        description="Blandade grönsaker i säsong",
        price=130,
    )

    Product.objects.create(
        producer=producer,
        # "Beetroot - Kew Horticultural Society Summer Show" by Annie Mole is
        # licensed under CC BY 2.0. To view a copy of this license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image="producer-images/rodbetor.jpg",
        name="Rödbetor",
        description="Rödbetor i knippe. Storleken varierar.",
        price=25,
    )
    Product.objects.create(
        producer=producer,
        # "Kale and banana smoothie" by Mervi Emilia is licensed under CC BY
        # 2.0. To view a copy of this license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image="producer-images/gronkal.jpg",
        name="Grönkål",
        description="Grönkål i knippe. God till sallad eller smoothie.",
        price=30,
    )

    Product.objects.create(
        producer=producer,
        # "Onions" by srqpix is licensed under CC BY 2.0. To view a copy of this
        # license, visit
        # https://creativecommons.org/licenses/by/2.0/?ref=openverse.
        image="producer-images/lok.jpg",
        name="Knippe Gullök",
        description="Gullök i knippe. Passar utmärkt i matlagning.",
        price=35,
    )
    Product.objects.create(
        producer=producer,
        image="producer-images/jordgubbar.jpg",
        name="Jordgubbar, 1 liter",
        description=("Färska jordgubbar av sorten Sweet Delight. Små, söta och saftiga."),
        price=75,
    )

    Location.objects.create(
        producer=producer,
        place_and_time="Bogestadskolan (Hembygdsvägen) 17:30-18:00",
        date=datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=14),
        is_published=True,
    )
    Location.objects.create(
        producer=producer,
        place_and_time="Cleantechpark Gjuterigatan (rakt bakom tågstationen) 17:45-18:05",
        date=datetime.datetime.now(tz=datetime.UTC).date() + datetime.timedelta(days=14),
        is_published=True,
    )

    shutil.rmtree(str(settings.MEDIA_ROOT), ignore_errors=True)
    shutil.copytree(
        str(settings.PROJECT_ROOT / "../demo-media"),
        str(settings.MEDIA_ROOT / "producer-images"),
        dirs_exist_ok=True,
    )
    print("Development database generated.")
    print("Login with username: admin, password: admin 😄🎉")
