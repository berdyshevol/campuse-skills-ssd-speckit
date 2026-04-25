# Phase 0 Research — Campus SkillSwap

This document resolves the open questions and technology choices needed before
Phase 1 design can proceed. Each entry follows the pattern **Decision /
Rationale / Alternatives considered**.

---

## R1. Frontend stack: Bootstrap 5 templates vs. Next.js + Tailwind

**Decision**: Server-rendered Django templates with **Bootstrap 5** loaded from a
CDN, using `{% extends %}` / `{% block %}` template inheritance. **No SPA, no
JavaScript build step.** The spec's Assumptions paragraph that references
"Next.js with Tailwind" is overridden by this decision and should be updated
to read "Bootstrap 5 + server-rendered Django templates" the next time the
spec is touched.

**Rationale**:

- Constitution v1.0.0 Principle II ("Idiomatic Django, No Detours")
  *explicitly forbids* SPA frontends unless the plan documents a justified
  Complexity Tracking entry. There is no spec requirement that depends on
  client-side state, real-time interactivity, or anything else only an SPA
  can provide.
- Constitution v1.0.0 Technology Stack Constraints fix Bootstrap 5 +
  Django templates as the frontend stack and require a constitution amendment
  to change them.
- The original `project_brief/brief.md` lists "Bootstrap templates with
  template inheritance" as a hard requirement.
- Resolving the conflict in favor of the constitution avoids an amendment and
  matches the brief, so the change is the lower-risk path.
- Bootstrap 5 via CDN means zero build pipeline, which preserves the
  three-command setup and the Beginner-First Pedagogy principle.

**Alternatives considered**:

- *Next.js + Tailwind, Django REST Framework backend.* Rejected: violates
  Principles II and III (would require DRF, a separate frontend project, a
  build pipeline, and a token-auth scheme). Adds three concept stacks the
  learner does not need to study Django.
- *HTMX progressive enhancement on top of Django templates.* Rejected for v1:
  no spec requirement currently needs it. Could be added as an enhancement
  later without violating the constitution.
- *Django templates + Tailwind via the Tailwind CLI.* Rejected: introduces a
  Node toolchain (build step) that the constitution disallows ("no build step
  beyond `collectstatic`").

---

## R2. Django version

**Decision**: Django **5.2 LTS** (released April 2025; supported until April
2028). Pinned in `requirements.txt` as `django>=5.2,<5.3`.

**Rationale**:

- The constitution requires "the latest LTS available at the time of feature
  work". As of 2026-04-25, Django 5.2 LTS is the latest LTS line.
- Long-term support guarantees three years of security patches, which exceeds
  the project's lifetime.
- 5.2 includes mature `CheckConstraint` / `UniqueConstraint` support, which we
  rely on for the `Review` (author, skill) uniqueness constraint and the
  `BookingRequest` status `CharField` choices.

**Alternatives considered**:

- *Django 4.2 LTS.* Older LTS line; rejected because 5.2 is available and the
  constitution prefers the *latest* LTS.
- *Django 5.1.* Not an LTS release. Rejected for security-window reasons.

---

## R3. Authentication — User model and registration

**Decision**: Use Django's built-in `auth.User` model unchanged. Login and
logout reuse `django.contrib.auth.views.LoginView` and `LogoutView` directly.
Registration is implemented as a thin `accounts` app that subclasses
`UserCreationForm` to add a required, unique `email` field (the form does not
swap `USERNAME_FIELD`).

**Rationale**:

- Constitution Principle II forbids third-party auth backends and rewriting
  what `django.contrib.auth` already provides.
- A custom `User` model is a documented Django footgun for beginners (the
  warning is explicit in the Django docs: swap it on day one or never). Since
  the spec's needs (email, display name) are met by the stock `User` model
  plus a unique email, swapping is unnecessary.
- `UserCreationForm` is the canonical beginner pattern. Subclassing to add an
  email field is the smallest possible change and is a teaching opportunity
  (one inline comment explains the override).

**Alternatives considered**:

- *Custom `User` model with `email` as `USERNAME_FIELD`.* Rejected: large
  blast radius (admin, password reset, fixtures all need adjustment) for a
  v1-cosmetic benefit. The username field is exposed alongside email on the
  form; users may pick whatever they like.
- *`django-allauth` or `django-registration`.* Rejected: third-party
  dependency forbidden by Principle II without justification.

**Operational note**: `LOGIN_URL = 'login'` and `LOGIN_REDIRECT_URL = 'dashboard'`
are set in `settings.py`. The `accounts/templates/registration/login.html`
path is the convention `LoginView` looks for, so no view override is needed.

---

## R4. Search — keyword + category filter

**Decision**: Implement search using a single Django ORM query that combines
`Skill.objects.filter(title__icontains=q)` (when `q` is provided) and
`category=<id>` (when a category filter is set). Results are paginated with
Django's `Paginator` (page size 12). Empty `q` and missing category both
default to "no constraint."

**Rationale**:

- Spec FR-012 only requires *case-insensitive substring match against
  title* and an exact category filter. SQLite's `LIKE` (which `icontains`
  compiles to) is sufficient at the project's scale (low thousands of rows).
