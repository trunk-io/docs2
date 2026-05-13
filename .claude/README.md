# .claude — Agents, Skills, and Drafts

Claude Code configuration for the Trunk docs (Mintlify) repo. Skills are documentation-focused: scaffolding new pages, processing notes into PRs, reviewing changes, verifying PRs against production.

## Structure

```
.claude/
├── agents/                       # Subagent definitions (spawned via the Agent tool)
│   └── doc-researcher.md         # Gathers Linear/PR/Slite/docs context before writing
├── skills/                       # User-invoked workflows (triggered via /skill-name)
│   ├── docs-research/            # Audit existing docs to find gaps and placement
│   ├── outline-docs/             # Scaffold a new docs page from scratch
│   ├── write-docs/               # Trunk2 context → PR pipeline (9 phases)
│   └── verify-docs-pr/           # Verify a docs PR's feature is live in prod
├── drafts/                       # Optional input notes files for write-docs
│   └── TEMPLATE.md               # Scaffold for new draft notes
├── tmp/                          # Scratch outputs (gitignored)
├── settings.json                 # Shared permissions (committed)
└── settings.local.json           # Per-machine overrides (gitignored)
```

## Mental model

The flow is **research → write → verify**:

| Phase | Skill |
|---|---|
| Research | `/docs-research` (existing-coverage audit) + `doc-researcher` agent (Linear/PR/Slite context) |
| Write | `/outline-docs` (blank-page scaffold) or `/write-docs` (full PR pipeline) |
| Verify | `/verify-docs-pr` (is the feature actually live in prod?) |

## Agents vs. Skills

**Agents** (`agents/`) are autonomous subprocesses spawned by the `Agent` tool. They run with a specific model and limited toolset, do their work, and return results to the parent conversation. Use agents for parallelizable research tasks.

**Skills** (`skills/`) are user-invoked workflows triggered with `/skill-name`. They run in the main conversation with full tool access and follow a structured multi-phase pipeline. Use skills for end-to-end tasks that produce artifacts (PRs, tickets, reports).

| Type | How to invoke | Runs where | Best for |
|---|---|---|---|
| Agent | Spawned via the `Agent` tool | Background subprocess | Research, context gathering, parallel work |
| Skill | `/skill-name` | Main conversation | Multi-step workflows with user checkpoints |

## Skill reference

### `/docs-research`

**When:** Before writing a new doc (or right after a deploy) to audit existing coverage, find gaps, and decide where new content should live.

**What it does:** Five-phase audit:
1. Maps the relevant product-area group in `docs.json` and lists candidate `.mdx` files
2. Searches existing docs (hosted search + local grep) for the topic and synonyms
3. Classifies each hit as `covered`, `partial`, or `adjacent`
4. Recommends placement for new content — defaulting to extending an existing page over creating a new one
5. Generates a structured report with existing coverage, gaps, suggested placement, and cross-links to add

**Inputs:** A topic / feature name / product area. Optional: a feature description, PR body, or Linear ticket. `full` for a site-wide audit.

**Outputs:** A research report that feeds directly into `/outline-docs` or `/write-docs`.

---

### `/outline-docs`

**When:** Starting a brand-new docs page from scratch with no prior spec.

**What it does:** Asks page type (Overview / Reference / Guide), title, and save path. Generates a scaffolded `.mdx` file with sections pre-filled with 1-2 sentences plus focused `<!-- TODO -->` markers. Adds the page to `docs.json` navigation. Runs `trunk fmt`.

**Inputs:** Conversation context (title, page type, topic) — asks only for what's missing.

**Outputs:** A new `.mdx` file ready for content, plus a post-checklist.

---

### `/write-docs`

**When:** Given a draft notes file, trunk2 PR numbers, Linear ticket IDs, a deploy tag, or Slite links — anything that says "document this feature."

