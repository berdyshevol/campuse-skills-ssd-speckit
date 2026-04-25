# Campus SkillSwap — Manual E2E Test Scenarios

Run via Playwright MCP against a freshly seeded local server. Mark each
scenario `[X]` when it passes; `[F]` if currently failing (with a note).

## Setup (run once before each test pass)

```bash
# Free port 8000
lsof -ti :8000 -sTCP:LISTEN 2>/dev/null | xargs -r kill -9

# Reset + seed demo data (alice, bob, charlie / password SkSwap!2025; 3 skills)
.venv/bin/python manage.py seed_demo

# Start backend
.venv/bin/python manage.py runserver 8000
```

Base URL: `http://127.0.0.1:8000/`

Demo accounts (all with password `SkSwap!2025`):

| User | Role in scenarios |
|------|-------------------|
| alice | Owner — owns "Python tutoring" ($20) and "Algebra basics" (Free) |
| bob | Owner — owns "Spanish conversation" ($15) |
| charlie | Stranger — owns nothing |

## Scope

In-scope: US1 (browse), US2 (auth + post), US3 (search), US6 (manage).
Out-of-scope (skipped this round): US4 booking, US5 reviews.

## Scenarios

### US1 — Browse and discover (anonymous)

- [X] **S1.** Anonymous visitor opens `/` and sees all 3 seeded skill cards
      with title, category, price (or "Free"), and availability badge.
- [X] **S2.** Clicking a card opens `/skills/<pk>/` showing description, owner
      username, contact preference, and full price/availability — no
      "Request a Session" form (anonymous).
- [X] **S3.** Empty-state copy with register/login CTAs renders when no
      skills exist (delete all seeded skills via shell, reload `/`).

### US2 — Register, sign in, post a skill

- [X] **S4.** Visitor clicks Register → fills valid form (new username + email
      + password) → is auto-logged-in, redirected to `/dashboard/`, sees
      success flash.
- [X] **S5.** Logged-in user clicks "Create skill" → submits valid form →
      redirected to detail page with success flash; new skill appears at `/`
      and on `/dashboard/` "My posts".
- [X] **S6.** Submit create-skill form with empty title → form re-renders
      with field-level error; no skill saved.
- [X] **S7.** Logout → public listings; nav shows Login/Register only.
      Log back in → dashboard "My posts" still lists the skill from S5.

### US3 — Search by title or category

- [X] **S8.** Type "python" in keyword input, submit → only "Python tutoring"
      shown; keyword input retains "python".
- [X] **S9.** Pick "Languages" category, submit → only "Spanish conversation"
      shown.
- [X] **S10.** Combine keyword "spanish" + category "Languages" → narrows to
      one card.
- [X] **S11.** Search for "xyznomatch" → "no skills match your search" empty
      state with a Clear-filters link that returns to full list.

### US6 — Manage personal listings (owner only)

- [X] **S12.** Logged in as alice, dashboard "My posts" lists both her
      skills with Edit + Delete buttons.
- [X] **S13.** Edit "Python tutoring" → change price to 25 → redirected to
      detail page with success flash; new price visible on detail and on `/`.
- [X] **S14.** On `/skills/<pk>/edit/` for a skill she does NOT own (bob's
      Spanish), alice gets HTTP 403.
- [X] **S15.** Delete one of alice's skills via the confirm page → removed
      from `/` and from `/dashboard/`.

## Status legend

- `[ ]` not yet tested
- `[X]` passed
- `[F]` failed — see note below the line
