from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from skills.models import Category, Skill

User = get_user_model()


class SkillCleanTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="u", password="x")
        cls.category = Category.objects.create(name="Test cat", slug="test-cat")

    def make(self, **overrides) -> Skill:
        defaults = {
            "title": "T",
            "description": "D",
            "category": self.category,
            "owner": self.user,
            "contact_preference": Skill.ContactPreference.EMAIL,
            "availability": Skill.Availability.AVAILABLE,
            "is_free": True,
            "price": None,
        }
        defaults.update(overrides)
        return Skill(**defaults)

    def test_free_with_no_price_is_ok(self):
        skill = self.make(is_free=True, price=None)
        skill.clean()
        self.assertIsNone(skill.price)

    def test_free_with_price_clears_price(self):
        skill = self.make(is_free=True, price=Decimal("10"))
        skill.clean()
        self.assertIsNone(skill.price)

    def test_priced_with_no_price_raises(self):
        skill = self.make(is_free=False, price=None)
        with self.assertRaises(ValidationError):
            skill.clean()

    def test_priced_with_negative_price_raises(self):
        skill = self.make(is_free=False, price=Decimal("-1"))
        with self.assertRaises(ValidationError):
            skill.clean()

    def test_priced_with_positive_price_is_ok(self):
        skill = self.make(is_free=False, price=Decimal("10"))
        skill.clean()
        self.assertEqual(skill.price, Decimal("10"))
