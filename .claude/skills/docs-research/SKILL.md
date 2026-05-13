---
name: docs-research
description: >-
  Audit the existing Mintlify docs site to inform new documentation work.
  Run before /outline-docs or /write-docs to (1) identify gaps in coverage,
  (2) recommend placement for new content, and (3) prevent duplicated effort
  by surfacing existing pages that already touch the topic.
allowed-tools: Read, Glob, Grep, Bash(rg *), Bash(jq *), mcp__claude_ai_trunk_docs__searchDocumentation
---

# Docs Research

Survey the existing Trunk docs site before writing new content. Produces a structured report covering existing coverage, gaps, recommended placement, and cross-link opportunities.

## Inputs

The user provides:

- **A topic, feature name, or product area** — required scope (e.g., "auto-quarantine override", "Merge Queue health page", "flaky test history timeline")
- **Optional context** — a feature description, PR body, Linear ticket, or notes file that describes what's about to be documented
- **`full`** — site-wide audit mode (slower; reads every page in every product area)

If no scope is provided, ask what to research before proceeding.

## Workflow

Follow these phases in order.

### Phase 1: Map the relevant area

1. Read `docs.json`. Identify which top-level group(s) the topic belongs to (e.g., `flaky-tests`, `merge-queue`, `setup-and-administration`).
2. List all `.mdx` files in the relevant group directories via `Glob`.
3. For each candidate page, read its frontmatter (`title`, `description`) and section headers (lines starting with `##` or `###`) to build a lightweight coverage map. Don't read full bodies yet.

In `full` mode, skip the topic-narrowing and walk every group.

### Phase 2: Search for topical overlap

For the given topic and its likely synonyms:

1. **Hosted docs search** — `mcp__claude_ai_trunk_docs__searchDocumentation` for the topic, the feature name, and 2-3 likely synonyms.
2. **Local grep** — `Grep` across the relevant `.mdx` files for the same terms.
3. **Hit list** — for each match, capture:
   - File path
   - Section header containing the match
   - One-line summary of what that section currently says about the topic (read just enough of the section body to summarize)

### Phase 3: Classify each hit

For every existing page that touches the topic, label it:

| Label | Meaning |
|---|---|
| `covered` | Topic is fully documented here; new content would duplicate |
| `partial` | Topic is mentioned briefly; could be expanded in-place rather than creating a new page |
| `adjacent` | Related but distinct topic; new content should cross-link, not merge |

Anything mentioned in the input scope but absent from the hit list is a **gap**.

### Phase 4: Recommend placement

For each gap or partial-coverage finding, propose where the new content should live:

1. Identify the most relevant product-area group in `docs.json`.
2. Decide between **extending an existing page** (default) and **creating a new page** (only if the topic clearly doesn't fit any existing page's scope).
3. If creating new, suggest 2-3 specific placement options with rationale (e.g., "new file under `flaky-tests/configuration/auto-quarantine-overrides.mdx`, between `auto-quarantine.mdx` and `quarantine-history.mdx` to maintain the configuration → behavior → audit ordering").
4. Note natural cross-links — pages that should reference the new content once it exists.

**Bias:** extending an existing page beats creating a new one. Only recommend a new page when the topic warrants its own scope and the existing pages would feel bloated if extended.

### Phase 5: Generate report

Print a structured report. Format:

```
Docs Research — <topic>
========================================

## Existing coverage

| Page | Coverage | What it says |
|---|---|---|
| <path>.mdx | covered | <one-line summary> |
| <path>.mdx | partial | <one-line summary; what's missing> |
| <path>.mdx | adjacent | <one-line summary; how it relates> |

## Gaps
- <specific aspect> — not covered anywhere
- <specific aspect> — not covered anywhere

## Recommended placement
1. **Extend** `<existing-page>.mdx` — <rationale>
2. **New page** at `<path>.mdx` — <rationale, including where it sits in the nav>

## Cross-links to add
- `<existing-page>` → `<new-content>`
- `<existing-page>` → `<new-content>`

## Suggested next step
- /outline-docs to scaffold <X> at <path>
- /write-docs <PR-or-ticket-ref> targeting <path>
- (no action — topic is already well covered)
```

In `full` mode, replace the per-topic structure with a per-group coverage matrix.

## When to use

- **Before `/outline-docs`** — confirm a new page is needed and identify the right path
- **Before `/write-docs`** — surface existing content the new docs should reference or replace
- **After a deploy** — spot gaps where shipped features are undocumented
- **For periodic audits** — run in `full` mode to find stale, duplicated, or thin coverage across product areas

## Guidelines

- **Code is law.** Prefer canonical sources (trunk2 PRs, code, official Mintlify docs) over Slack speculation when classifying coverage.
- **Be specific.** "Auto-quarantine is mentioned" is useless. "Auto-quarantine is mentioned in `flaky-tests/configuration.mdx` Phase 3 as a one-liner; behavior details and override flow are missing" is what we want.
- **Default to extending, not creating.** Three thin pages on adjacent topics is worse than one well-organized page. Only recommend a new page when the topic deserves its own scope.
- **Surface dependents.** When a page changes location or scope (in `full` mode audits), note any cross-links from other pages that would need updating.
