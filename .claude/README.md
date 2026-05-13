# .claude — Agents, Skills, and Drafts

Claude Code configuration for the Trunk docs (Mintlify) repo. Skills are documentation-focused: scaffolding new pages, processing notes into PRs, reviewing changes, verifying PRs against production.

## Structure

```
.claude/
├── agents/                       # Subagent definitions (spawned via the Agent tool)
│   └── doc-researcher.md         # Gathers Linear/PR/Slite/docs context before writing
├── skills/                       # User-invoked workflows (triggered via /skill-name)
│   ├── outline-docs/             # Scaffold a new docs page from scratch
│   ├── write-docs/               # Notes → PR pipeline (9 phases)
│   ├── review-docs/              # Pre-PR review of local changes
│   ├── draft-docs/               # Generate notes files from trunk2 context
│   ├── verify-docs-pr/           # Verify a docs PR's feature is live in prod
│   └── docs-review/              # Audit live docs.trunk.io pages
├── drafts/                       # Input notes files for write-docs
│   └── TEMPLATE.md               # Scaffold for new draft notes
├── tmp/                          # Scratch outputs (gitignored)
├── settings.json                 # Shared permissions (committed)
└── settings.local.json           # Per-machine overrides (gitignored)
```

## Agents vs. Skills

**Agents** (`agents/`) are autonomous subprocesses spawned by the `Agent` tool. They run with a specific model and limited toolset, do their work, and return results to the parent conversation. Use agents for parallelizable research tasks.

**Skills** (`skills/`) are user-invoked workflows triggered with `/skill-name`. They run in the main conversation with full tool access and follow a structured multi-phase pipeline. Use skills for end-to-end tasks that produce artifacts (PRs, tickets, reports).

| Type | How to invoke | Runs where | Best for |
|---|---|---|---|
| Agent | Spawned via the `Agent` tool | Background subprocess | Research, context gathering, parallel work |
| Skill | `/skill-name` | Main conversation | Multi-step workflows with user checkpoints |

## Skill reference

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

**Inputs:** A `.claude/drafts/<topic>.md` file (preferred), or raw PR/ticket references.

**Outputs:** Branch, draft PR, Linear update, Slack post in `tmp/<topic>/slack.md`.

**Discipline:** One draft = one PR. Always opens as draft for human review.

---

### `/review-docs`

**When:** Docs changes are ready locally and you want a structural review before opening a PR.

**What it does:** Five-phase review:
1. Identifies changed `.mdx` files via `git diff main...HEAD`
2. **Audits `docs.json` redirects** for stale or missing entries when files have been moved or deleted
3. Runs `trunk fmt` and `trunk check`
4. Reads sibling pages in the same product area to establish a style baseline
5. Reviews each file for repetition, structural completeness, logic errors, and Trunk style consistency

**Inputs:** Optional file path (single-file mode), otherwise the full branch diff.

**Outputs:** A structured report. Offers to apply mechanical fixes directly.

---

### `/draft-docs`

**When:** After a trunk2 deploy, or anytime you want to pre-populate drafts from PR / Linear / deploy-tag context.

**What it does:** Reads trunk2 PRs, Linear tickets, and Slack/Slite context. Classifies which PRs need docs. For each, generates a `<featurename>.md` notes file in `.claude/drafts/` containing: feature summary, target pages, gap analysis, code references, and "what changed" prose.

**Inputs:** A deploy tag, `latest`, PR numbers, Linear IDs, or a freeform feature description.

**Outputs:** One notes file per documentable feature, written directly to `.claude/drafts/` for processing by `/write-docs`.

---

### `/verify-docs-pr`

**When:** A docs PR is open and you need to confirm the feature it documents is actually shipped to customers before publishing.

**What it does:** Classifies a PR as `live`, `staged`, `pending`, `blocked`, or `unknown` using indirect signals: linked eng PR merge state, follow-up PRs in trunk2, Slack rollout chatter, e2e flag defaults, and legacy code presence. Posts the verdict as a comment on the docs PR and the linked Linear ticket. Updates the PR title with a verdict prefix (`[ready to merge]`, `[blocked]`, etc.) and flips non-live PRs to draft.

**Inputs:** A PR number (single mode), or no arg for a sweep across all open PRs.

**Outputs:** PR comment, Linear comment, title prefix update, draft state.

**Auto-invoked:** by `/write-docs` Phase 4 after PR creation.

---

### `/docs-review`

**When:** Auditing existing docs.trunk.io pages for accuracy, naming consistency, AI-readability, or running a site-wide quality pass.

**What it does:** Reads local `.mdx` files and reviews them for: factual accuracy against the code, naming consistency, structural issues, and AI-friendliness (clear hierarchy, scannable headers, no ambiguous pronouns). Reports findings.

**Inputs:** A page path or glob, a product area name, `full` for a site-wide pass, or no arg to ask.

**Outputs:** A structured audit report.

**vs. `/review-docs`:** `/review-docs` is pre-PR diff review on your local branch. `/docs-review` audits already-published pages for ongoing quality.

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

`drafts/` holds input notes files that feed into `/write-docs`. Each file represents one documentable feature; processing it produces one PR.

- **`TEMPLATE.md`** — scaffold for new drafts. Don't edit this; copy it.
- **`<featurename>.md`** — one per feature. Generated either manually or by `/draft-docs`.

Drafts are inputs, not outputs. Never modify or delete a draft mid-pipeline — it's the source of truth for what was requested.

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

- `outline-docs` — uses `.mdx`, updates `docs.json` nav, generates Mintlify callouts
- `review-docs` — audits `docs.json` redirects, expects Mintlify callout components, no GitBook syntax
- `write-docs` — updates `docs.json` instead of `summary.md`
- `verify-docs-pr` — hardcoded to `trunk-io/docs2`
- `draft-docs` — outputs directly to `.claude/drafts/` (no copy step needed)
- `docs-review` — reviews `.mdx` files

When updating one of these skills, decide whether the change is generic (also update gutils) or project-specific (only update here). Intentional drift between the two is fine and expected.
