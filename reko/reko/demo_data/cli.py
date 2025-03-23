# ruff: noqa: E402

import argparse
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reko.settings.dev")
django.setup()


from reko.reko.models import Producer

from .demo_data import create_user, generate_demo_data

parser = argparse.ArgumentParser()
parser.add_argument("--create-superuser", action="store_true")


def main() -> None:
    args = parser.parse_args()

    generate_demo_data()

    if args.create_superuser:
        create_user(
            email="admin@example.com",
            is_superuser=True,
        )
        producer = create_user(
            email="producer@example.com",
            is_superuser=False,
        )
        producer.producers.add(Producer.objects.get())

        print("Admin:     admin@example.com / password")
        print("Producer:  producer@example.com / password")

    print()
    print("Demo data has been populated! Happy hacking! 😄")
