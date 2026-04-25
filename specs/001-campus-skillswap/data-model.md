# Phase 1 Data Model — Campus SkillSwap

This document defines the persistent entities for v1, their fields,
relationships, validation rules, and state transitions. Field types are
expressed as Django ORM field classes (`django.db.models.*`). All models
will live in `skills/models.py` for v1.

A short legend used below:

- **PK** — primary key (Django adds `id` automatically; not repeated in field
  tables).
- **FK → X** — `ForeignKey(X, on_delete=...)`.
- **`null/blank`** — `null=` controls the database column; `blank=`
  controls form validation. Defaults are `False` unless noted.

---

## Entity overview

| Entity | Purpose | Owns | Owned by / referenced by |
|--------|---------|------|--------------------------|
| `User` (Django built-in `auth.User`) | A registered student account. | Skills, BookingRequests sent, Reviews written. | — |
| `Category` | Admin-managed taxonomy entry. | Skills (logically). | Admin. |
| `Skill` | A listing offered by a User. | BookingRequests, Reviews. | `owner` (User), `category` (Category). |
| `BookingRequest` | A request from one User to engage a Skill owned by another User. | — | `requester` (User), `skill` (Skill). |
| `Review` | A 1–5 star rating + text written by a User on a Skill. | — | `author` (User), `skill` (Skill). |

Relationship diagram (textual):

```text
auth.User ──────────┬──── (1, *) ──── Skill ──── (*, 1) ──── Category
                    │                  │
                    │                  ├──── (1, *) ──── BookingRequest ──── (*, 1) ──── auth.User (requester)
                    │                  │
                    │                  └──── (1, *) ──── Review ──── (*, 1) ──── auth.User (author)
                    │
                    └──── (1, *) ──── BookingRequest (requester)
                    └──── (1, *) ──── Review (author)
```

---

## 1. `User` — Django's `auth.User` (used as-is)

We do NOT define a custom `User` model. We use `django.contrib.auth.models.User`
unchanged. Fields used by the application:

| Field | Type | Notes |
|-------|------|-------|
| `username` | CharField (Django default, max 150) | Required by Django. Shown as the public display name on listings, detail pages, and reviews. |
| `email` | EmailField | Required and unique in our registration form (the stock model marks it optional; the form override fixes this). |
| `password` | (managed by `set_password`) | Hashed by Django. Never stored in plain text. |
| `date_joined` | DateTimeField | Auto-populated by Django. |

**Why no custom user model?** See `research.md` §R3. The cost of swapping
`auth.User` mid-project is high; the spec's needs (email + display name) are
met by the default.

**Display-name policy**: templates show `user.username`. If the user supplies
a `first_name` or `last_name` later (we do not collect it on register), those
can be surfaced as a separate enhancement.

---

## 2. `Category`

| Field | Type | Notes |
|-------|------|-------|
| `name` | `CharField(max_length=80, unique=True)` | The human-readable taxonomy label, e.g. `"Tutoring — Math"`. |
| `slug` | `SlugField(max_length=80, unique=True)` | URL-safe, used in admin and (optionally) future filter URLs. |
| `description` | `TextField(blank=True)` | Optional admin-facing hint for the meaning of the category. |
| `is_active` | `BooleanField(default=True)` | When `False`, the category is hidden from listing-page filter dropdowns and from the create/edit form. Existing skills that point to a retired category continue to display the category name. |

**Meta**:

```python
class Meta:
    ordering = ["name"]
    verbose_name_plural = "categories"
```

**`__str__`**: `return self.name`

**Validation rules**:

- `name` and `slug` must be unique (`unique=True`).
- The category cannot be deleted if any `Skill` references it — enforced by
  `Skill.category` using `on_delete=PROTECT`. To remove a category, an admin
  reassigns or deletes the dependent skills first, *or* sets `is_active=False`
  to retire it instead (preferred path).

**Seeded via data migration** (`0002_seed_categories.py`); see `research.md`
§R5 for the initial list.

---

## 3. `Skill`

