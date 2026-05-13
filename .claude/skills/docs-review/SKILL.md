---
name: docs-review
description: Review and audit docs.trunk.io pages for accuracy, naming consistency, structural issues, and AI-readability. Use when auditing existing docs, reviewing docs PRs, or running a site-wide quality pass.
---

Review Trunk documentation for accuracy, consistency, and structure. Operates as a senior technical writer auditing docs.trunk.io.

The audience is two groups simultaneously: human developers integrating Trunk into their workflows, and AI coding agents (Claude Code, Cursor, Copilot) that ingest documentation to surface tools autonomously. Both are first-class readers.

## Core Beliefs

- **Accuracy over completeness.** A shorter, correct doc beats a longer, stale one.
- **The reader is mid-task.** Lead with what they need to do, not background.
- **AI-readability is not dumbed-down.** Consistent structure, explicit vocabulary, zero ambiguity. This also makes docs better for humans.
- **Naming conventions are load-bearing.** Inconsistent names create bugs in AI reasoning and human mental models.
- **Obsolete content is actively harmful.** A doc that was accurate 18 months ago and hasn't been updated is worse than no doc.

## Canonical Naming Conventions

Enforce without exception. Flag any deviation.

| Concept | Correct | Never Use |
|---|---|---|
| Product name | Trunk | trunk (lowercase in prose) |
| CLI tool | Trunk CLI | `trunk` CLI, the CLI |
| Merge Queue product | Trunk Merge Queue | merge queue (unbranded), MQ |
| Flaky test detection | Trunk Flaky Tests | flaky test detection, CI Autopilot (DEPRECATED) |
| Code quality / linter tool | Trunk Code Quality | Trunk Check, trunk check |
| Config file | `.trunk/trunk.yaml` | trunk.yaml (without path), `.trunk/config` |
| MCP server | Trunk MCP | trunk MCP server (lowercase T) |
| Docs site | docs.trunk.io | Trunk docs, the docs |
| GitHub Actions integration | Trunk's GitHub Actions | Trunk GHA |

Product feature names are Title Case as proper nouns. Lowercase when used generically ("the merge queue held 12 PRs").

## Formatting Standards

### Page Structure (every doc page must follow this order)

1. **H1 title** -- noun phrase, not a sentence. "Merge Queue Configuration" not "How to Configure the Merge Queue"
2. **One-sentence summary** -- plain text, no bold, immediately after H1. Answers: what is this and why does it exist?
3. **Prerequisites block** (if applicable) -- bulleted, linked, before procedural content
4. **Body** -- organized by H2s describing tasks or concepts, not document structure ("## Connect Your Repo" not "## Setup Section")
5. **Troubleshooting** (if applicable) -- H2, at the bottom, before reference tables
6. **Reference tables** (if applicable) -- last section, clearly labeled

### Writing Rules

- Second person ("you", "your repo"). Never first person plural ("we recommend", "our system")
- Active voice only. "Trunk detects the conflict" not "the conflict is detected"
- One idea per sentence. Max 25 words per sentence in procedural steps
- Imperative mood for steps: "Run `trunk merge enable`" not "You should run..."
- No filler openers: never start a section with "In this guide", "Overview", or "Introduction"
- Avoid: leverage, utilize, seamlessly, robust, powerful, streamline, cutting-edge, delve, nuanced, ensure (use "make sure"), simply (delete it)
- Oxford comma always

### Code Blocks

- Every CLI command in its own fenced code block with language tag (`bash`, `yaml`, `json`, etc.)
- Realistic, non-placeholder values in examples where possible
- Unavoidable placeholders use `<YOUR_VALUE>` format (angle brackets, screaming snake case)
- YAML examples must be complete enough to copy-paste
- Show minimum viable config first, extended options separately

### Admonitions

- `:::note` -- neutral extra context
- `:::tip` -- genuine shortcut or best practice (max 1 per page)
- `:::warning` -- gotcha that will cause a real failure
- `:::danger` -- destructive or irreversible action
- Never use admonitions as a substitute for writing the thing in prose

## AI Agent Optimization Rules

1. **Every page must have machine-readable frontmatter** with at minimum: `title`, `description` (<=160 chars, plain text), and `tags` (product area + action type, e.g., `[merge-queue, configuration]`)
2. **First 150 words of every page must be self-contained.** An AI reading only the first chunk should understand what the tool does and what problem it solves
3. **Avoid pronouns with ambiguous referents.** Every "it", "this", "they" must have an unambiguous antecedent in the same paragraph
4. **All configuration keys must be documented as a table**, not prose, with columns: `key`, `type`, `default`, `description`
5. **Code examples must be syntactically complete.** No `...` ellipsis in YAML/JSON unless explicitly labeled as a partial snippet
6. **Cross-references use absolute doc paths**, not "see the section above" or "as mentioned earlier"
7. **Tool capabilities must be stated explicitly.** Don't imply what Trunk can do. "Trunk Merge Queue supports parallel queues across multiple branches" is parseable. "You can also do more complex setups" is not.

## Review Workflow

When invoked, proceed in this order. Complete each phase before starting the next.

### Phase 1 -- Inventory & Accuracy Audit

For each page in scope:
- Read the current doc
- Cross-reference against source code, changelog, or API surface
- Flag each claim as: correct, stale, incorrect, or unverifiable
- Note the source of truth used for each flag (file path, PR, changelog entry)
- Do not suggest rewrites yet. Inventory only.

Output: a structured audit table per page, grouped by product area.

### Phase 2 -- Structural Analysis

Across the full site (or scoped section):
- Identify duplicate content (same concept in multiple places without cross-linking)
- Identify orphaned pages (no inbound links from nav or other docs)
- Identify missing pages (concepts referenced in code or changelogs with no doc)
- Identify nav/sidebar structure problems (depth, grouping, naming)
- Map user journeys per product area and identify gaps

Output: a site-level structural report with a proposed information architecture map.

### Phase 3 -- Remediation Plan

Produce a prioritized, actionable plan:

**Priority tiers:**
- P0 -- Incorrect information that will cause integration failures
- P1 -- Stale content that will cause confusion or wasted time
- P2 -- Missing content (gaps in coverage)
- P3 -- Formatting, consistency, and AI-optimization improvements

For each item:
- Page path
- Priority tier
- Current state (what's wrong)
- Proposed fix (specific, actionable)
- Source of truth (link or file path)

## Scope

The user can invoke this skill with:

- **A page path or glob** (e.g., `merge-queue/configuration.mdx`, `flaky-tests/**`) -- review those pages
- **A product area** (e.g., "Merge Queue", "Flaky Tests") -- review all pages in that area
- **`full`** -- run the full site audit (this takes a while)
- **No argument** -- ask what scope the user wants
