from django.contrib.auth import get_user_model
from django.test import TestCase

from skills.models import Category, Skill

User = get_user_model()


class OwnerPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="owner", password="x")
        cls.other = User.objects.create_user(username="other", password="x")
        cls.category = Category.objects.create(name="Cat", slug="cat")
        cls.skill = Skill.objects.create(
            title="S", description="D", category=cls.category,
            is_free=True, price=None,
            contact_preference=Skill.ContactPreference.EMAIL,
            availability=Skill.Availability.AVAILABLE,
            owner=cls.owner,
        )

    def test_non_owner_cannot_edit(self):
        self.client.login(username="other", password="x")
        r = self.client.get(f"/skills/{self.skill.pk}/edit/")
        self.assertEqual(r.status_code, 403)

    def test_non_owner_cannot_delete(self):
        self.client.login(username="other", password="x")
        r = self.client.post(f"/skills/{self.skill.pk}/delete/")
        self.assertEqual(r.status_code, 403)

    def test_owner_can_edit(self):
        self.client.login(username="owner", password="x")
        r = self.client.get(f"/skills/{self.skill.pk}/edit/")
        self.assertEqual(r.status_code, 200)

    def test_anonymous_redirects_to_login(self):
        r = self.client.get(f"/skills/{self.skill.pk}/edit/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/accounts/login/", r.headers["Location"])
