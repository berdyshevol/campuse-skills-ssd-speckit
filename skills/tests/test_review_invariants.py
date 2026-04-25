from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from skills.models import BookingRequest, Category, Review, Skill

User = get_user_model()


class ReviewInvariantTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner", password="x")
        cls.author = User.objects.create_user(username="author", password="x")
        cls.category = Category.objects.create(name="Cat", slug="cat")
        cls.skill = Skill.objects.create(
            title="S", description="D", category=cls.category,
            is_free=True, price=None,
            contact_preference=Skill.ContactPreference.EMAIL,
            availability=Skill.Availability.AVAILABLE,
            owner=cls.owner,
        )

    def _accepted_booking(self):
        return BookingRequest.objects.create(
            requester=self.author, skill=self.skill,
            message="ok", proposed_time=datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
            status=BookingRequest.Status.ACCEPTED,
        )

    def test_review_without_accepted_booking_rejected_by_clean(self):
        review = Review(author=self.author, skill=self.skill, rating=4, text="t")
        with self.assertRaises(ValidationError):
            review.clean()

    def test_update_or_create_keeps_uniqueness(self):
        self._accepted_booking()
        Review.objects.update_or_create(
            author=self.author, skill=self.skill,
            defaults={"rating": 4, "text": "first"},
        )
        Review.objects.update_or_create(
            author=self.author, skill=self.skill,
            defaults={"rating": 5, "text": "second"},
        )
        self.assertEqual(Review.objects.filter(author=self.author, skill=self.skill).count(), 1)
        review = Review.objects.get(author=self.author, skill=self.skill)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "second")

    def test_unique_constraint_blocks_duplicate_create(self):
        self._accepted_booking()
        Review.objects.create(author=self.author, skill=self.skill, rating=4, text="a")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(author=self.author, skill=self.skill, rating=5, text="b")
