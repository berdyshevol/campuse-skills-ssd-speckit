"""Reset and seed a deterministic demo dataset for manual / e2e testing.

Usage: `python manage.py seed_demo`

Creates three users (alice, bob, charlie) and three skill posts across two
categories. Wipes any pre-existing rows for these usernames first so the
command is idempotent.
"""
from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from skills.models import BookingRequest, Category, Review, Skill

User = get_user_model()

DEMO_PASSWORD = "SkSwap!2025"
DEMO_USERS = [
    ("alice", "alice@example.com"),
    ("bob", "bob@example.com"),
    ("charlie", "charlie@example.com"),
]


class Command(BaseCommand):
    help = "Reset and seed a deterministic demo dataset for e2e testing."

    @transaction.atomic
    def handle(self, *args, **options):
        # Wipe demo state. Real Category rows from the data migration are kept.
        usernames = [u for u, _ in DEMO_USERS]
        BookingRequest.objects.filter(requester__username__in=usernames).delete()
        BookingRequest.objects.filter(skill__owner__username__in=usernames).delete()
        Review.objects.filter(author__username__in=usernames).delete()
        Skill.objects.filter(owner__username__in=usernames).delete()
        User.objects.filter(username__in=usernames).delete()

        users = {}
        for username, email in DEMO_USERS:
            user = User.objects.create_user(
                username=username, email=email, password=DEMO_PASSWORD,
            )
            users[username] = user
            self.stdout.write(f"  created user: {username}")

        # Two distinct categories so US3 category filter has something to do.
        cat_prog = Category.objects.get(name="Programming & Tech")
        cat_lang = Category.objects.get(name="Languages")

        skills_data = [
            {
                "title": "Python tutoring",
                "description": "Hands-on Python: variables, functions, OOP, debugging.",
                "category": cat_prog,
                "is_free": False,
                "price": Decimal("20.00"),
                "owner": users["alice"],
            },
            {
                "title": "Algebra basics",
                "description": "Algebra I/II review for first-year students.",
                "category": cat_prog,
                "is_free": True,
                "price": None,
                "owner": users["alice"],
            },
            {
                "title": "Spanish conversation",
                "description": "Casual Spanish conversation practice.",
                "category": cat_lang,
                "is_free": False,
                "price": Decimal("15.00"),
                "owner": users["bob"],
            },
        ]
        for data in skills_data:
            Skill.objects.create(
                contact_preference=Skill.ContactPreference.EMAIL,
                availability=Skill.Availability.AVAILABLE,
                **data,
            )
            self.stdout.write(f"  created skill: {data['title']} (owner={data['owner'].username})")

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(DEMO_USERS)} users + {len(skills_data)} skills."
        ))
