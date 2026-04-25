---
description: "Task list for Campus SkillSwap implementation (single Django project, Bootstrap 5, SQLite)"
---

# Tasks: Campus SkillSwap

**Input**: Design documents from `/specs/001-campus-skillswap/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/url-routes.md, quickstart.md

**Tests**: OPTIONAL per constitution. We add a small targeted suite for the four invariants identified in `research.md` §R10 (Skill Free/priced rule, BookingRequest self/unavailable rejection, Review uniqueness + accepted-booking gate, owner-only permissions). All other testing is the manual smoke-test walkthrough in `quickstart.md`.

**Organization**: Tasks are grouped by user story so each priority slice produces a runnable, demoable increment per Principle IV (Incremental Vertical Slices).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story tag (US1–US6); Setup, Foundational, and Polish phases carry no tag
- All paths are relative to repository root

## Path Conventions

- Repository root: `/Users/oleg/Documents/BAYLOR/AI/campuse-skills-ssd-speckit/`
- Django project package: `config/`
- Apps: `skills/`, `accounts/`
- Templates live under each app's `templates/` directory; per Django convention, `skills/` uses `templates/skills/...` and `accounts/` uses `templates/registration/...` so `LoginView`/`LogoutView` find them automatically.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization — Django project, two apps, settings, root URL conf.

- [X] T001 Create `requirements.txt` at repo root with the single line `django>=5.2,<5.3` (per `research.md` §R2)
- [X] T002 Initialize the Django project package by running `django-admin startproject config .` from repo root (creates `manage.py`, `config/__init__.py`, `config/settings.py`, `config/urls.py`, `config/wsgi.py`, `config/asgi.py`)
- [X] T003 [P] Create the `skills` app by running `python manage.py startapp skills` from repo root
- [X] T004 [P] Create the `accounts` app by running `python manage.py startapp accounts` from repo root
- [X] T005 Configure `config/settings.py`: add `"skills"` and `"accounts"` to `INSTALLED_APPS`; set `LOGIN_URL = "login"`, `LOGIN_REDIRECT_URL = "skills:dashboard"`, `LOGOUT_REDIRECT_URL = "skills:list"`; add `MESSAGE_TAGS` mapping (DEBUG→secondary, INFO→info, SUCCESS→success, WARNING→warning, ERROR→danger) per `contracts/url-routes.md` "Settings keys" section; confirm `TEMPLATES["APP_DIRS"]` is `True` so per-app `templates/` directories load automatically
- [X] T006 [P] Extend the existing `.gitignore` at repo root to include `db.sqlite3`, `.venv/`, `__pycache__/`, and `*.pyc`
- [X] T007 [P] Configure `config/urls.py` to include: `admin.site.urls`, `django.contrib.auth.urls` mounted at `accounts/`, `accounts.urls` mounted at `accounts/`, and `skills.urls` mounted at root `""` (per `contracts/url-routes.md` "URL conventions")
- [X] T008 [P] Create `skills/urls.py` with `app_name = "skills"` and an empty `urlpatterns = []` list (routes are added per user story)
- [X] T009 [P] Create `accounts/urls.py` with `app_name = "accounts"` and an empty `urlpatterns = []` list

**Checkpoint**: `python manage.py check` passes, `python manage.py runserver` boots (404 on `/` is expected at this point).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Items used by every user story. Scoped narrowly per Principle III: only the base template, the `Category` model, its seed migration, and admin registration. No premature scaffolding for Skill, BookingRequest, or Review — those land inside the user-story phase that needs them first.

**⚠️ CRITICAL**: No user-story phase may begin until this phase is complete.

- [X] T010 Create the base layout `skills/templates/skills/base.html` with Bootstrap 5 CDN `<link>` and `<script>`, a top nav with brand link to `{% url "skills:list" %}` (auth links added in US2), a `{% block content %}` body, and a Bootstrap-styled `{% if messages %}` block using the `MESSAGE_TAGS` from settings
- [X] T011 [P] Create `skills/static/skills/css/app.css` with empty stylesheet (project-specific overrides on top of Bootstrap; populated as needed in later tasks)
- [X] T012 Define the `Category` model in `skills/models.py` per `data-model.md` §2 (fields: `name` unique, `slug` unique, `description` blank, `is_active` default True; `Meta.ordering = ["name"]`, `verbose_name_plural = "categories"`; `__str__` returns `self.name`) — include an inline teaching comment on why we do not use `TextChoices` (FR-028 admin manageability)
- [X] T013 Generate the initial migration by running `python manage.py makemigrations skills` (produces `skills/migrations/0001_initial.py` containing `Category`)
- [X] T014 Create the data migration `skills/migrations/0002_seed_categories.py` with a `RunPython` operation that idempotently `get_or_create`s the 10 categories listed in `research.md` §R5; include a reverse function (`migrations.RunPython.noop` is acceptable for v1) and an inline comment explaining why we seed in a migration rather than a fixture
- [X] T015 Register `Category` in `skills/admin.py` with `list_display = ("name", "slug", "is_active")`, `prepopulated_fields = {"slug": ("name",)}`, and `list_filter = ("is_active",)`
- [X] T016 Apply migrations end-to-end: `python manage.py migrate` — verify `db.sqlite3` is created and the 10 seeded categories appear under `/admin/` after `createsuperuser`

**Checkpoint**: Foundation ready — every user story below can now begin.

---

## Phase 3: User Story 1 — Browse and Discover Skills as a Visitor (Priority: P1) 🎯 MVP

**Goal**: A logged-out visitor can open the public listings page, see skill cards (title, category, price/Free, availability), click into a detail page, and read full skill information without authentication.

**Independent Test**: With one or more `Skill` rows seeded via `/admin/`, an anonymous browser session at `http://127.0.0.1:8000/` shows the listing, clicking a card opens the detail page, and no login prompt is encountered. Empty state shows when there are no skills.

