# URL Route Contract — Campus SkillSwap

This is the v1 contract between the URL space and the views that handle each
route. Because Campus SkillSwap is a server-rendered Django app, the contract
is expressed as a URL table rather than an OpenAPI/JSON schema.

Each row lists:

- **URL** — the URL pattern (Django path syntax).
- **Name** — the namespaced reverse name (used in templates and `redirect()`).
- **Methods** — HTTP methods accepted by the view.
- **Auth** — what authorization is required.
- **Inputs** — form fields or query parameters consumed.
- **Output** — the template rendered (for GET) or the redirect target
  (for POST), plus any messages set via `django.contrib.messages`.
- **Spec ref** — functional requirement(s) and user story this route serves.

All form views set a flash message on success or failure (per FR-029) and
re-render with field errors when validation fails. All routes that require
login redirect anonymous users to `LOGIN_URL` (`/accounts/login/`) with the
original path stored in `?next=`.

---

## URL conventions

- Project URLconf at `config/urls.py` includes:
  - `path("admin/", admin.site.urls)`
  - `path("accounts/", include("django.contrib.auth.urls"))` — supplies
    `login`, `logout`, `password_change`, etc.
  - `path("accounts/", include("accounts.urls"))` — adds `register`.
  - `path("", include("skills.urls"))` — everything else.
- App URL namespace: `app_name = "skills"` in `skills/urls.py`. Templates use
  `{% url "skills:list" %}`, etc.
- `<int:pk>` is used for object IDs. No slugs in v1.

---

## Routes

### Public — no authentication required

| URL | Name | Methods | Auth | Inputs | Output | Spec ref |
|-----|------|---------|------|--------|--------|----------|
| `/` | `skills:list` | GET | Anonymous OK | Query: `q` (string, optional), `category` (int, optional), `page` (int, optional) | `skills/skill_list.html` with paginated `Skill` queryset, current filter values, and category options. Empty state when no posts match. | FR-010, FR-012, FR-013, FR-014, FR-030 / US1, US3 |
| `/skills/<int:pk>/` | `skills:detail` | GET | Anonymous OK | Path: `pk` | `skills/skill_detail.html` with the `Skill`, its reviews, average rating, count, owner display name, and (for logged-in non-owners) a booking-request form. 404 when the pk doesn't exist. | FR-011, FR-022 / US1, US4, US5 |

### Authentication — Django built-ins + thin registration

| URL | Name | Methods | Auth | Inputs | Output | Spec ref |
|-----|------|---------|------|--------|--------|----------|
| `/accounts/login/` | `login` | GET, POST | Anonymous | Form: `username`, `password` | Renders `registration/login.html`. On POST success, redirects to `?next=` or `LOGIN_REDIRECT_URL` (`/dashboard/`). On failure, re-renders with errors. Sets success message on login. | FR-002 / US2 |
| `/accounts/logout/` | `logout` | POST | Authenticated | — | Logs out, redirects to `skills:list`, sets info message. | FR-002 / US2 |
| `/accounts/register/` | `accounts:register` | GET, POST | Anonymous | Form: `username`, `email` (required, unique), `password1`, `password2` | GET renders `registration/register.html`. POST creates `User`, logs them in, redirects to `dashboard`, sets success message. POST with errors re-renders the form. | FR-001, FR-003 / US2 |

### Skills — owner CRUD (login required + ownership for write)

| URL | Name | Methods | Auth | Inputs | Output | Spec ref |
|-----|------|---------|------|--------|--------|----------|
| `/skills/new/` | `skills:create` | GET, POST | Login required | Form: `title`, `description`, `category`, `is_free`, `price`, `contact_preference`, `availability` | GET renders `skills/skill_form.html` (blank). POST validates via `SkillForm.clean()`, sets `owner=request.user`, saves, redirects to `skills:detail` with success message. POST with errors re-renders. | FR-005, FR-009, FR-029 / US2 |
| `/skills/<int:pk>/edit/` | `skills:update` | GET, POST | Login required + owner only | Path: `pk`; Form: same as create | GET renders pre-filled form. POST updates and redirects to `skills:detail` with success message. Non-owner gets 403. | FR-006, FR-008, FR-009, FR-029 / US6 |
| `/skills/<int:pk>/delete/` | `skills:delete` | GET, POST | Login required + owner only | Path: `pk` | GET renders `skills/skill_confirm_delete.html`. POST deletes and redirects to `skills:list` with success message. Non-owner gets 403. | FR-007, FR-008, FR-029 / US6 |

### Booking requests

