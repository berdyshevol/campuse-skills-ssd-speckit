# Quickstart — Campus SkillSwap (developer setup)

This is the manual you'll follow to get a fresh checkout of the project
running on your laptop and to walk through every user story slice in the
browser. It also serves as the **smoke-test script** referenced by the
constitution's quality gates: the implementer must run through the
"Smoke-test walkthrough" section below at the end of every feature slice
and record the result in the commit/PR.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.11 or newer | Verify with `python3 --version`. |
| pip | bundled with Python | — |
| `venv` module | bundled with Python | We use stdlib `venv`, no Conda or Poetry. |
| A modern browser | Chrome, Firefox, Safari, or Edge — current version | For viewing pages. |
| (optional) `git` | any recent | Only needed for committing your work. |

You do **not** need: Node.js, Docker, Postgres, npm, Tailwind, or DRF.

---

## Setup (3-command path)

From the repository root:

```bash
# 1. Create and activate a virtual environment.
python3 -m venv .venv
source .venv/bin/activate            # on Windows: .venv\Scripts\activate

# 2. Install Django (and any other listed dependencies).
pip install -r requirements.txt

# 3. Apply migrations (creates db.sqlite3 and seeds default categories).
python manage.py migrate
```

Then create an admin login and start the server:

```bash
python manage.py createsuperuser     # follow the prompts
python manage.py runserver           # serves http://127.0.0.1:8000/
```

Open http://127.0.0.1:8000/ in your browser. You should see the public skill
listing page (empty state on a fresh database).

---

## What `migrate` produced

After step 3 you should have:

- `db.sqlite3` — a single-file SQLite database in the repo root (gitignored).
- 10 seeded `Category` rows (visible at http://127.0.0.1:8000/admin/ → Categories
  after creating the superuser). The list comes from the data migration
  documented in `research.md` §R5.
- All Django auth tables (`auth_user`, sessions, etc.) created by
  `django.contrib.auth` and `django.contrib.sessions`.

---

## Smoke-test walkthrough

Run through these steps after every user-story slice is implemented, in the
order the slices were built. Each step is independently verifiable, in line
with the constitution's "Incremental Vertical Slices" principle. Record the
result (`PASS` / `FAIL` + notes) in the commit or PR description for that
slice.

You will need at least two browser sessions to exercise the multi-user flows
(use a regular window + an incognito/private window, or two browsers).

### US1 — Browse and discover (public, no login)

1. From the admin, create one `Skill` post (assign it to your superuser as
   `owner`, pick any active category, fill in a price or mark it Free).
2. Open http://127.0.0.1:8000/ in a private window (logged out).
3. **Expect**: the listing page shows the skill card with title, category,
   price (or "Free"), and availability.
4. Click the skill card.
5. **Expect**: the detail page shows the full description, owner display
   name, contact preference, price, category, and availability. There is no
   "Request a Session" button (you are anonymous).
6. Delete the skill via admin and reload the listings page.
7. **Expect**: a friendly empty-state message inviting registration.

### US2 — Register, sign in, post a skill

1. From the public listings, click "Register".
2. Submit the form with a valid email, username, and password.
3. **Expect**: you are auto-logged-in, redirected to the dashboard, and see
   a success flash message.
4. Click "Create skill", fill in all fields with valid values, submit.
5. **Expect**: redirected to the new skill's detail page; success flash;
   the skill appears in `/` (listings) and on `/dashboard/`.
6. Submit a second skill but leave `title` blank.
7. **Expect**: form re-renders with a field-level error; no skill is saved.
8. Click "Logout".
9. **Expect**: redirected to the public listings; info flash; the dashboard
   link is gone.
10. Log in again with the same credentials.
11. **Expect**: dashboard reappears, your previously created skill is listed.

### US3 — Search by title or category

1. As a logged-in user, create three or more skills across at least two
   different categories (or seed via admin).
2. On `/`, type a keyword that matches some titles, submit.
3. **Expect**: only matching titles are displayed; the keyword input retains
   its value; clearing it restores the full list.
4. Pick a category from the filter dropdown; submit.
5. **Expect**: only skills in that category are shown; combining keyword +
   category narrows further.
