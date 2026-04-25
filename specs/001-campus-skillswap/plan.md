# Implementation Plan: Campus SkillSwap

**Branch**: `001-campus-skillswap` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-campus-skillswap/spec.md`

## Summary

Campus SkillSwap is a beginner-oriented student marketplace built as a single Django
project. Authenticated students can publish skill posts (CRUD), browse and search the
public catalogue without an account, request booking sessions on others' posts, and
leave ratings/reviews after an accepted booking. A personal dashboard surfaces a user's
own posts, sent requests, and received requests.

The technical approach honors the project constitution: a single Django LTS project,
SQLite for storage, server-rendered templates with Bootstrap 5 for the UI, and the
built-in `django.contrib.auth` / `django.contrib.admin` / `django.contrib.messages`
apps for authentication, administration, and user feedback. No SPA, no DRF, no
external auth. Vertical slices map directly to the spec's six user stories in
P1 → P3 order, so each priority level produces a runnable, demoable increment.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.2 LTS, Bootstrap 5 (CDN, no build step)
**Storage**: SQLite (single-file `db.sqlite3`, suitable for development and demos)
**Testing**: Django built-in test runner (`python manage.py test`) using `TestCase` /
`Client`; tests are OPTIONAL per constitution and added selectively for the
trickiest invariants (uniqueness, permissions, validation)
**Target Platform**: Local development via `runserver`; deployment target is a single
Linux/macOS host running `runserver` or `gunicorn` (out of scope for v1)
**Project Type**: Web application — single Django project, server-rendered
**Performance Goals**: First paint < 1 s on a typical desktop with seed data of ~25
posts; no specific QPS target (single-campus scale, low hundreds of users)
**Constraints**: Must run from a clean checkout with three commands
(`pip install -r requirements.txt`, `python manage.py migrate`,
`python manage.py runserver`); SQLite only; no JavaScript build pipeline
**Scale/Scope**: ~6 user stories, ~5 models, ~12 URL routes, ~8 templates; target
a single-campus or course-sized audience (low hundreds of users, low thousands
of posts)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.specify/memory/constitution.md` v1.0.0.

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. Beginner-First Pedagogy (NON-NEGOTIABLE) | ✅ Pass | Plan mandates teaching comments and per-slice browser walkthrough; data-model.md and research.md will explain WHY for each non-obvious choice. |
| II. Idiomatic Django, No Detours | ✅ Pass | All chosen tech is Django built-in: auth, admin, messages, ORM, ModelForm, generic CBVs/FBVs, template inheritance. The spec's "Next.js + Tailwind" assumption is overridden in favor of Bootstrap 5 + Django templates per constitution; resolution recorded in [research.md](./research.md). No DRF, no SPA. |
| III. Simplicity & YAGNI | ✅ Pass | One Django project, one Django app (`skills`); no service layer, no repository pattern, no custom managers beyond Django defaults. Three similar lines preferred over premature abstraction. SQLite + Bootstrap 5 retained. |
| IV. Incremental Vertical Slices | ✅ Pass | User stories US1–US6 from the spec map directly to vertical slices in P1 → P3 order. Each slice ends with a working URL and template usable through `runserver`. No "foundational refactor" task blocks more than one story; foundational items (project init, Category model + seed) are scoped narrowly and listed in tasks.md as the Foundational phase. |
| V. Readable Code with Teaching Comments | ✅ Pass | Plan requires inline comments on `on_delete` choices, custom `clean()` methods, `select_related`/`prefetch_related` use, custom validation, and the booking/review uniqueness constraints. Templates use `{% extends %}` / `{% block %}`. |

**Quality Gates inherited from the constitution** (all must pass before merge):

1. Constitution Check (this section) — filled, no unjustified violations.
2. Migrations committed alongside model edits — every model task in tasks.md will pair
   `models.py` edits with a `makemigrations` artifact.
3. Manual smoke test of every story slice via `runserver` — recorded in the slice's
   completion note.
4. Admin registration for every user-owned model — `Skill`, `Category`,
   `BookingRequest`, `Review` will all be registered in `admin.py`.
5. Beginner-readability review — at least one inline comment per non-obvious Django
   construct introduced.

No violations require Complexity Tracking entries (the table at the bottom of this
file is intentionally empty).