| Field | Type | Notes |
|-------|------|-------|
| `title` | `CharField(max_length=120)` | Spec edge case caps at 120 chars. |
| `description` | `TextField(max_length=4000)` | Spec edge case caps at 4000 chars. |
| `category` | `FK → Category, on_delete=PROTECT, related_name="skills"` | `PROTECT` because losing a category would orphan posts; admins must retire instead. |
| `is_free` | `BooleanField(default=False)` | When `True`, `price` MUST be `None`. |
| `price` | `DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(Decimal("0.00"))])` | Required when `is_free=False`; max value 999_999.99 (well above realistic). |
| `contact_preference` | `CharField(max_length=16, choices=ContactPreference.choices)` | Choices: `EMAIL` (`"email"`), `IN_APP` (`"in_app"`), `PHONE` (`"phone"`). The `IN_APP` option is informational for v1 (no in-app messaging yet). |
| `availability` | `CharField(max_length=16, choices=Availability.choices, default=Availability.AVAILABLE)` | Choices: `AVAILABLE` (`"available"`), `UNAVAILABLE` (`"unavailable"`). Controls whether new booking requests are accepted. |
| `owner` | `FK → auth.User, on_delete=CASCADE, related_name="skills"` | When a user is deleted, their skills go with them. v1 has no account-deletion UI, so this only matters for admin operations. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Set once on insert. |
| `updated_at` | `DateTimeField(auto_now=True)` | Refreshed on every save. |

**Choices classes** (defined as nested `TextChoices` for self-documentation):

```python
class ContactPreference(models.TextChoices):
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In-app message"
    PHONE = "phone", "Phone"

class Availability(models.TextChoices):
    AVAILABLE = "available", "Available"
    UNAVAILABLE = "unavailable", "Unavailable"
```

**Meta**:

```python
class Meta:
    ordering = ["-created_at"]               # FR-014: newest first by default
    constraints = [
        models.CheckConstraint(
            name="skill_free_xor_priced",
            check=(
                models.Q(is_free=True, price__isnull=True)
                | models.Q(is_free=False, price__isnull=False, price__gte=0)
            ),
        ),
    ]
```

**`__str__`**: `return self.title`

**Validation rules** (`clean()` raises `ValidationError`):

- If `is_free is True` → `price` is set to `None` before save.
- If `is_free is False` → `price` MUST be present and `>= 0`.
- The `CheckConstraint` mirrors the same invariant at the DB level so
  admin/shell operations cannot bypass the form.

**Computed properties / methods** (light, only what views actually need):

- `display_price` → returns `"Free"` if `is_free` else `f"${price:,.2f}"`.
- `can_be_booked_by(user)` → returns `True` if `user.is_authenticated` AND
  `user != self.owner` AND `self.availability == Availability.AVAILABLE`.

**State transitions**: `availability` may flip `AVAILABLE ↔ UNAVAILABLE` at
any time by the owner. No other state on this model.

---

## 4. `BookingRequest`

| Field | Type | Notes |
|-------|------|-------|
| `requester` | `FK → auth.User, on_delete=CASCADE, related_name="requests_made"` | The student asking for the session. |
| `skill` | `FK → Skill, on_delete=CASCADE, related_name="requests"` | The skill being requested. |
| `message` | `TextField(max_length=2000)` | Free text from the requester. |
| `proposed_time` | `DateTimeField()` | A proposed start time; not enforced as a calendar slot. |
| `status` | `CharField(max_length=10, choices=Status.choices, default=Status.PENDING)` | See state transitions below. |
| `created_at` | `DateTimeField(auto_now_add=True)` | |
| `updated_at` | `DateTimeField(auto_now=True)` | Refreshed when status changes. |

**Choices class**:

```python
class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
```

**Meta**:

```python
class Meta:
    ordering = ["-created_at"]
    constraints = [
        models.CheckConstraint(
            name="bookingrequest_status_valid",
            check=models.Q(status__in=["pending", "accepted", "declined"]),
        ),
    ]
```

**`__str__`**: `return f"{self.requester} → {self.skill} ({self.status})"`

**Validation rules** (`clean()` raises `ValidationError`):

- `requester != skill.owner` (FR-019, US4 acceptance scenario 4).
- On *creation only* (i.e., `self._state.adding is True`), reject if
  `skill.availability != "available"` (FR-020).

