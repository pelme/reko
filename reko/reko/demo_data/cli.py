# ruff: noqa: E402

import argparse
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reko.settings.dev")
django.setup()


from reko.reko.models import User

from .demo_data import generate_demo_data

parser = argparse.ArgumentParser()
parser.add_argument("--create-superuser", action="store_true")


def main() -> None:
    args = parser.parse_args()

    generate_demo_data()

    if args.create_superuser:
        admin_email = "admin@example.com"
        admin_password = "admin"

        if User.objects.filter(email=admin_email).exists():
            print("Admin user already exists, skipping creation.")
        else:
            User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
            )

            print("Admin user created.")
            print(f"Admin login:     {admin_email}")
            print(f"Admin password:  {admin_password}")

    print()
    print("Demo data has been populated! Happy hacking! 😄")
