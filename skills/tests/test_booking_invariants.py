from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from skills.models import BookingRequest, Category, Skill

User = get_user_model()


class BookingInvariantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner", password="x")
        cls.requester = User.objects.create_user(username="req", password="x")
        cls.category = Category.objects.create(name="Cat", slug="cat")
        cls.skill = Skill.objects.create(
            title="S", description="D", category=cls.category,
            is_free=True, price=None,
            contact_preference=Skill.ContactPreference.EMAIL,
            availability=Skill.Availability.AVAILABLE,
            owner=cls.owner,
        )

    def make_booking(self, **overrides) -> BookingRequest:
        defaults = {
            "requester": self.requester,
            "skill": self.skill,
            "message": "hi",
            "proposed_time": datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
        }
        defaults.update(overrides)
        return BookingRequest(**defaults)

    def test_self_booking_is_rejected(self):
        booking = self.make_booking(requester=self.owner)
        with self.assertRaises(ValidationError):
            booking.clean()

    def test_unavailable_skill_rejects_new_booking(self):
        self.skill.availability = Skill.Availability.UNAVAILABLE
        self.skill.save()
        booking = self.make_booking()
        with self.assertRaises(ValidationError):
            booking.clean()

    def test_available_skill_allows_booking(self):
        booking = self.make_booking()
        booking.clean()  # should not raise