**Post-design re-check (after Phase 1)**: After producing `research.md`,
`data-model.md`, `contracts/url-routes.md`, and `quickstart.md`, all five
principles are still satisfied with no new violations:

- The data model uses only stock Django field types and constraint helpers;
  no custom managers, no abstract base classes, no third-party packages
  (Principles II, III).
- Routes are HTML-only with Django form/view conventions; the URL contract
  introduces no JSON envelope, no token auth, no API versioning (Principle II).
- Each user-story slice in `quickstart.md` is independently demoable through
  `runserver`, matching the spec's P1 → P3 ordering (Principle IV).
- `research.md` and `data-model.md` carry the WHY narrative that the
  implementation will mirror as inline comments per Principles I and V.
- The Free/priced rule, review uniqueness, and self-action prevention are
  all expressed at the form, model `clean()`, and database-constraint
  level — defense-in-depth that doubles as a teaching moment (Principle I).

## Project Structure

### Documentation (this feature)

```text
specs/001-campus-skillswap/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/
│   └── url-routes.md    # Phase 1 output: URL + view contract
└── tasks.md             # Phase 2 output (/speckit-tasks command — NOT created here)
```

### Source Code (repository root)

```text
manage.py
config/                            # Django project package (project-level settings)
├── __init__.py
├── settings.py                    # SQLite, INSTALLED_APPS, auth redirects, messages
├── urls.py                        # Project URL conf — includes skills.urls + admin
├── wsgi.py
└── asgi.py

skills/                            # The single Django app for v1
├── __init__.py
├── apps.py
├── admin.py                       # Admin registration: Category, Skill, BookingRequest, Review
├── forms.py                       # RegisterForm, SkillForm, BookingRequestForm, ReviewForm
├── models.py                      # Category, Skill, BookingRequest, Review
├── urls.py                        # App-level URL conf for everything skill-related
├── views.py                       # Function-based or class-based views per route
├── permissions.py                 # Tiny helpers (e.g., is_owner check) — only if reused
├── migrations/
│   ├── __init__.py
│   ├── 0001_initial.py            # Generated by makemigrations
│   └── 0002_seed_categories.py    # Data migration: seed default categories
├── fixtures/                      # (Optional) JSON seed data, if data migration not used
├── templates/
│   └── skills/
│       ├── base.html              # Bootstrap 5 layout, nav, messages block
│       ├── skill_list.html        # Public listing + search (US1, US3)
│       ├── skill_detail.html      # Detail + booking action + reviews (US1, US4, US5)
│       ├── skill_form.html        # Create/edit form (US2, US6)
│       ├── skill_confirm_delete.html  # Delete confirmation (US6)
│       ├── dashboard.html         # Personal dashboard (US6, US4 received requests)
│       └── partials/
│           ├── _skill_card.html
│           ├── _review_list.html
│           └── _booking_row.html
└── static/
    └── skills/
        └── css/
            └── app.css            # Project-specific styling on top of Bootstrap

accounts/                          # Tiny app for registration (login/logout reuse Django's built-ins)
├── __init__.py
├── apps.py
├── forms.py                       # EmailRequiredUserCreationForm
├── urls.py                        # /accounts/register/
├── views.py                       # RegisterView
├── templates/
│   └── registration/
│       ├── login.html             # Conventional path picked up by django.contrib.auth
│       ├── logged_out.html
│       └── register.html

tests/                             # OPTIONAL per constitution; added selectively
└── (per-app test_*.py if introduced)

requirements.txt                   # django>=5.2,<5.3 (LTS pin)
db.sqlite3                         # Created by `manage.py migrate`; gitignored
```

**Structure Decision**: One Django project (`config/`) with two Django apps:

- **`skills/`** holds the domain (Category, Skill, BookingRequest, Review) plus the
  dashboard. Keeping booking and review inside `skills/` rather than splitting them
  into separate apps follows YAGNI (Principle III) — these models share the `Skill`
  parent and have no independent re-use case.
- **`accounts/`** is a thin wrapper around `django.contrib.auth` that adds *only*
  the email-required registration form/view. Login and logout use Django's
  built-in `LoginView` / `LogoutView` directly; we do not re-implement them.

This is the simplest layout that still groups the per-app templates correctly for
Django's template loader (`templates/skills/...` and `templates/registration/...`).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified.**

No violations to track. The plan is fully constitution-compliant.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| _(none)_  | _(n/a)_    | _(n/a)_                              |
