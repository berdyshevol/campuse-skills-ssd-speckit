# Campus SkillSwap

> A small student-to-student skill marketplace — post a skill you can teach,
> browse what others offer, request a session, and review afterwards.

**Live demo:** <https://berdyshevo.pythonanywhere.com/> · log in with one of
the [demo accounts](#demo-accounts) below.

Built end-to-end with [**GitHub Spec Kit**](https://github.com/github/spec-kit):
the spec, plan, data model, and tasks under
[`specs/001-campus-skillswap/`](specs/001-campus-skillswap/) were authored
*before* any code, then implemented to match. The entire feature lives on
branch [`001-campus-skillswap`](../../tree/001-campus-skillswap).

**Stack:** Django 5.2 LTS · SQLite · server-rendered templates · Bootstrap 5
(CDN). No SPA, no DRF, no JS build step.

---

## Quick start

Requires Python 3.11+.

```bash
git clone https://github.com/berdyshevol/campuse-skills-ssd-speckit.git
cd campuse-skills-ssd-speckit
git checkout 001-campus-skillswap

python3 -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate                  # creates db.sqlite3, seeds 10 categories
python manage.py seed_demo                # optional: 3 demo users + 3 skills
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

### Demo accounts

`python manage.py seed_demo` creates three users (password `SkSwap!2025`):

| User    | Owns                                              |
|---------|---------------------------------------------------|
| alice   | "Python tutoring" ($20), "Algebra basics" (Free)  |
| bob     | "Spanish conversation" ($15)                      |
| charlie | nothing — useful as a "stranger" account          |

For Django admin: `python manage.py createsuperuser` and visit
<http://127.0.0.1:8000/admin/>.

---

## What's in it

The six user stories from
[`spec.md`](specs/001-campus-skillswap/spec.md), in priority order:

| #   | Story                          | What it does                                                                |
|-----|--------------------------------|-----------------------------------------------------------------------------|
| US1 | Browse & discover              | Anonymous visitors see the catalogue and detail pages.                      |
| US2 | Register, sign in, post        | Students register, log in, and publish skill posts.                         |
| US3 | Search                         | Filter listings by case-insensitive title keyword and/or category.          |
| US4 | Booking lifecycle              | Logged-in users request bookings; owners accept or decline.                 |
| US5 | Reviews                        | After an accepted booking, leave 1–5★; resubmit updates in place.           |
| US6 | Manage listings                | Owners edit/delete their own posts; non-owners get 403.                     |

Invariants are enforced at form (`clean()`), view, and database
(`CheckConstraint` / `UniqueConstraint`) levels — see
[`data-model.md`](specs/001-campus-skillswap/data-model.md) and
[`research.md`](specs/001-campus-skillswap/research.md).

---

## Project layout

```text
manage.py
config/                       Django project package (settings, root URL conf)
accounts/                     Registration app (login/logout reuse Django built-ins)
skills/
  models.py                   Category, Skill, BookingRequest, Review (+ DB constraints)
  views.py                    Views per route in contracts/url-routes.md
  forms.py                    SkillForm, BookingRequestForm, ReviewForm
  permissions.py              OwnerOnlyMixin (403 for non-owners)
  templates/skills/           Bootstrap 5 templates + partials
  migrations/                 Includes 0002_seed_categories.py data migration
  management/commands/
    seed_demo.py              Resets + seeds the demo dataset
  tests/                      Invariant tests (15 cases)
specs/001-campus-skillswap/
  spec.md, plan.md, research.md, data-model.md
  contracts/url-routes.md, quickstart.md, tasks.md
tests/e2e/scenarios.md        Manual Playwright walkthrough (US1, US2, US3, US6)
```

URL routes:
[`specs/001-campus-skillswap/contracts/url-routes.md`](specs/001-campus-skillswap/contracts/url-routes.md).

---

## Testing

**Unit / invariant tests** (Django `TestCase`):

```bash
python manage.py test
```

15 cases covering the highest-leverage rules: Skill Free/priced,
BookingRequest self / unavailable rejection, Review uniqueness +
accepted-booking gate, and owner-only permissions.

**Manual E2E scenarios** — Playwright walkthrough in
[`tests/e2e/scenarios.md`](tests/e2e/scenarios.md). Covers US1, US2, US3, US6.
Run after `seed_demo` and update the checkboxes as you go.

---

## Resetting the database

```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_demo                # optional
```

Categories are re-seeded automatically by the data migration. To retire a
category in the admin, set `is_active=False` rather than deleting it
(Skill uses `on_delete=PROTECT`).

---

## Spec Kit artifacts

The spec-first workflow is documented in
[`specs/001-campus-skillswap/`](specs/001-campus-skillswap/):

- [`spec.md`](specs/001-campus-skillswap/spec.md) — user stories + acceptance criteria
- [`plan.md`](specs/001-campus-skillswap/plan.md) — implementation plan
- [`research.md`](specs/001-campus-skillswap/research.md) — design decisions
- [`data-model.md`](specs/001-campus-skillswap/data-model.md) — entities + constraints
- [`contracts/url-routes.md`](specs/001-campus-skillswap/contracts/url-routes.md) — URL contract
- [`tasks.md`](specs/001-campus-skillswap/tasks.md) — task breakdown
- [`quickstart.md`](specs/001-campus-skillswap/quickstart.md) — manual smoke test

Project rules are in
[`.specify/memory/constitution.md`](.specify/memory/constitution.md).