- No full-text engine is needed; introducing one (Postgres + `SearchVector`,
  Meilisearch, etc.) would violate Principles II and III.
- The implementation is two lines of view code plus a small form, which makes
  it an excellent teaching example of Django's queryset chaining.

**Alternatives considered**:

- *Postgres full-text search (`SearchVector`).* Rejected: contradicts the
  SQLite constraint and is unnecessary at this scale.
- *Client-side filtering of the entire list.* Rejected: requires loading all
  posts into the page, breaks pagination, fails when the catalogue grows
  beyond a few dozen entries.
- *Search across `description` as well as `title`.* Rejected for v1: the
  spec is explicit that the keyword search applies to title only (FR-012).
  Easy to extend later by changing one filter clause.

---

## R5. Categories — seeding and lifecycle

**Decision**: `Category` is a model with `name` (unique), `slug` (unique),
optional `description`, and an `is_active` boolean. An initial set of
categories is created via a **data migration** (`0002_seed_categories.py`)
shipped with the codebase so a fresh `migrate` produces a usable database.
Admins can add, edit, or *retire* (set `is_active=False`) categories from
`/admin/`. Retiring instead of deleting preserves the FK from `Skill`.

**Rationale**:

- Spec FR-028 requires a curated, admin-managed list. Hard-coding categories
  as a `TextChoices` enum would lock the list to deploy time and violate
  FR-028's "admin can add, edit, or retire" requirement.
- A data migration is Django-idiomatic for "seed data that must exist after a
  fresh setup." It also serves as a teaching example of `RunPython` /
  `migrations.RunPython`.
- `is_active=False` instead of physical delete prevents foreign-key cascades
  from wiping out historical skill posts when an admin tidies the taxonomy.
  The `Skill.category` FK uses `on_delete=PROTECT` for the same reason.

**Initial seed list** (a reasonable starting taxonomy; admins can edit):

1. Tutoring — Math
2. Tutoring — Science
3. Tutoring — Humanities
4. Languages
5. Programming & Tech
6. Music
7. Art & Design
8. Sports & Fitness
9. Cooking
10. Other

**Alternatives considered**:

- *Hard-coded `TextChoices`.* Rejected: violates FR-028 (admin manageability).
- *Auto-create categories on the fly when a user types one in.* Rejected:
  spec edge case explicitly forbids it ("users cannot create arbitrary new
  ones").

---

## R6. Skill validation — Free vs. priced posts

**Decision**: `Skill` has a boolean `is_free` and a nullable `price`
(`DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)`).
Validation in `Skill.clean()`:

- If `is_free is True` → `price` is forced to `None` on save.
- If `is_free is False` → `price` MUST be present and `>= 0`; otherwise raise
  `ValidationError`.

A `CheckConstraint` on the model mirrors the rule at the database level:
`(is_free=True AND price IS NULL) OR (is_free=False AND price IS NOT NULL AND
price >= 0)`.

**Rationale**:

- Edge-cases section of the spec requires this exact invariant ("a post is
  either Free or has a price ≥ 0; the owner cannot leave both unset or set a
  negative price").
- Doubling up form-level validation (`clean()`) and database-level
  (`CheckConstraint`) is good Django practice and a teaching opportunity:
  the form gives the friendly error, the constraint stops bad data getting in
  via the admin or shell.

**Alternatives considered**:

- *Single `price` field with `0` meaning Free.* Rejected: `0` is a valid
  paid price (free trial, donation-based) in some cultures, and a separate
  flag is clearer in the UI.
- *Form-only validation, no constraint.* Rejected: admins editing in
  `/admin/` could bypass the rule.

---

## R7. Booking-request lifecycle and self-action prevention

**Decision**: `BookingRequest.status` is a `CharField` with
`TextChoices` (`PENDING`, `ACCEPTED`, `DECLINED`), defaulting to `PENDING`.
Allowed transitions:

- `PENDING → ACCEPTED` (owner action)
- `PENDING → DECLINED` (owner action)
- No transitions out of `ACCEPTED` or `DECLINED` for v1.

Self-action prevention is enforced in three places:

1. `BookingRequest.clean()` raises `ValidationError` when `requester ==
   skill.owner`.
2. The view that handles `POST /skills/<pk>/request/` returns 403 if the
   logged-in user is the owner (defensive, in case the form is bypassed).
3. The skill detail template hides the "Request a Session" form when
   `request.user == skill.owner`.

A new request is also rejected if `skill.availability == 'unavailable'`
(spec FR-020).

**Rationale**:

- Three-state status machine is the simplest model that satisfies FR-016 and
  US4. No state-machine library is required.
- Defense in depth (clean() + view + template) catches the same beginner
  mistake from three angles, which is a teaching point.

**Alternatives considered**:

- *Adding a `CANCELLED` status that the requester can set.* Rejected for v1:
  no spec requirement.
- *`django-fsm` or another state-machine library.* Rejected: violates
  Principle II and is overkill for three states.

---

## R8. Review uniqueness and update semantics

**Decision**: `Review` has a `UniqueConstraint(fields=['author', 'skill'],
name='unique_review_per_author_skill')`. The view that handles review
submission uses `Review.objects.update_or_create(author=..., skill=...,
defaults={...})` so a second submission updates the existing row rather than
raising `IntegrityError`.

The view also enforces:

- The author is not the skill owner (FR-023).
- The author has at least one `BookingRequest` with `status='accepted'` for
  this skill (FR-021, FR-024).

**Rationale**:

- FR-024 explicitly says "subsequent submissions update their existing
  review." `update_or_create` is the canonical Django pattern for that.
- The DB-level unique constraint stops races and admin-side mistakes.

**Alternatives considered**:

- *Allow multiple reviews per (user, skill) pair.* Rejected: contradicts
  spec FR-024.
- *Soft-delete old review and create new one.* Rejected: more state for no
  benefit.

---

## R9. Permissions — owner-only edit/delete and dashboard scoping

**Decision**: Use Django's `LoginRequiredMixin` for any view that requires
authentication. Owner-only views (skill edit, skill delete, request
respond) use a small `OwnerOnlyMixin` that overrides `dispatch` to
return 403 unless `request.user == self.get_object().owner` (or
`self.get_object().skill.owner` for `BookingRequest` respond). The dashboard
view filters by `request.user` for both "my posts" and "my requests."

**Rationale**:

- `LoginRequiredMixin` is the canonical Django pattern. `UserPassesTestMixin`
  could replace `OwnerOnlyMixin`, but `OwnerOnlyMixin` reads more clearly in
  the `views.py` and lives in 10 lines.
- Filtering the dashboard by `request.user` is straightforward and safer than
  trusting URL parameters.

**Alternatives considered**:

- *`django-guardian` per-object permissions.* Rejected: violates Principle II
  and is dramatically heavier than the requirement.
- *Pure `UserPassesTestMixin` everywhere.* Rejected: equally valid but the
  named mixin documents intent better.

---

## R10. Tests — what to write, what to skip

**Decision**: Per the constitution, tests are OPTIONAL. We will add a small
suite (`tests/` per app, using `django.test.TestCase`) for the four
invariants that are easy to break and hard to spot:

1. `Skill.clean()` — Free vs. priced rule.
2. `BookingRequest` — self-booking is rejected; new requests on
   `unavailable` skills are rejected.
3. `Review` — uniqueness per (author, skill); only allowed when an accepted
   booking exists.
4. Permissions — non-owner cannot edit/delete a skill; non-author cannot edit
   a review.

We will NOT write tests for: template rendering, list/detail views with
trivial logic, Django's own auth machinery, admin pages.

**Rationale**:

- Tests on fragile invariants give the highest learning return per line.
- Testing trivial views duplicates Django's own test coverage.

**Alternatives considered**:

- *No tests at all.* Allowed by the constitution but rejected because the
  invariants above are exactly the kind of thing a beginner refactors and
  silently breaks.
- *Full test pyramid.* Rejected: violates Principle III for a project of
  this size.

---

## R11. URL conventions

**Decision**: Follow Django's idiomatic URL style:

- App-prefixed `name=` values (`skills:list`, `skills:detail`, `skills:create`,
  etc.) so templates and `redirect()` calls reference views symbolically.
- `<int:pk>` for object IDs (no slugs) — simpler for v1, consistent with
  `auto_now_add` IDs. Slugs can be added later without breaking history.
- Booking and review actions are nested under the parent skill (e.g.,
  `/skills/12/request/`, `/skills/12/review/`) to match REST-ish reading.

**Rationale**:

- Namespaced URLs are a constitution-friendly best practice that prevents
  cross-app collisions and is taught in every Django tutorial.
- Integer pks keep the URL contract dead-simple for the first iteration.

**Alternatives considered**:

- *Slug-based URLs.* Deferred: nice-to-have, not in spec.
- *Flat URL space (no skill nesting).* Rejected: harder to teach and read.

---

## Resolved status

All `NEEDS CLARIFICATION` markers from Technical Context are now resolved.
The plan is ready for Phase 1 (data model, contracts, quickstart).
