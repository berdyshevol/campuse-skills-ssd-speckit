# Feature Specification: Campus SkillSwap

**Feature Branch**: `001-campus-skillswap`
**Created**: 2026-04-25
**Status**: Draft
**Input**: User description: "Campus SkillSwap — a student marketplace where users can post skills or services they offer to others. Includes registration/login, skill posts (CRUD), browsing, search by title/category, booking/session requests, reviews & ratings, and a personal dashboard. Backend in Django, frontend in Next.js + Tailwind, SQLite for development."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse and Discover Skills as a Visitor (Priority: P1)

A prospective student visits the Campus SkillSwap site without an account and wants to see what skills and services other students offer. They land on a public listing page, scan available skills (each showing title, category, price/free indicator, availability), and click into a detail page to see the full description and contact preference. They can decide whether to register before reaching out.

**Why this priority**: Discovery is the marketplace's front door. Without a way to browse public listings, no visitor can evaluate value or convert into a registered user. This is the smallest slice that proves the marketplace concept.

**Independent Test**: With a database seeded with a handful of skill posts, an anonymous visitor can navigate to the public listings page, see at least one skill summary, click through to the detail page, and read the full skill information without being asked to log in.

**Acceptance Scenarios**:

1. **Given** the site has at least one published skill post, **When** a visitor opens the home/listings page, **Then** they see a list of skill posts each showing title, category, price (or "Free" indicator), and availability status.
2. **Given** a visitor is on the listings page, **When** they select a specific skill post, **Then** they see a detail view with the full description, owner display name, contact preference, price, category, and availability.
3. **Given** there are no published skills, **When** a visitor opens the listings page, **Then** they see a friendly empty-state message inviting them to register and post the first skill.

---

### User Story 2 - Register, Sign In, and Post a Skill (Priority: P1)

A student wants to offer tutoring or a service to other students. They register an account with email and password, log in, and create a skill post by filling in title, description, category, price (or marking it as Free), contact preference, and availability status. After submission, the post appears in the public listings and on the student's personal dashboard. They can log out and log back in later.

**Why this priority**: Posting is the marketplace's supply side. Without it, browsing in Story 1 has nothing to show. Together, Stories 1 and 2 form the minimum viable two-sided marketplace.

**Independent Test**: A new user can complete registration, log in, submit a valid skill post, and then verify the post appears both on the public listings and on their dashboard. After logout and re-login, the post persists.

**Acceptance Scenarios**:

1. **Given** a visitor with no account, **When** they complete the registration form with a valid email, password, and required profile fields, **Then** an account is created, they are logged in, and a confirmation message is shown.
2. **Given** a registered user is logged in, **When** they submit the "create skill" form with all required fields, **Then** the skill post is saved with the current timestamp and the user as owner, and a success message appears.
3. **Given** a registered user is logged in, **When** they submit the create-skill form with missing required fields, **Then** the form is rejected with field-level error messages and no post is created.
4. **Given** a logged-in user, **When** they click "log out," **Then** their session ends and they are redirected to the public listings page.
5. **Given** a registered user has logged out, **When** they log back in with correct credentials, **Then** they regain access to their dashboard and previously created posts.

---

### User Story 3 - Search Skills by Title or Category (Priority: P2)

A student looking for help in a specific subject (e.g., "calculus" or "graphic design") uses a search box to find relevant skills. They type a keyword and/or pick a category, and the listing narrows to matching posts. They can clear the search to return to the full listing.

**Why this priority**: As the catalogue grows, scrolling stops scaling. Search converts discovery from accidental to intentional, and the brief explicitly calls it out as a beginner-friendly enhancement. It depends on Stories 1 and 2 having data to filter, so it is P2.

**Independent Test**: With multiple skill posts spanning two or more categories, a user can enter a keyword that matches some titles, see only matching posts, switch to a category filter, and confirm the displayed results match the filter. Clearing the search restores the full list.

**Acceptance Scenarios**:

1. **Given** the listings page contains posts with varied titles, **When** a user types a keyword present in some titles and submits, **Then** only posts whose title contains the keyword (case-insensitive) are shown.
2. **Given** the listings page contains posts in multiple categories, **When** a user selects a single category filter, **Then** only posts in that category are shown.
3. **Given** a search returns no results, **When** the empty result page is rendered, **Then** a "no skills match your search" message is shown with a clear way to reset the filters.
4. **Given** filters are active, **When** the user clears the search, **Then** the full unfiltered listing is restored.