**What it does:** Full 9-phase pipeline:
1. Overlap detection (Phase 0) — refuses to proceed if another PR covers the same topic
2. Research across Linear, Slite, Slack, trunk2 PR diffs, and existing docs
3. Drafts new content or in-place edits, updating `docs.json` if adding pages
4. Creates a branch, commits, opens a **draft** PR with author tags
5. Updates Linear and writes a Slack post draft
6. Invokes `/verify-docs-pr` to check whether the feature is actually live in prod

**Inputs:** Trunk2 PR refs, Linear ticket IDs, a deploy tag, Slite links, or an optional `.claude/drafts/<topic>.md` file for batch workflows.

**Outputs:** Branch, draft PR, Linear update, Slack post in `tmp/<topic>/slack.md`.

**Discipline:** One feature = one PR. Always opens as draft for human review.

---

### `/verify-docs-pr`

**When:** A docs PR is open and you need to confirm the feature it documents is actually shipped to customers before publishing.

**What it does:** Classifies a PR as `live`, `staged`, `pending`, `blocked`, or `unknown` using indirect signals: linked eng PR merge state, follow-up PRs in trunk2, Slack rollout chatter, e2e flag defaults, and legacy code presence. Posts the verdict as a comment on the docs PR and the linked Linear ticket. Updates the PR title with a verdict prefix (`[ready to merge]`, `[blocked]`, etc.) and flips non-live PRs to draft.

**Inputs:** A PR number (single mode), or no arg for a sweep across all open PRs.

**Outputs:** PR comment, Linear comment, title prefix update, draft state.

**Auto-invoked:** by `/write-docs` Phase 4 after PR creation.

---

## Agent reference

### `doc-researcher`

Subagent (not a slash command). Spawned via the `Agent` tool with `subagent_type: doc-researcher`.

**Model:** Sonnet 4.6 (chosen for speed).

**Tools:** `Read`, `Grep`, `Glob`, `Bash` — read-only.

**When:** Before `/write-docs` when the scope is unclear or multiple tickets need surveying.

**What it does:** Reads Linear tickets, linked PRs, and existing docs pages. Returns a structured research brief: feature summary, source PRs (with GitHub author handles), current docs coverage, key technical details pulled from code, and a suggested doc structure.

**Use it in parallel** with other research (Slack, Slite searches) to save time.

## Drafts

`drafts/` is optional scratch space for batch workflows. `/write-docs` accepts trunk2 PR / Linear / deploy-tag refs directly, so most invocations skip drafts entirely. Use a draft file when you want to curate notes by hand before processing — for example, post-deploy when several features ship and you want to triage which ones need docs first.

- **`TEMPLATE.md`** — scaffold for new drafts. Don't edit; copy it.
- **`<featurename>.md`** — one per feature. Author manually, then run `/write-docs <featurename>`.

If you do use a draft file, treat it as input: never modify or delete it mid-pipeline.

## Tmp

`tmp/` is scratch space written by skills during execution:

- `tmp/<draft-name>/sources.md` — research audit trail for the reviewer
- `tmp/<draft-name>/slack.md` — Slack post draft (mrkdwn format, ready to paste)
- `tmp/report.html` — cumulative HTML report from `/write-docs` runs

Everything under `tmp/` is gitignored except `.gitkeep`.

## Settings

- **`settings.json`** — shared permissions baseline. Committed. Curate carefully; anything in here is auto-approved for every contributor on this repo.
- **`settings.local.json`** — per-machine overrides. Gitignored. Each contributor curates their own.

## Source of truth

Generic versions of these skills live in `~/Developer/gutils/claude-code/skills/trunk/` (the canonical personal-use copy). The versions in this directory are **project-tuned for Mintlify**:

- `docs-research` — audits `docs.json` groups, reads `.mdx` files, defaults to extending existing pages over creating new ones
- `outline-docs` — uses `.mdx`, updates `docs.json` nav, generates Mintlify callouts
- `write-docs` — updates `docs.json` instead of `summary.md`
- `verify-docs-pr` — hardcoded to `trunk-io/docs2`

When updating one of these skills, decide whether the change is generic (also update gutils) or project-specific (only update here). Intentional drift between the two is fine and expected.
