from django.db import migrations
from django.utils.text import slugify

# We seed in a migration (not a fixture) so a fresh `manage.py migrate` produces
# a usable database with the default taxonomy already present. Idempotent via
# get_or_create so re-running the migration on an existing DB is safe.
DEFAULT_CATEGORIES = [
    "Tutoring — Math",
    "Tutoring — Science",
    "Tutoring — Humanities",
    "Languages",
    "Programming & Tech",
    "Music",
    "Art & Design",
    "Sports & Fitness",
    "Cooking",
    "Other",
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("skills", "Category")
    for name in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(
            name=name,
            defaults={"slug": slugify(name), "is_active": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("skills", "0001_initial"),
    ]

    operations = [
        # Reverse is a no-op: removing the seed rows on `migrate skills zero`
        # would risk cascading into user data. Acceptable for v1.
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