---

### User Story 4 - Request a Booking/Session for a Skill (Priority: P2)

A logged-in student finds a skill they want and submits a session request: a short message, proposed time, and any context. The skill owner receives the request, can review pending requests on their dashboard, and can accept or decline each one. The requester sees the current status (pending, accepted, declined) of their requests.

**Why this priority**: Booking turns browsing into action and is the marketplace's conversion event. It depends on Stories 1 and 2 (skills must exist) but is not required for read-only discovery, so it is P2.

**Independent Test**: A logged-in user submits a request for an existing skill, the skill's owner (a different account) sees the request on their dashboard, accepts it, and the requester sees the status change to "accepted."

**Acceptance Scenarios**:

1. **Given** a logged-in user is viewing a skill detail page they do not own, **When** they submit a request with a message and proposed time, **Then** a request is created in "pending" status and both the requester and the skill owner can see it on their respective dashboards.
2. **Given** a skill owner has a pending request on their dashboard, **When** they choose "accept" or "decline," **Then** the request status updates accordingly and the requester's view reflects the new status.
3. **Given** a user is not logged in, **When** they attempt to request a session, **Then** they are redirected to the login/registration page and the request is not created.
4. **Given** a user is viewing their own skill detail page, **When** the page renders, **Then** the "request a session" action is hidden or disabled (owners cannot book their own skills).

---

### User Story 5 - Rate and Review a Skill (Priority: P3)

After receiving help through a skill, a student leaves a star rating (1–5) and a short written review on that skill's page. The skill detail page shows an aggregate rating and a list of recent reviews. Owners cannot review their own skills.

**Why this priority**: Reviews build trust and improve discovery quality, but the marketplace functions without them in early use. They depend on bookings/usage existing, so they sit at P3.

**Independent Test**: A logged-in user (other than the owner) submits a 4-star review with text on a skill they have a booking for, and the skill detail page shows the new review and an updated average rating reflecting it.

**Acceptance Scenarios**:

1. **Given** a logged-in user has an accepted booking for a skill, **When** they submit a rating (1–5) and review text on that skill's page, **Then** the review is saved with their username and the current timestamp, and appears in the skill's reviews list.
2. **Given** a skill has multiple reviews, **When** a visitor opens the skill detail page, **Then** an average rating (rounded to one decimal) and the count of reviews are displayed alongside the most recent reviews.
3. **Given** a logged-in user is viewing their own skill, **When** the page renders, **Then** they cannot submit a review of it.
4. **Given** a user has no accepted booking for the skill, **When** they attempt to submit a review, **Then** the submission is rejected with an explanation.

---

### User Story 6 - Manage Personal Listings via Dashboard (Priority: P3)

A skill owner navigates to their dashboard to see all the skills they have posted, the booking requests they have received and sent, and reviews on their skills. From the dashboard they can edit any of their skill posts (changing title, description, price, availability, etc.) or delete posts they no longer want listed.

**Why this priority**: Edit/delete improves owner experience and listing hygiene but is not strictly needed for an MVP — owners can re-create posts if needed. The dashboard view itself becomes more valuable as more activity accumulates.

**Independent Test**: A logged-in owner opens their dashboard, edits one of their existing skill posts (changing the price), saves it, and the public listings page reflects the new price. They then delete a different post and confirm it disappears from public listings.

**Acceptance Scenarios**:

1. **Given** a logged-in user has at least one skill post, **When** they open their dashboard, **Then** they see all their own skill posts with edit and delete actions.
2. **Given** an owner is on the dashboard, **When** they edit a skill and submit valid changes, **Then** the post is updated and the public detail page reflects the new content.
3. **Given** an owner is on the dashboard, **When** they delete a skill, **Then** they are prompted for confirmation, and on confirm the skill is removed from public listings and from their dashboard.
4. **Given** a logged-in user, **When** they try to access another user's edit/delete URL directly, **Then** the action is blocked with a permission-denied response.

---

### Edge Cases

