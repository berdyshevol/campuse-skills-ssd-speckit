# Campus SkillSwap

A beginner-oriented student marketplace built as a single Django project.
Authenticated students can publish skill posts, browse and search the public
catalogue without an account, request booking sessions on others' posts, and
leave ratings/reviews after an accepted booking.

Built per [Spec Kit](https://github.com/github/spec-kit) feature
[`001-campus-skillswap`](specs/001-campus-skillswap/) following the project
[constitution](.specify/memory/constitution.md): Django 5.2 LTS, Bootstrap 5
via CDN, SQLite, server-rendered templates. No SPA, no DRF, no JavaScript
build pipeline.

## Quick start

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate             # creates db.sqlite3 + seeds 10 categories
python manage.py createsuperuser     # for /admin/
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

## Features

The six user stories from [`spec.md`](specs/001-campus-skillswap/spec.md), in
priority order:

| Priority | Story | What it does |
|----------|-------|--------------|
| P1 | US1 — Browse and discover | Anonymous visitors see the public skill listing and detail pages. |
| P1 | US2 — Register, sign in, post | Students register with a unique email, log in, and publish skill posts. |
| P2 | US3 — Search | Filter listings by case-insensitive title keyword and/or category. |
| P2 | US4 — Booking lifecycle | Logged-in users request bookings; owners accept or decline. |
| P3 | US5 — Reviews | Users with an accepted booking leave 1–5 star reviews; resubmit updates in place. |
| P3 | US6 — Manage listings | Owners edit or delete their own posts; non-owners get 403. |

Defense-in-depth invariants are enforced at form (`clean()`), view, and
database (`CheckConstraint`/`UniqueConstraint`) levels — see
[`data-model.md`](specs/001-campus-skillswap/data-model.md) and
[`research.md`](specs/001-campus-skillswap/research.md).

## Project layout

```text
manage.py
config/                 Django project package (settings, root URL conf)
accounts/               Registration app (login/logout reuse Django built-ins)
skills/                 Domain app: Category, Skill, BookingRequest, Review
  models.py             Models with clean() + DB constraints
  views.py              CBV/FBV per route in contracts/url-routes.md
  forms.py              SkillForm, BookingRequestForm, ReviewForm
  permissions.py        OwnerOnlyMixin (403 for non-owners)
  templates/skills/     Bootstrap 5 templates + partials
  migrations/           Includes 0002_seed_categories.py data migration
  tests/                Optional invariant tests (15 cases)
specs/001-campus-skillswap/
  spec.md, plan.md, research.md, data-model.md
  contracts/url-routes.md, quickstart.md, tasks.md
```

URL routes are documented in
[`contracts/url-routes.md`](specs/001-campus-skillswap/contracts/url-routes.md).

## Testing

```bash
python manage.py test
```

15 invariant tests cover the four highest-leverage rules: Skill Free/priced,
BookingRequest self/unavailable rejection, Review uniqueness +
accepted-booking gate, and owner-only permissions. Tests are optional per the
constitution; the canonical verification is the manual smoke walkthrough in
[`quickstart.md`](specs/001-campus-skillswap/quickstart.md).

## Admin

After `createsuperuser`, visit <http://127.0.0.1:8000/admin/>. Category, Skill,
BookingRequest, and Review are all registered. To retire a category, set
`is_active=False` rather than deleting it (Skill uses `on_delete=PROTECT`).

## Resetting the database

```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

Categories are re-seeded automatically by the data migration.
