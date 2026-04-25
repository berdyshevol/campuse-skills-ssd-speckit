<!--
SYNC IMPACT REPORT
==================
Version change: TEMPLATE (unfilled) → 1.0.0
Bump rationale: Initial ratification. The previous file was the unfilled template
                with placeholder tokens; this is the first concrete constitution,
                so MAJOR=1, MINOR=0, PATCH=0.

Modified principles (from placeholders → concrete names):
  - [PRINCIPLE_1_NAME]   → I. Beginner-First Pedagogy (NON-NEGOTIABLE)
  - [PRINCIPLE_2_NAME]   → II. Idiomatic Django, No Detours
  - [PRINCIPLE_3_NAME]   → III. Simplicity & YAGNI
  - [PRINCIPLE_4_NAME]   → IV. Incremental Vertical Slices
  - [PRINCIPLE_5_NAME]   → V. Readable Code with Teaching Comments

Added sections:
  - Technology Stack Constraints (replaces [SECTION_2_NAME])
  - Development Workflow & Quality Gates (replaces [SECTION_3_NAME])
  - Governance (filled with concrete amendment + versioning rules)

Removed sections: none.

Templates requiring updates:
  - .specify/templates/plan-template.md      ✅ aligned (Constitution Check
       gate already references this file; principles map to existing
       Complexity Tracking and Technical Context fields)
  - .specify/templates/spec-template.md      ✅ aligned (user-story priority
       structure satisfies Principle IV; no schema changes needed)
  - .specify/templates/tasks-template.md     ✅ aligned (story-grouped tasks
       and optional-tests stance match Principles I, III, IV)
  - .specify/templates/checklist-template.md ✅ aligned (no constitution-
       specific content)
  - .claude/skills/speckit-*                 ✅ aligned (commands reference
       this file generically; no agent-specific names embedded)
  - README.md / docs/quickstart.md           ⚠ pending — neither file exists
       yet; runtime guidance lives in CLAUDE.md and project_brief/brief.md.
       Re-evaluate when a README is added.

Follow-up TODOs: none. All placeholders resolved.
-->

# Campus SkillSwap Constitution

## Core Principles

### I. Beginner-First Pedagogy (NON-NEGOTIABLE)

Every contribution treats the codebase as teaching material first and a product
second. The implementing agent MUST act as both developer and patient instructor:
explain in plain language WHAT each non-trivial change does and WHY before or
alongside the code, and call out common beginner pitfalls (e.g. forgetting
`makemigrations`, mutating `request.user` server-side, missing CSRF tokens).
Jargon MUST be defined on first use within a feature's spec or plan.

**Rationale**: This project exists to help a learner build Django fluency. Code
that ships without an accessible explanation fails the project's primary goal,
even if it works.

### II. Idiomatic Django, No Detours

Solutions MUST use Django's built-ins before introducing alternatives: the
auth app, admin, ORM, ModelForm, generic class-based or function-based views,
the messages framework, template inheritance, and Django's own test runner.
External frameworks (DRF, Celery, custom middleware, alternative ORMs, SPA
frontends) are forbidden unless the spec explicitly requires them AND the plan
records the justification in Complexity Tracking.

**Rationale**: The learner is studying Django; detours into other ecosystems
dilute that learning and add maintenance surface a beginner project does not
need.

### III. Simplicity & YAGNI

Build only what the current spec requests. Premature abstractions
(service layers, repository patterns, custom managers, generic mixins),
speculative configuration, and unrequested feature flags are prohibited.
Three similar lines are preferred over an abstraction that hides them. SQLite
is the chosen database; Bootstrap 5 is the chosen UI library; do not swap
either without an amendment to this constitution.

**Rationale**: Complexity is the dominant failure mode for beginner projects.
Each abstraction added is a concept the learner now has to maintain, debug,
and reason about.

### IV. Incremental Vertical Slices

Features MUST be delivered as independently runnable, demoable user stories
in priority order (P1 → P2 → P3 …) per the spec template. Each story slice
MUST be independently testable through the browser or admin (model, view,
template, URL, migration where applicable) before the next slice begins. No
"foundational refactor" tasks may be scheduled that block more than one user
story without an explicit Foundational phase entry in `tasks.md`.