**Permission rules** (enforced in views):

- Only the `skill.owner` may move a request from `PENDING` to `ACCEPTED` or
  `DECLINED`.
- Both `requester` and `skill.owner` may *view* the request on their
  dashboards.

**State transitions**:

```text
PENDING ─────accept─────▶ ACCEPTED   (terminal in v1)
   │
   └────decline────▶ DECLINED        (terminal in v1)
```

There are no transitions out of `ACCEPTED` or `DECLINED` in v1; admins can
manually edit via `/admin/` if necessary.

---

## 5. `Review`

| Field | Type | Notes |
|-------|------|-------|
| `author` | `FK → auth.User, on_delete=CASCADE, related_name="reviews_written"` | The reviewer. |
| `skill` | `FK → Skill, on_delete=CASCADE, related_name="reviews"` | The reviewed skill. |
| `rating` | `PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])` | Integer 1–5. |
| `text` | `TextField(max_length=2000)` | Free-text review. |
| `created_at` | `DateTimeField(auto_now_add=True)` | Set on insert; preserved across `update_or_create`. |
| `updated_at` | `DateTimeField(auto_now=True)` | Refreshed when the user resubmits (FR-024). |

**Meta**:

```python
class Meta:
    ordering = ["-created_at"]
    constraints = [
        models.UniqueConstraint(
            fields=["author", "skill"],
            name="unique_review_per_author_skill",
        ),
        models.CheckConstraint(
            name="review_rating_range",
            check=models.Q(rating__gte=1, rating__lte=5),
        ),
    ]
```

**`__str__`**: `return f"{self.author} on {self.skill}: {self.rating}★"`

**Validation rules** (`clean()` raises `ValidationError`):

- `author != skill.owner` (FR-023).
- `BookingRequest.objects.filter(requester=author, skill=skill,
  status="accepted").exists()` MUST be true (FR-021, FR-024).

**Submit semantics** (in the view):

- The view uses `Review.objects.update_or_create(author=request.user,
  skill=skill, defaults={"rating": ..., "text": ...})` so a second submission
  by the same user updates rather than duplicates (FR-024).

**Aggregate display**:

- The skill detail view computes `Review.objects.filter(skill=skill)
  .aggregate(avg=Avg("rating"), count=Count("id"))` and renders
  `avg` rounded to one decimal alongside `count` (FR-022).

---

## Index considerations

For the v1 scale (low thousands of rows, SQLite), Django's default indexes
(primary key, FK indexes, `unique=True` on `Category.name` and
`Category.slug`) are sufficient. Two additional explicit indexes are added
because they support the only non-trivial query patterns:

| Model | Index | Justification |
|-------|-------|---------------|
| `Skill` | `Index(fields=["category"])` (already created by FK) — no extra needed. | Filter-by-category on listings page. |
| `Skill` | `Index(fields=["-created_at"])` | Default ordering on listings page (FR-014). |
| `BookingRequest` | `Index(fields=["requester", "status"])` | Dashboard "my requests" query. |
| `BookingRequest` | `Index(fields=["skill", "status"])` | Dashboard "received requests" query and the "did this user have an accepted booking?" check used by Review validation. |

These are added in the same `0001_initial.py` migration as the model
definitions.

---

## Migrations plan

| Migration | What it does |
|-----------|--------------|
| `0001_initial.py` | Creates `Category`, `Skill`, `BookingRequest`, `Review` plus their indexes and constraints. |
| `0002_seed_categories.py` | `RunPython` data migration that inserts the 10 default categories (research §R5). Idempotent: uses `Category.objects.get_or_create(name=...)`. |

No further migrations are anticipated for v1 unless the spec changes.

---

## Out of scope for v1

The following are intentionally NOT modeled in v1 (consistent with spec
Assumptions § "Out of scope for v1"):

- In-app messaging threads or chat history.
- Payment records / transaction logs.
- Notifications (email or in-app).
- Account deletion / GDPR data export.
- Image uploads (no `ImageField` anywhere in v1).
- Calendar/availability slots (the `proposed_time` is informational).

If any of these are added later, they would be new models (or new apps) and
would not require restructuring the entities defined above.
