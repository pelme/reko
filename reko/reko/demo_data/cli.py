# ruff: noqa: E402

import argparse
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reko.settings.dev")
django.setup()


from .demo_data import create_user, generate_demo_data

parser = argparse.ArgumentParser()
parser.add_argument("--create-superuser", action="store_true")


def main() -> None:
    args = parser.parse_args()

    producers = generate_demo_data()

    if args.create_superuser:
        superuser = create_user(
            email="admin@example.com",
            password="password",
            is_superuser=True,
        )
        print(f"Admin:     {superuser.email} / password")

    for producer in producers:
        user = create_user(
            email=producer.email,
            password="password",
            is_superuser=False,
        )
        user.producers.add(producer)
        print(f"Producer:  {user.email} / password")

    print()
    print("Demo data has been populated! Happy hacking! 😄")