**Rationale**: Vertical slices keep the learner in a tight feedback loop where
every increment produces something visible and runnable, which is how Django
fluency is built.

### V. Readable Code with Teaching Comments

Source code MUST follow Django conventions for naming, file layout, and app
structure. Inline comments are REQUIRED where Django-specific behavior is
non-obvious to a beginner (e.g. `on_delete` choices, custom `save()` logic,
template tag semantics, `select_related` use, signal handlers, custom
`Meta` options). Comments MUST explain WHY, not WHAT the code already says.
Templates MUST use `{% extends %}` / `{% block %}` inheritance, not copy-paste.

**Rationale**: Pedagogical comments are part of the deliverable, not an
afterthought. They are the medium through which the codebase teaches.

## Technology Stack Constraints

The following stack is fixed by this constitution. Changing any item requires
a constitution amendment (MINOR or MAJOR depending on impact):

- **Language**: Python 3.11+
- **Framework**: Django (latest LTS available at the time of feature work)
- **Database**: SQLite (single-file, committed-friendly defaults)
- **Frontend**: Server-rendered Django templates with Bootstrap 5 and
  template inheritance; no SPA, no build step beyond `collectstatic`
- **Authentication**: `django.contrib.auth` (no third-party auth backends)
- **Admin**: `django.contrib.admin` registration is REQUIRED for every
  user-owned model
- **Messages**: `django.contrib.messages` for all user-facing flash feedback
- **Testing** (when tests are requested): Django's built-in test runner
  (`python manage.py test`) using `TestCase` / `Client`

The functional surface area of v1 is defined in `project_brief/brief.md` and
includes: registration/login/logout, a `Skill` model bound to `User`, CRUD
forms and views, dashboard, search by title or category, review & rating,
and booking/request flows. Features outside this surface area require a spec
and plan that pass the Constitution Check.

## Development Workflow & Quality Gates

All work follows the Spec Kit pipeline: `/speckit-specify` → `/speckit-clarify`
(when needed) → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement`.

**Gates that MUST pass before merging a feature**:

1. **Constitution Check** in `plan.md` is filled in and shows no unjustified
   violations. Any violation MUST appear in the Complexity Tracking table
   with a concrete simpler-alternative rejection reason.
2. **Migrations are committed** in the same change set as the model edits
   that produced them. `makemigrations` MUST NOT be deferred.
3. **Manual smoke test** of every user story slice through the running
   `runserver` instance OR the Django admin, with the result noted in the
   PR/commit message. Type checks and unit tests do not substitute for this.
4. **Admin registration** exists for every user-owned model added in the
   feature.
5. **Beginner-readability review**: at least one inline comment per
   non-obvious Django construct introduced in the diff, per Principle V.

Tests are OPTIONAL per the tasks template; when included, they MUST be
written before the implementation they cover and they MUST initially fail.

## Governance

This constitution supersedes ad-hoc preferences and prior conventions. When
guidance in this file conflicts with a feature request, the feature request
MUST be revised or the constitution MUST be amended — the conflict cannot be
silently ignored.

**Amendment procedure**:

1. Propose the change by editing `.specify/memory/constitution.md` via the
   `/speckit-constitution` command.
2. Update the Sync Impact Report comment at the top of the file.
3. Bump the version per the policy below.
4. Propagate changes to dependent templates listed in the report and mark
   each ✅ updated or ⚠ pending.
5. Commit the amendment with a message of the form
   `docs: amend constitution to vX.Y.Z (<summary>)`.

**Versioning policy** (semantic versioning of this document):

- **MAJOR**: Backward-incompatible governance change, principle removal, or
  redefinition that invalidates prior plans.
- **MINOR**: New principle or section added, or material expansion of an
  existing principle.
- **PATCH**: Clarifications, wording fixes, typo corrections, or
  non-semantic refinements.

**Compliance review**: Every `/speckit-plan` execution MUST evaluate the
Constitution Check gate against the principles above. Every
`/speckit-analyze` execution MUST flag drift between this file and the
spec/plan/tasks artifacts. Runtime development guidance for the agent lives
in `CLAUDE.md` and `project_brief/brief.md`; both are subordinate to this
constitution.

**Version**: 1.0.0 | **Ratified**: 2026-04-25 | **Last Amended**: 2026-04-25