**Spec refs**: FR-010, FR-011, FR-014, FR-030 / acceptance scenarios US1.1–US1.3.

### Implementation for User Story 1

- [X] T017 [US1] Add the `Skill` model + nested `ContactPreference` and `Availability` `TextChoices` to `skills/models.py` per `data-model.md` §3 (fields, `Meta.ordering = ["-created_at"]`, `Meta.constraints` with `skill_free_xor_priced` `CheckConstraint`, `Meta.indexes` for `-created_at`, `clean()` enforcing Free/priced rule, `display_price` property, `can_be_booked_by()` method, `__str__`); include teaching comments on `on_delete=PROTECT` for `category`, `on_delete=CASCADE` for `owner`, and the rationale for the `CheckConstraint`
- [X] T018 [US1] Generate the Skill migration: `python manage.py makemigrations skills` (produces `skills/migrations/0003_skill.py`); run `python manage.py migrate` to apply
- [X] T019 [P] [US1] Register `Skill` in `skills/admin.py` with `list_display = ("title", "owner", "category", "is_free", "price", "availability", "created_at")`, `list_filter = ("category", "availability", "is_free")`, `search_fields = ("title", "description")`, `raw_id_fields = ("owner",)`
- [X] T020 [P] [US1] Create the partial `skills/templates/skills/partials/_skill_card.html` rendering one skill card (title link to detail, category, `display_price`, availability badge)
- [X] T021 [US1] Create `skills/templates/skills/skill_list.html` extending `skills/base.html` — render paginated cards by including `_skill_card.html`, plus the empty-state copy (FR-030 / US1.3) inviting registration when `object_list` is empty (search form is added in US3)
- [X] T022 [P] [US1] Create `skills/templates/skills/skill_detail.html` extending `skills/base.html` — show `title`, `category`, owner display name, `display_price`, `availability`, `contact_preference`, full `description`; review list and booking form blocks are added in US4/US5
- [X] T023 [US1] Implement `SkillListView` (CBV `ListView` recommended) in `skills/views.py` with `model = Skill`, `template_name = "skills/skill_list.html"`, `context_object_name = "skills"`, `paginate_by = 12`, default queryset ordering `-created_at` (FR-014); use `select_related("category", "owner")` and add an inline comment explaining why
- [X] T024 [US1] Implement `SkillDetailView` (CBV `DetailView`) in `skills/views.py` with `model = Skill`, `template_name = "skills/skill_detail.html"`, using `select_related("category", "owner")`; 404 path is automatic via `get_object_or_404`
- [X] T025 [US1] Wire URL patterns in `skills/urls.py`: `path("", SkillListView.as_view(), name="list")` and `path("skills/<int:pk>/", SkillDetailView.as_view(), name="detail")`
- [X] T026 [US1] Run the US1 section of `quickstart.md` ("Smoke-test walkthrough → US1") in a private browser window and record PASS/FAIL with notes in the commit message