6. Search for a string that matches nothing.
7. **Expect**: "no skills match your search" empty state with a "clear
   filters" link.

### US4 — Booking request lifecycle

You need two accounts: **Owner** (created in US2) and **Requester** (a new
account). Use two browser sessions.

1. As **Requester**, open a skill owned by **Owner** and submit a booking
   request with a message and proposed time.
2. **Expect**: success flash; the request appears in the Requester's
   dashboard with status `pending`.
3. As **Owner**, open the dashboard.
4. **Expect**: the new request appears under "received requests" with
   `accept` and `decline` buttons.
5. Click "accept".
6. **Expect**: status changes to `accepted` on the Owner's dashboard.
7. Refresh the Requester's dashboard.
8. **Expect**: same request now shows status `accepted`.
9. As **Requester**, log out and try to submit a booking request from the
   detail page.
10. **Expect**: redirected to login with `?next=` set.
11. As **Owner**, view your own skill's detail page.
12. **Expect**: the "Request a Session" form is hidden.
13. Mark the skill `unavailable` (edit it). As Requester, attempt another
    booking request on the same skill.
14. **Expect**: the request is rejected with an error flash.

### US5 — Rate and review

Continuing with **Owner** and **Requester** from US4, where Requester has
an `accepted` booking on Owner's skill.

1. As **Requester**, open the skill's detail page.
2. **Expect**: a review form is visible (rating 1–5 + text).
3. Submit a 4-star review with text.
4. **Expect**: the review appears immediately on the detail page; the
   average rating shows `4.0` and the review count `1`.
5. Submit a *second* review on the same skill (change the rating to 5,
   tweak the text).
6. **Expect**: the previous review is updated in place (still one review,
   now 5 stars); the average shows `5.0`.
7. As **Owner**, open your own skill's detail page.
8. **Expect**: no review form is shown.
9. As a third user **Stranger** (no booking), open the same skill.
10. **Expect**: no review form shown OR submission fails with an explanatory
    error.

### US6 — Manage personal listings

As **Owner**:

1. Open `/dashboard/`.
2. **Expect**: every skill you posted appears with `Edit` and `Delete`
   actions.
3. Click `Edit` on one skill; change the price; save.
4. **Expect**: redirected to detail page with success flash; the new price
   is reflected immediately on `/` and on the public detail page.
5. Click `Delete` on a different skill; confirm.
6. **Expect**: skill disappears from both `/dashboard/` and `/`.
7. Try to access another user's edit URL directly (e.g.,
   `/skills/<pk>/edit/` for a skill you do not own).
8. **Expect**: 403 Forbidden response.

---

## Resetting the local database

If you want a fresh start (e.g., to re-run the smoke test from scratch):

```bash
# Stop runserver first (Ctrl+C). Then:
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The data migration re-seeds the default categories automatically.

---

## Running the optional test suite

If tests have been added per `research.md` §R10:

```bash
python manage.py test
```

All tests should pass. Remember: tests are OPTIONAL per the constitution
and complement — but do not replace — the manual smoke-test walkthrough
above.

---

## Common beginner pitfalls (heads-up)

- **Forgot to run `makemigrations` after editing `models.py`.** The next
  `runserver` will print a warning about unapplied changes. Run
  `python manage.py makemigrations` and commit the generated migration
  alongside your model edit.
- **Edited a template but didn't reload the page hard.** Templates are
  re-read on every request in `DEBUG=True`, but stale CSS in the browser
  cache can mislead you. Use Cmd-Shift-R / Ctrl-Shift-R.
- **Logged-in user in one tab, anonymous in another from the same browser.**
  Sessions are per-browser. Use a private window for the anonymous role.
- **Tried to delete a `Category` that has skills.** This raises a
  `ProtectedError` because of `on_delete=PROTECT`. Retire it instead by
  unchecking `is_active` in the admin (see `data-model.md` §3).
- **Form fields render unstyled.** Make sure your template renders the form
  with Bootstrap 5 classes — typically via the Bootstrap-friendly form
  rendering snippet documented in the form templates.