- **Duplicate skill titles by the same owner**: allowed, since two different sessions of the same topic are reasonable; the system disambiguates by ID and timestamp.
- **Long descriptions or titles**: enforce a maximum length on title (e.g., 120 chars) and description (e.g., 4000 chars) with friendly validation messages.
- **Free vs. priced posts**: a post is either Free or has a price ≥ 0; the owner cannot leave both unset or set a negative price.
- **Availability status changes mid-request**: if the owner marks a skill "unavailable" while a request is pending, the request remains visible but new requests are blocked until status returns to "available."
- **Self-actions**: a user cannot request their own skill, cannot review their own skill, and cannot leave more than one review per (user, skill) pair.
- **Account deletion / orphaned content**: out of scope for v1; assume accounts persist for the duration of the project.
- **Search with special characters or empty query**: an empty query returns the full unfiltered list; special characters are treated as plain text.
- **Categories**: categories are drawn from a curated list (managed by admin) so users cannot create arbitrary new ones.

## Requirements *(mandatory)*

### Functional Requirements

**Authentication & Accounts**

- **FR-001**: System MUST allow a visitor to register an account using an email address and a password.
- **FR-002**: System MUST allow a registered user to log in with their credentials and log out, ending the session.
- **FR-003**: System MUST persist user accounts and sessions across visits.
- **FR-004**: System MUST prevent unauthenticated users from creating, editing, or deleting skill posts, submitting booking requests, or submitting reviews.

**Skill Posts (CRUD)**

- **FR-005**: Authenticated users MUST be able to create a skill post with the following fields: title, description, category, price-or-free indicator, contact preference, availability status, owner (auto-assigned), and created-at timestamp (auto-assigned).
- **FR-006**: Skill post owners MUST be able to edit any field of their own skill posts.
- **FR-007**: Skill post owners MUST be able to delete their own skill posts.
- **FR-008**: System MUST prevent users from editing or deleting skill posts they do not own.
- **FR-009**: System MUST validate skill posts before save: required fields present, price non-negative when not marked Free, title and description within length limits, category from the allowed list.

**Browsing & Search**

- **FR-010**: System MUST provide a publicly accessible listing of skill posts visible without authentication.
- **FR-011**: System MUST provide a public detail view per skill post showing all displayable fields.
- **FR-012**: System MUST provide a search facility that filters the listing by keyword (case-insensitive substring match against title) and by category.
- **FR-013**: System MUST allow keyword and category filters to be combined and cleared.
- **FR-014**: Listings MUST default to a sensible order (newest first) when no filter is active.

**Booking / Requests**

- **FR-015**: Authenticated users MUST be able to submit a booking request for a skill they do not own, including a message and a proposed time.
- **FR-016**: Each request MUST have a status of `pending`, `accepted`, or `declined`, defaulting to `pending`.
- **FR-017**: Skill owners MUST be able to accept or decline pending requests on their skills.
- **FR-018**: Both requester and owner MUST be able to view the requests in which they participate, on their respective dashboards.
- **FR-019**: System MUST prevent a user from booking their own skill.
- **FR-020**: System MUST prevent new booking requests on skills marked unavailable.

**Reviews & Ratings**

- **FR-021**: Authenticated users with an `accepted` booking for a skill MUST be able to submit one rating (1–5 stars) and a written review on that skill.
- **FR-022**: System MUST display, on each skill detail page, the average rating and the count of reviews, plus the list of individual reviews with reviewer name and timestamp.
- **FR-023**: System MUST prevent a user from reviewing their own skill.
- **FR-024**: System MUST prevent a user from submitting more than one review per (user, skill) pair; subsequent submissions update their existing review.

**Dashboard**

- **FR-025**: Authenticated users MUST have a personal dashboard showing: their own skill posts (with edit/delete actions), booking requests they have made, and booking requests they have received.
- **FR-026**: The dashboard MUST be accessible only to the authenticated user it belongs to.

**Administration**

- **FR-027**: An administrator MUST be able to manage users, skill posts, categories, booking requests, and reviews through a privileged management interface.
- **FR-028**: System MUST provide a curated list of categories that administrators can add to, edit, or retire; non-admins cannot create new categories.

**Feedback & Messaging**