**Checkpoint**: User Story 1 is fully demoable. The MVP supply side (US2) is next.

---

## Phase 4: User Story 2 — Register, Sign In, and Post a Skill (Priority: P1)

**Goal**: A new student can register, log in, log out, and create a skill post. The post appears on the public listing and on their dashboard. After logout/login the post persists.

**Independent Test**: Visitor → register form → logged in → `Create skill` form → valid submit → skill appears at `/` and at `/dashboard/`. Logout, log back in, dashboard still shows the skill. Invalid submit (missing title) shows a field error and saves nothing.

**Spec refs**: FR-001, FR-002, FR-003, FR-004, FR-005, FR-009, FR-029 / acceptance scenarios US2.1–US2.5.

### Implementation for User Story 2

- [X] T027 [P] [US2] Create `accounts/forms.py` with `RegisterForm(UserCreationForm)` adding a required, unique `email = EmailField(required=True)` and a `clean_email()` that rejects duplicates against `User.objects.filter(email__iexact=...)`; teaching comment notes why we override the form rather than swapping `User` (research §R3)
- [X] T028 [P] [US2] Create `accounts/templates/registration/login.html` extending `skills/base.html` and rendering `form` with Bootstrap field markup and a "Register" link to `{% url "accounts:register" %}`
- [X] T029 [P] [US2] Create `accounts/templates/registration/logged_out.html` extending `skills/base.html` with a brief "You have been logged out" message and a link back to `{% url "skills:list" %}`
- [X] T030 [P] [US2] Create `accounts/templates/registration/register.html` extending `skills/base.html` and rendering `RegisterForm`
- [X] T031 [US2] Implement `RegisterView` in `accounts/views.py` (FBV or CBV) — on POST: save user, call `login(request, user)`, set a `messages.success` flash, redirect to `{% url "skills:dashboard" %}`; on GET or invalid POST render `registration/register.html`
- [X] T032 [US2] Wire `path("register/", RegisterView.as_view(), name="register")` in `accounts/urls.py`
- [X] T033 [P] [US2] Create `SkillForm(ModelForm)` in `skills/forms.py` exposing `title`, `description`, `category`, `is_free`, `price`, `contact_preference`, `availability`; in `__init__` filter `self.fields["category"].queryset` to `Category.objects.filter(is_active=True)`; in `clean()` enforce the Free/priced rule (research §R6) — when `is_free=True` set `cleaned_data["price"] = None`, when `is_free=False` require `price` present and `>= 0`, raising `ValidationError` on `price` otherwise
- [X] T034 [P] [US2] Create `skills/templates/skills/skill_form.html` extending `skills/base.html` and rendering `SkillForm` with Bootstrap field markup; this template is reused for create and edit (US6)
- [X] T035 [US2] Implement `SkillCreateView(LoginRequiredMixin, CreateView)` in `skills/views.py` with `model = Skill`, `form_class = SkillForm`, `template_name = "skills/skill_form.html"`; override `form_valid()` to set `form.instance.owner = self.request.user` and add `messages.success`; redirect to the new skill's detail page on success
- [X] T036 [P] [US2] Implement a minimal `DashboardView(LoginRequiredMixin, TemplateView)` in `skills/views.py` with `template_name = "skills/dashboard.html"`; context provides `request.user` only (sections are filled in by US4 and US6)
- [X] T037 [P] [US2] Create `skills/templates/skills/dashboard.html` extending `skills/base.html` with a greeting and stub sections "My posts (coming in US6)", "Requests sent / received (coming in US4)" — replaced incrementally
- [X] T038 [US2] Add the routes to `skills/urls.py`: `path("skills/new/", SkillCreateView.as_view(), name="create")` and `path("dashboard/", DashboardView.as_view(), name="dashboard")`
- [X] T039 [US2] Update `skills/templates/skills/base.html` nav: add "Login" + "Register" links when `user.is_authenticated` is False; add "Dashboard" + "Create skill" + a logout `<form method="post">` (Django requires POST for logout) when authenticated
- [X] T040 [US2] Run the US2 section of `quickstart.md` ("Smoke-test walkthrough → US2") and record PASS/FAIL in the commit message