| URL | Name | Methods | Auth | Inputs | Output | Spec ref |
|-----|------|---------|------|--------|--------|----------|
| `/skills/<int:pk>/request/` | `skills:request_booking` | POST | Login required + non-owner + skill `available` | Path: `pk`; Form: `message`, `proposed_time` | Creates `BookingRequest(status=PENDING, requester=request.user, skill=skill)`, redirects to `skills:detail` with success message. 403 if user is the owner; refuses (with error message + redirect) if skill is `unavailable`. | FR-015, FR-016, FR-019, FR-020, FR-029 / US4 |
| `/requests/<int:pk>/respond/` | `skills:respond_request` | POST | Login required + skill owner | Path: `pk`; Form: `action` ∈ {`accept`, `decline`} | Updates the `BookingRequest.status` accordingly, redirects to `dashboard` with success message. 403 if requester is not the skill owner. | FR-017, FR-018, FR-029 / US4 |

### Reviews

| URL | Name | Methods | Auth | Inputs | Output | Spec ref |
|-----|------|---------|------|--------|--------|----------|
| `/skills/<int:pk>/review/` | `skills:submit_review` | POST | Login required + non-owner + has accepted booking on this skill | Path: `pk`; Form: `rating` (int 1–5), `text` | `update_or_create` review for `(author=request.user, skill=skill)`, redirect to `skills:detail` with success message. Errors re-render the detail page with the review form open and field errors. 403 if user is the owner; error message if no accepted booking exists. | FR-021, FR-022, FR-023, FR-024, FR-029 / US5 |

### Dashboard

| URL | Name | Methods | Auth | Inputs | Output | Spec ref |
|-----|------|---------|------|--------|--------|----------|
| `/dashboard/` | `skills:dashboard` | GET | Login required | — | `skills/dashboard.html` with three sections: my skill posts (with edit/delete links), requests I have sent (with status), requests I have received (with accept/decline buttons for `pending`). Empty-state copy when any section is empty. | FR-018, FR-025, FR-026, FR-030 / US4, US6 |

### Admin

| URL | Name | Methods | Auth | Output | Spec ref |
|-----|------|---------|------|--------|----------|
| `/admin/...` | `admin:*` (Django default) | GET, POST | `is_staff=True` | Standard Django admin. `Category`, `Skill`, `BookingRequest`, `Review` are registered (FR-027, FR-028). | FR-027, FR-028 |

---

## HTTP-status conventions

- `200 OK` — successful render of a GET.
- `302 Found` — successful POST that redirects (Post/Redirect/Get pattern).
- `403 Forbidden` — authenticated user attempts an action that requires
  ownership or staff (e.g., editing someone else's skill).
- `404 Not Found` — `pk` does not exist or filter excludes the object (e.g.,
  retired-but-not-deleted category in a future version).
- Anonymous user hitting a login-required route → `302` to
  `/accounts/login/?next=<original>`.

There is no `4xx`/`5xx` JSON envelope — this is HTML-only. Errors render
through Django's standard `403.html`, `404.html`, and `500.html`.

---

## Form contracts (summary)

These are the field sets the views accept. Field-level validation rules are
documented in `data-model.md`.

### `RegisterForm` (in `accounts/forms.py`)

Subclasses `django.contrib.auth.forms.UserCreationForm`. Adds:

- `email` — `EmailField(required=True)` with a uniqueness check in
  `clean_email()`.

### `SkillForm` (in `skills/forms.py`)

Django `ModelForm` for `Skill`. Fields exposed:

- `title`, `description`, `category`, `is_free`, `price`, `contact_preference`,
  `availability`.

The form's `clean()` enforces the Free/priced rule (research §R6) and
returns a friendly error message for the `price` field.

The `category` field's queryset is filtered to `is_active=True` so retired
categories don't appear in the dropdown.

### `BookingRequestForm` (in `skills/forms.py`)

Django `ModelForm` for `BookingRequest`. Fields exposed:

- `message`, `proposed_time`.

The view (not the form) sets `requester` and `skill`, runs `clean()` (which
enforces the self-booking and unavailable-skill rules), and saves.

### `ReviewForm` (in `skills/forms.py`)

Django `ModelForm` for `Review`. Fields exposed:

- `rating` (radio or numeric input 1–5), `text`.

The view sets `author` and `skill`, performs `update_or_create` to honor
FR-024, and runs the "accepted booking exists" check before save.

---

## Settings keys this contract relies on

To make the routes behave as described, `config/settings.py` MUST set:

- `LOGIN_URL = "login"` — Django default; explicit for clarity.
- `LOGIN_REDIRECT_URL = "skills:dashboard"` — where login goes when no `?next=`.
- `LOGOUT_REDIRECT_URL = "skills:list"` — public listing after logout.
- `MESSAGE_TAGS = {messages.DEBUG: "secondary", messages.INFO: "info",
  messages.SUCCESS: "success", messages.WARNING: "warning",
  messages.ERROR: "danger"}` — maps Django message levels to Bootstrap 5
  alert classes so flash messages render correctly without per-template
  conditionals.