- **FR-029**: System MUST display user-facing confirmation, warning, and error messages for key actions (registration, login/logout, post create/edit/delete, request submission, review submission).
- **FR-030**: System MUST present friendly empty-states (e.g., empty listings, no search results, no requests) instead of blank pages.

### Key Entities *(include if feature involves data)*

- **User**: A registered student account. Attributes include identity (email, display name), credentials (handled by the authentication subsystem), and timestamps. Each user can own many skill posts, send many booking requests, receive many booking requests (via their skills), and write many reviews.
- **Skill Post**: A listing offered by a User. Attributes: title, description, category (reference), price (or "Free" indicator), contact preference, availability status, owner (reference to User), created-at. Has many booking requests and many reviews.
- **Category**: An administrator-managed taxonomy entry used to classify skill posts. Attributes: name, optional description. Each skill post belongs to exactly one category.
- **Booking Request**: A request from one User to engage a Skill Post owned by another User. Attributes: requester (reference to User), skill (reference to Skill Post), message, proposed time, status (`pending`/`accepted`/`declined`), created-at, updated-at.
- **Review**: A rating and written feedback left by a User on a Skill Post. Attributes: author (reference to User), skill (reference to Skill Post), rating (1–5), text, created-at. Constrained to one per (author, skill) pair, and only allowed when the author has an accepted booking on that skill.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time visitor can locate the public listings, open a skill detail page, and read its full description in under 60 seconds without logging in.
- **SC-002**: A new student can complete registration and publish their first skill post within 5 minutes of arriving on the site for the first time.
- **SC-003**: When the catalogue contains at least 25 skill posts across at least 3 categories, a search by keyword or category returns the correct subset of posts in 95% of cases (verified by sampled manual checks).
- **SC-004**: 90% of attempted invalid actions (missing required fields, unauthorized edits, self-booking, double review) are blocked with a clear, user-readable error message rather than a generic system error.
- **SC-005**: From the dashboard, a logged-in owner can edit any of their existing skill posts and see the change reflected on the public detail page within 5 seconds of saving.
- **SC-006**: A booking-request lifecycle (submit → owner accepts/declines → requester sees status) completes correctly and visibly to both parties in 95% of test runs across the standard browser set.
- **SC-007**: Every primary page (listings, detail, dashboard, login, register, create-skill) renders correctly on a typical desktop viewport (≥ 1280px) and a typical mobile viewport (≤ 414px) without content being cut off or overlapping.
- **SC-008**: A reviewer rating a skill they have an accepted booking for sees their review appear on the skill detail page, and the displayed average rating reflects the new score, immediately after submission.

## Assumptions

- **Open registration**: any visitor can register with an email and password; the project does not gate registration to a specific campus email domain. Verification of student status is out of scope for v1.
- **Off-platform fulfillment of paid services**: the "price" field is informational; payments and session scheduling are handled by users off-platform (e.g., they meet up or coordinate via the listed contact preference). The platform does not collect, hold, or process payments.
- **Contact preference is a fixed-list choice**: users pick from a short system-provided list (e.g., "email," "in-app message," "phone"); deeper messaging features (chat threads, attachments) are out of scope for v1.
- **Single role for end users**: all registered students are peers — any student can both post skills and request skills from others. There is no separate "tutor" role.
- **Administrator role**: a small number of operators have elevated access via the privileged management interface for moderation and category management.
- **Backend technology stack**: Django, with SQLite for local development (per project brief). Persistence and migrations are handled by Django's ORM.
- **Frontend technology stack**: Next.js with Tailwind CSS for styling (per user direction). The Django backend exposes data to the Next.js frontend; the integration pattern (REST or other) is a planning-phase decision.
- **Authentication scope**: standard email-and-password authentication is sufficient for v1; SSO, OAuth, two-factor, and social login are out of scope.
- **Internationalization, accessibility-AA conformance, and SEO optimization**: not in scope for v1; English-only with reasonable but not formally audited accessibility.
- **Scale**: the application targets a single-campus or course-sized audience (low hundreds of users, low thousands of posts) and does not need horizontal-scale infrastructure for v1.
- **Data retention**: no automated deletion or archival; all data persists for the lifetime of the project.
- **Out of scope for v1**: real-time notifications, in-app messaging threads, payment processing, calendar integration, mobile native apps, account deletion / GDPR-style data export, and image uploads.