**Checkpoint**: P1 complete — Campus SkillSwap is a working two-sided marketplace. Stop here for the MVP demo.

---

## Phase 5: User Story 3 — Search Skills by Title or Category (Priority: P2)

**Goal**: A user (logged in or not) can filter the listing by keyword (case-insensitive title substring) and/or category. Filters combine and clear.

**Independent Test**: With multiple skills across two categories, the listing narrows correctly when typing a keyword, when picking a category, and when both are combined. Empty result shows the "no matches" empty state with a reset link. Clearing returns the full list.

**Spec refs**: FR-012, FR-013, FR-014, FR-030 / acceptance scenarios US3.1–US3.4.

### Implementation for User Story 3

- [X] T041 [US3] Update `SkillListView` in `skills/views.py` to read `self.request.GET.get("q", "").strip()` and `self.request.GET.get("category")`; override `get_queryset()` to apply `filter(title__icontains=q)` when `q` is non-empty and `filter(category_id=category)` when `category` is provided; preserve existing `select_related` and `-created_at` ordering (research §R4)
- [X] T042 [US3] Override `get_context_data()` on `SkillListView` to add `q`, `selected_category`, and `categories = Category.objects.filter(is_active=True)` so the template can render the filter form with its current state retained
- [X] T043 [US3] Update `skills/templates/skills/skill_list.html`: add a `<form method="get">` with a text input bound to `q`, a `<select>` populated from `categories`, a "Search" submit button, and a "Clear" link to `{% url "skills:list" %}`; render pagination links preserving query parameters; when `object_list` is empty AND filters are active render the "no skills match your search" empty state with the same Clear link (FR-030 / US3.3)
- [X] T044 [US3] Run the US3 section of `quickstart.md` ("Smoke-test walkthrough → US3") and record PASS/FAIL

**Checkpoint**: Listings are now intentional discovery, not just scrolling.

---

## Phase 6: User Story 4 — Request a Booking/Session for a Skill (Priority: P2)

**Goal**: A logged-in user submits a booking request on a skill they don't own. Status starts `pending`. The owner can `accept` or `decline`. Both parties see the current status on their dashboards. Self-booking and booking on `unavailable` skills are blocked.

**Independent Test**: Two-account flow per `quickstart.md` US4. Requester creates request → Owner sees it received and accepts → Requester sees status flip to `accepted`. Anonymous attempt redirects to login. Owner viewing their own detail page sees no booking form. Booking on an `unavailable` skill is rejected.

**Spec refs**: FR-015, FR-016, FR-017, FR-018, FR-019, FR-020, FR-029 / acceptance scenarios US4.1–US4.4.

### Implementation for User Story 4

