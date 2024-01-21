import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "reko.settings.dev"
django.setup()

import datetime  # noqa
from django.contrib.auth.models import User  # noqa
from reko.producer.models import Category, Product, Producer  # noqa
from reko.occasion.models import Occasion, Location  # noqa


def hermelins(grönsaker, dryck):
    producer = Producer.objects.create(
        name="Hermelins grönsaker",
        company_name="Hermelins grönsaker AB",
        organisation_number="559293-7287",
        slug="hermelins-grönsaker",
        image="producer-images/hermelinscover.jpg",
        description=(
            "Vi sår, rensar ogräs, skördar, tvättar och knippar för hand. "
            "Det gör vi för att respektive gröda finns på så pass små ytor att maskiner inte går att använda. "
            "Men även för att vi vill behandla grönsakerna med omsorg."
        ),
    )

    producer.categories.set([grönsaker, dryck])

    Product.objects.create(
        producer=producer,
        image="producer-images/hermelins1.jpg",
        name="Grönsakskasse",
        description="Se innehåll på bilden.",
        price=130,
    )

    Product.objects.create(
        producer=producer,
        image="producer-images/rodbetor.jpg",
        name="Rödbetor",
        price=25,
    )
    Product.objects.create(
        producer=producer,
        image="producer-images/gronkal.jpg",
        name="Grönkål",
        price=30,
    )

    Product.objects.create(
        producer=producer,
        image="producer-images/lok.jpg",
        name="Knippe Gullök",
        price=35,
    )
    Product.objects.create(
        producer=producer,
        image="producer-images/hermelins2.jpg",
        name="Monicas Jordgubbsaft",
        price=75,
    )
    return producer


def tomatboden(*, grönsaker):
    producer = Producer.objects.create(
        name="Tomatboden i Varv",
        company_name="Assarsson Trädgård AB",
        organisation_number="559293-7287",
        slug="tomatboden-i-varv",
        image="producer-images/tomatbodencover.jpg",
        product_description="Tomater",
        description="Vi odlar våra obesprutade tomater och gurka i växthus som värms med träpellets, allt bevattningsvatten recirkulerar och återanvänds i odlingen. Vi är certifierade enligt Svenskt Sigill och medlemmar i Östgötamat, läs gärna mer om oss på www.tomatboden.se",  # noqa
    )

    producer.categories.set([grönsaker])

    return producer


def main():
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(username="admin", password="admin")

    occasion = Occasion.objects.create(
        date=datetime.date(2021, 8, 26),
        is_published=True,
    )
    occasion.locations.set(
        [
            Location.objects.create(
                time_start=datetime.time(17, 00),
                time_end=datetime.time(17, 30),
                name="IKANO-huset parkering, Tornby",
                code="IK",
            ),
            Location.objects.create(
                time_start=datetime.time(17, 45),
                time_end=datetime.time(18, 5),
                name="Cleantechpark Gjuterigatan (rakt bakom tågstationen)",
                code="CT",
            ),
            Location.objects.create(
                time_start=datetime.time(18, 30),
                time_end=datetime.time(19, 00),
                name="Bogestadskolan (Hembygdsvägen)",
                code="BS",
            ),
        ]
    )

    Producer.objects.all().delete()

    (grönsaker, _) = Category.objects.get_or_create(name="Grönsaker", slug="grönsaker")
    (dryck, _) = Category.objects.get_or_create(name="Dryck", slug="dryck")
    (kött_fisk, _) = Category.objects.get_or_create(name="Kött&Fisk", slug="kött-fisk")
    (mejeri, _) = Category.objects.get_or_create(name="Mejeri", slug="mejeri")
    (honung, _) = Category.objects.get_or_create(name="Honung", slug="honung")
    (ägg, _) = Category.objects.get_or_create(name="Ägg", slug="ägg")

    occasion.producers.set(
        [
            hermelins(grönsaker=grönsaker, dryck=dryck),
            tomatboden(grönsaker=grönsaker),
        ]
    )


if __name__ == "__main__":
    main()