- [X] T045 [US4] Add the `BookingRequest` model + `Status` `TextChoices` to `skills/models.py` per `data-model.md` §4 (fields, `Meta.ordering = ["-created_at"]`, `Meta.constraints` with `bookingrequest_status_valid` `CheckConstraint`, `Meta.indexes` for `(requester, status)` and `(skill, status)`, `clean()` enforcing `requester != skill.owner` and rejecting creation when `skill.availability != "available"`, `__str__`); include a teaching comment on the two-place defense (clean() + DB constraint)
- [X] T046 [US4] Run `python manage.py makemigrations skills` (produces `skills/migrations/0004_bookingrequest.py`); apply with `migrate`
- [X] T047 [P] [US4] Register `BookingRequest` in `skills/admin.py` with `list_display = ("skill", "requester", "status", "created_at")`, `list_filter = ("status",)`, `raw_id_fields = ("skill", "requester")`
- [X] T048 [P] [US4] Add `BookingRequestForm(ModelForm)` to `skills/forms.py` exposing only `message` and `proposed_time` (the view sets `requester` and `skill`); use a Bootstrap-friendly `widgets = {"proposed_time": forms.DateTimeInput(attrs={"type": "datetime-local"})}`
- [X] T049 [P] [US4] Create `skills/permissions.py` with a small `OwnerOnlyMixin` that overrides `dispatch()` to return `HttpResponseForbidden` unless `request.user == self.get_object().owner`; add a teaching comment that this is preferred over `UserPassesTestMixin` for readability (research §R9)
- [X] T050 [P] [US4] Create `skills/templates/skills/partials/_booking_row.html` rendering one row of a booking request (skill title link, requester or owner counterparty, message snippet, proposed_time, status badge); the template accepts a `perspective` context variable (`"sent"` vs `"received"`) and renders accept/decline forms when `perspective == "received"` and `status == "pending"`
- [X] T051 [US4] Implement `RequestBookingView(LoginRequiredMixin, View)` in `skills/views.py` with POST-only `post()` that loads the skill via `get_object_or_404`, returns 403 if `request.user == skill.owner` (defense in depth), validates `BookingRequestForm`, runs `clean()` (which rejects unavailable skills), saves with `requester=request.user, skill=skill, status=Status.PENDING`, sets `messages.success`, and redirects to `skills:detail`; on validation failure set `messages.error` with the form's first error and redirect back to the detail page
- [X] T052 [US4] Implement `RespondRequestView(LoginRequiredMixin, View)` in `skills/views.py` with POST-only `post()` that loads `BookingRequest` by `pk`, returns 403 unless `request.user == booking.skill.owner`, reads `request.POST["action"]` ∈ `{"accept", "decline"}`, updates `status` to `Status.ACCEPTED` or `Status.DECLINED`, saves, sets `messages.success`, and redirects to `skills:dashboard`
- [X] T053 [US4] Replace the stub `DashboardView` in `skills/views.py` with a full implementation: `get_context_data()` returns `requests_sent = BookingRequest.objects.filter(requester=user).select_related("skill", "skill__owner")` and `requests_received = BookingRequest.objects.filter(skill__owner=user).select_related("skill", "requester")`, both ordered by `-created_at`; my-skills section is added in US6
- [X] T054 [US4] Update `skills/templates/skills/dashboard.html` to render the "Requests sent" and "Requests received" sections by looping `_booking_row.html` with the appropriate `perspective`; show empty-state copy in each section when the list is empty (FR-030)
- [X] T055 [US4] Update `skills/templates/skills/skill_detail.html` to render the booking form inside `{% if user.is_authenticated and user != skill.owner and skill.availability == "available" %}`; show an info banner when `skill.availability == "unavailable"` so users understand why the form is hidden
- [X] T056 [US4] Wire routes in `skills/urls.py`: `path("skills/<int:pk>/request/", RequestBookingView.as_view(), name="request_booking")` and `path("requests/<int:pk>/respond/", RespondRequestView.as_view(), name="respond_request")`
- [X] T057 [US4] Run the US4 section of `quickstart.md` ("Smoke-test walkthrough → US4") with two browser sessions and record PASS/FAIL

**Checkpoint**: Booking flow works end-to-end. Reviews (US5) become unblocked.

---

## Phase 7: User Story 5 — Rate and Review a Skill (Priority: P3)

**Goal**: A user with an `accepted` booking on a skill submits a 1–5 rating + text review. Detail page shows individual reviews, an average rating (1 decimal), and a count. Owners cannot review their own skill. A second submit by the same author updates the existing review (FR-024).

**Independent Test**: Two-account flow per `quickstart.md` US5. Requester (with accepted booking) submits 4-star review → appears on detail page, average shows `4.0`, count `1`. Re-submit at 5 stars → review row count remains `1`, average updates to `5.0`. Owner's own skill page shows no review form. A user with no accepted booking has the form hidden or the submit rejected.

**Spec refs**: FR-021, FR-022, FR-023, FR-024, FR-029 / acceptance scenarios US5.1–US5.4.

### Implementation for User Story 5

- [X] T058 [US5] Add the `Review` model to `skills/models.py` per `data-model.md` §5 (fields, `Meta.ordering = ["-created_at"]`, `Meta.constraints` with `unique_review_per_author_skill` `UniqueConstraint` and `review_rating_range` `CheckConstraint`, `clean()` enforcing `author != skill.owner` and `BookingRequest.objects.filter(requester=author, skill=skill, status="accepted").exists()`, `__str__`); include a teaching comment explaining `update_or_create` semantics for FR-024
- [X] T059 [US5] Run `python manage.py makemigrations skills` (produces `skills/migrations/0005_review.py`); apply
- [X] T060 [P] [US5] Register `Review` in `skills/admin.py` with `list_display = ("skill", "author", "rating", "created_at")`, `list_filter = ("rating",)`, `raw_id_fields = ("skill", "author")`
- [X] T061 [P] [US5] Add `ReviewForm(ModelForm)` to `skills/forms.py` exposing only `rating` and `text`; render `rating` as a number input bounded 1–5 (or radio group)
- [X] T062 [P] [US5] Create `skills/templates/skills/partials/_review_list.html` looping reviews and rendering author display name, rating (e.g., `★` glyphs), `text`, and `created_at`
- [X] T063 [US5] Implement `SubmitReviewView(LoginRequiredMixin, View)` in `skills/views.py` with POST-only `post()` that: loads skill via `get_object_or_404`; returns 403 if `request.user == skill.owner`; verifies `BookingRequest.objects.filter(requester=request.user, skill=skill, status="accepted").exists()` else `messages.error` + redirect to detail; validates `ReviewForm`; calls `Review.objects.update_or_create(author=request.user, skill=skill, defaults={"rating": ..., "text": ...})`; sets `messages.success`; redirects to `skills:detail`
- [X] T064 [US5] Update `SkillDetailView.get_context_data()` to add `reviews = skill.reviews.select_related("author").order_by("-created_at")[:20]`, `review_aggregate = skill.reviews.aggregate(avg=Avg("rating"), count=Count("id"))`, and `can_review = user.is_authenticated and user != skill.owner and BookingRequest.objects.filter(requester=user, skill=skill, status="accepted").exists()` so the template can decide whether to render the review form
- [X] T065 [US5] Update `skills/templates/skills/skill_detail.html` to render: average rating (rounded to 1 decimal via `floatformat:1`) and review count when `count > 0`, the `_review_list.html` partial, and the `ReviewForm` inside `{% if can_review %}`
- [X] T066 [US5] Wire `path("skills/<int:pk>/review/", SubmitReviewView.as_view(), name="submit_review")` in `skills/urls.py`
- [X] T067 [US5] Run the US5 section of `quickstart.md` ("Smoke-test walkthrough → US5") and record PASS/FAIL

**Checkpoint**: Trust signals on listings work; remaining gap is owner self-management (US6).

---

## Phase 8: User Story 6 — Manage Personal Listings via Dashboard (Priority: P3)

**Goal**: An owner edits or deletes their own skill posts from the dashboard. Public listing reflects the change. Non-owners attempting edit/delete URLs receive 403.

**Independent Test**: Owner opens dashboard → "My posts" section lists every skill they own with Edit/Delete actions → editing a price updates the public detail page → deleting a skill removes it from `/` and `/dashboard/`. Direct URL access by another user returns 403.

**Spec refs**: FR-006, FR-007, FR-008, FR-025, FR-026, FR-029 / acceptance scenarios US6.1–US6.4.

### Implementation for User Story 6

- [X] T068 [P] [US6] Implement `SkillUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView)` in `skills/views.py` reusing `SkillForm` and `skills/skill_form.html`; on success set `messages.success` and redirect to `skills:detail`
- [X] T069 [P] [US6] Implement `SkillDeleteView(LoginRequiredMixin, OwnerOnlyMixin, DeleteView)` in `skills/views.py` with `template_name = "skills/skill_confirm_delete.html"` and `success_url = reverse_lazy("skills:list")`; set `messages.success` after deletion via `delete()` override
- [X] T070 [P] [US6] Create `skills/templates/skills/skill_confirm_delete.html` extending `skills/base.html` with a confirm prompt, a POST `<form>` with `{% csrf_token %}` submitting to the delete URL, and a Cancel link back to `skills:detail`
- [X] T071 [US6] Update `DashboardView.get_context_data()` to also include `my_skills = Skill.objects.filter(owner=user).select_related("category").order_by("-created_at")`
- [X] T072 [US6] Update `skills/templates/skills/dashboard.html` to render the "My posts" section with an Edit and Delete action per skill (links pointing to `skills:update` and `skills:delete`); empty-state copy invites creating the first skill
- [X] T073 [US6] Add owner-only Edit/Delete action links to `skills/templates/skills/skill_detail.html` inside `{% if user == skill.owner %}`
- [X] T074 [US6] Wire routes in `skills/urls.py`: `path("skills/<int:pk>/edit/", SkillUpdateView.as_view(), name="update")` and `path("skills/<int:pk>/delete/", SkillDeleteView.as_view(), name="delete")`
- [X] T075 [US6] Run the US6 section of `quickstart.md` ("Smoke-test walkthrough → US6") and record PASS/FAIL

**Checkpoint**: All six user stories are independently functional. Feature scope is complete.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Constitution quality gates (admin coverage, teaching comments, optional invariant tests, end-to-end smoke walkthrough, viewport check).

- [X] T076 [P] Sweep `skills/models.py` and add or refine inline teaching comments per Principle V on each non-obvious construct: `on_delete=PROTECT` vs `CASCADE`, the `skill_free_xor_priced` `CheckConstraint`, the `unique_review_per_author_skill` `UniqueConstraint`, and the `clean()` methods (one to two short lines each, not multi-paragraph docstrings)
- [X] T077 [P] Sweep `skills/views.py` and add inline comments where `select_related` / `prefetch_related` is used and where `LoginRequiredMixin` / `OwnerOnlyMixin` are applied (one short line each)
- [X] T078 [P] Optional invariant test (research §R10 #1): create `skills/tests/__init__.py` and `skills/tests/test_skill_clean.py` covering `Skill.clean()` Free-vs-priced cases (free + price=None ✅, free + price=10 ✅ but price coerced to None, paid + price=None ❌, paid + negative price ❌, paid + price=10 ✅) using `django.test.TestCase`
- [X] T079 [P] Optional invariant test (research §R10 #2): `skills/tests/test_booking_invariants.py` covering self-booking rejection and `unavailable` skill rejection at create time
- [X] T080 [P] Optional invariant test (research §R10 #3): `skills/tests/test_review_invariants.py` covering `(author, skill)` uniqueness via `update_or_create`, and that submission without an `accepted` booking is rejected by `clean()`
- [X] T081 [P] Optional invariant test (research §R10 #4): `skills/tests/test_permissions.py` covering 403 for non-owner editing/deleting a skill, and 403 for non-author updating a review
- [X] T082 Run `python manage.py test` and confirm all optional tests pass (skip this task if T078–T081 are intentionally deferred)
- [X] T083 Verify the three-command setup from a clean checkout: `pip install -r requirements.txt`, `python manage.py migrate`, `python manage.py runserver` — record any deviation from `quickstart.md` "Setup (3-command path)"
- [ ] T084 [P] Verify each primary page (listings, detail, dashboard, login, register, create-skill) renders without overlap on a desktop viewport (≥ 1280 px) and a mobile viewport (≤ 414 px) per SC-007; capture screenshots or notes in the commit
- [X] T085 Run the full `quickstart.md` smoke-test walkthrough (US1 → US6) end-to-end on a freshly migrated database and capture PASS/FAIL with notes; this is the constitution's Quality Gate #3

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No prior dependencies — start immediately.
- **Phase 2 (Foundational)**: Requires Phase 1. **BLOCKS** every user-story phase.
- **Phase 3 (US1, P1)**: Requires Phase 2.
- **Phase 4 (US2, P1)**: Requires Phase 2. Independent of US1 in principle, but smoke-testing US2 is easier when US1's listing already works (the success of `Create skill` is verified by visiting the public listing). Sequential P1 → P1 ordering is recommended.
- **Phase 5 (US3, P2)**: Requires Phase 2 *and* the `Skill` model from Phase 3 (US1 introduces `Skill`); pragmatically US3 is built after US1.
- **Phase 6 (US4, P2)**: Requires Phase 2, plus the `Skill` model (US1) and authentication (US2) — both must exist before booking is meaningful.
- **Phase 7 (US5, P3)**: Requires Phase 2, the `Skill` model (US1), and the `BookingRequest` model with `accepted` status (US4); reviews are gated on accepted bookings.
- **Phase 8 (US6, P3)**: Requires Phase 2, the `Skill` model (US1), and authentication (US2). Independent of US3, US4, US5.
- **Phase 9 (Polish)**: After all targeted user stories are complete.

### Within Each User Story

- Models before migrations; migrations before any view/admin/form/template depending on them.
- Forms and views before URL wiring.
- URL wiring before the smoke-test task.
- Smoke-test task is always the last task in the phase.

### Parallel Opportunities

- **Phase 1**: T003, T004 in parallel (different app directories); T006, T007, T008, T009 in parallel after T005 (different files).
- **Phase 2**: T010, T011 in parallel (template vs. CSS).
- **Phase 3 (US1)**: After T018 (migration applied), T019, T020, T022 are parallel (admin vs. partials vs. detail template).
- **Phase 4 (US2)**: T027, T028, T029, T030 are parallel (form vs. three templates); T033, T034 are parallel; T036, T037 are parallel (view stub vs. template stub).
- **Phase 6 (US4)**: T047, T048, T049, T050 are parallel after T046 (admin vs. form vs. mixin vs. partial).
- **Phase 7 (US5)**: T060, T061, T062 are parallel after T059.
- **Phase 8 (US6)**: T068, T069, T070 are parallel.
- **Phase 9**: T076–T081 and T084 all parallel (different files / read-only viewport check).

---

## Parallel Example: User Story 1

```bash
# After T018 (migration applied), launch the three independent file-creation tasks together:
Task: "Register Skill in skills/admin.py"                                      # T019
Task: "Create skills/templates/skills/partials/_skill_card.html"               # T020
Task: "Create skills/templates/skills/skill_detail.html"                       # T022
```

## Parallel Example: User Story 4

```bash
# After T046 (BookingRequest migration applied), four independent files:
Task: "Register BookingRequest in skills/admin.py"                             # T047
Task: "Add BookingRequestForm to skills/forms.py"                              # T048
Task: "Create skills/permissions.py with OwnerOnlyMixin"                       # T049
Task: "Create skills/templates/skills/partials/_booking_row.html"              # T050
```

---

## Implementation Strategy

### MVP First (P1 only — User Stories 1 + 2)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational — Category model + seed + base template).
3. Complete Phase 3 (US1 — Browse and discover).
4. Complete Phase 4 (US2 — Register, sign in, post).
5. **STOP and VALIDATE**: Run quickstart §US1 and §US2. Demo / share.

This is the smallest runnable two-sided marketplace.

### Incremental Delivery (recommended)

1. MVP (above) → demo.
2. Add Phase 5 (US3 — Search) → demo.
3. Add Phase 6 (US4 — Booking) → demo.
4. Add Phase 7 (US5 — Reviews) → demo.
5. Add Phase 8 (US6 — Manage listings) → demo.
6. Run Phase 9 (Polish) → release-candidate.

Each step adds value without breaking previous stories; the constitution's smoke-test gate runs at the end of every step.

### Parallel Team Strategy

After Phase 2 completes:

- **Developer A**: Phase 3 (US1). Sets up the `Skill` model.
- **Developer B**: Phase 4 (US2) — but must rebase once `Skill` lands on `main` because `SkillForm` in T033 needs the model.
- **Developer C**: Wait until US1 is on `main`, then take Phase 5 (US3) and Phase 8 (US6) in sequence (both depend on US1's Skill model and views).
- **Developers**: After US2 lands, Phase 6 (US4) can start in parallel with Phase 5 (US3) since they touch separate models and templates.

For a solo learner (the most likely audience per the constitution's beginner-first principle), follow Incremental Delivery in strict P1 → P3 order.

---

## Notes

- `[P]` tasks = different files, no dependencies on incomplete tasks.
- `[Story]` label maps each task to its user story for traceability.
- Each user-story phase ends with a manual smoke-test task that fulfills constitution Quality Gate #3.
- Migrations are committed alongside the model edits that produce them (Quality Gate #2). Do **not** squash migrations during normal feature work.
- Admin registration is required for every user-owned model (Quality Gate #4) — do not skip the admin-registration task in any phase.
- Tests are OPTIONAL; the four invariant tests in Phase 9 are the highest-leverage targets per `research.md` §R10 and may be omitted if time-boxed.
- Avoid: vague tasks, two phases editing the same file simultaneously, and cross-story dependencies that break independence (none above).
