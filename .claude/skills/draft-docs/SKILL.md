---
name: draft-docs
description: Generates pre-populated documentation notes files from trunk2 context (PRs, deploy tags, Linear tickets). Use after a deploy or when the user wants to prepare docs updates, draft documentation, or bridge trunk2 changes to the docs repo.
---

Shared scripts are in: `~/.claude/skills/shared/scripts/`

Generate documentation notes files from trunk2 context, ready for the `/write-docs` skill in this repo. Output goes directly to `.claude/drafts/`, then invoke `/write-docs` to process.

## Task Progress Checklist

Copy this checklist and track progress:

```markdown
Docs Prep Progress:

- [ ] Step 1: Gather context (deploy tags, PRs, Linear tickets)
- [ ] Step 2: Classify PRs — identify documentable features
- [ ] Step 3: Research each feature deeply (diffs, Linear, existing docs)
- [ ] Step 4: Determine docs work needed (new page / update / skip)
- [ ] Step 5: Generate notes files
- [ ] Step 6: Output summary with copy instructions
```

## Inputs

The user may provide:

- **`latest`** — generate notes for user-facing features in the most recent deploy tag (mirrors `/changelog latest`)
- **A deploy tag or range** (e.g., `v126`, `v123 to v126`) — features shipped in those releases
- **PR numbers** — specific trunk2 PRs to document
- **Linear ticket IDs** — `TRUNK-NNNNN` references
- **A feature description** — freeform text about what needs documenting
- If nothing is provided, default to `latest` mode

## Output Location

Notes files are written to: `.claude/drafts/` in this repo (docs2).

Each run produces one or more files named `<featurename>.md` ready to be processed by `/write-docs`.

## Steps

1. **Gather context based on input**:
   - For `latest` or deploy tags: use `get-deploy-tags.sh` from `~/.claude/skills/shared/scripts/` to find PRs in the range, then `gh pr view` to get details
   - For PR numbers: use `gh pr view <number>` to get title, body, branch, diff
   - For Linear tickets: use `mcp__claude_ai_Linear__get_issue` to get details

2. **Classify PRs**: Split into user-facing vs. infrastructure (same logic as changelog skill). Only generate notes files for features that need documentation — not every user-facing change needs docs. Focus on:
   - New features or capabilities
   - Changed behavior or workflows
   - New configuration options
   - API changes
   - Features that customers have asked about

3. **For each documentable feature, research deeply**:
   - Read the PR diff: `gh pr diff <number> --name-only` to identify changed files, then read key files to understand the feature
   - Look up Linear tickets for descriptions, comments, and related tickets
   - Search existing docs via `mcp__claude_ai_trunk_docs__searchDocumentation` to find what currently exists and identify gaps
   - Search `#team-flaky-tests` and `#team-merge-queue` Slack channels for feature context, customer feedback, and usage details
   - Search Slite for internal specs, design docs, or planning notes that can inform documentation
   - Check if there are open changelog issues for this feature (`gh issue list --label changelog`) for additional context

4. **Determine what docs work is needed** for each feature:
   - **New page needed** — feature has no existing docs coverage
   - **Update existing page** — feature changes behavior described in current docs
   - **No docs needed** — bug fix or minor polish that doesn't affect documented behavior
   - Skip features that don't need docs changes

5. **Generate one notes file per feature** at `.claude/drafts/<featurename>.md` using this format:

   ```markdown
   # [Feature/Change Title]

   ## Type

   <!-- new-feature | update | fix | deprecation | explainer -->

   [type]

   ## Priority

   <!-- P1 | P2 | P3 | P4 -->

   [priority — P1 for new features, P2 for updates, P3 for fixes]

   ## Linear Tickets

   [list of TRUNK-NNNNN IDs found]

   ## What Changed

   [2-3 paragraph summary of what changed in the product, written from the
   user's perspective. Include specific details: new UI elements, new
   configuration options, changed behavior, new API endpoints, etc.]

   ## GitHub PRs

   [list of PR URLs from trunk-io/trunk2, with titles]

   ## Context Links

   [any Slack, Slite, Loom links found in Linear tickets or PR descriptions]

   ## Target Docs

   [specific docs pages that need updating, based on docs search results.
   Include the page title and URL. If a new page is needed, suggest where
   it should go in the hierarchy based on the groups defined in docs.json.]

   ## Existing Docs Gap Analysis

   [what the current docs say vs. what they should say after this change.
   Be specific — quote the outdated text if possible, and describe what
   needs to change.]

   ## Context

   [paste the most relevant context here:

   - Key sections from the PR description
   - Linear ticket description
   - Any code snippets that show the new behavior (config examples, API
     payloads, CLI commands, etc.)
   - Error messages or UI text that should appear in docs]
   ```

6. **Output summary**: Show the user:
   - List of notes files generated (with paths to `.claude/drafts/`)
   - For each: feature name, type (new/update), target docs page(s)
   - Features skipped (no docs needed) with brief reason
   - Suggested next step: `/write-docs` to process each draft

## Translating Code Changes

You are translating a code change (a GitHub pull request) for technical audiences.

1. Translate only what is evidenced in the PR body, the diff, linked issues, or review comments. Never invent functionality or user impact that isn't stated or clearly implied.
2. If the PR description is empty and the diff is mostly build artifacts or minified code, say you don't have enough context. Do not guess.
3. If you're uncertain, use phrases like "appears to" or "likely" and flag the output as low confidence.
4. For pure refactors or internal changes with no user-visible change, say so explicitly. Do not invent user-facing benefits.

For each notes file, generate a clear title and "What Changed" summary:

- **Title**: max 10 words, benefit-focused, present tense (e.g., "Flag Individual Tests as Flaky from Test Detail Page")
- **What Changed**: 3-5 sentences, max 150 words. Include what changed and why it matters to users.

## Guidelines

- **Code is law** — when Slack, Slite, or Linear content conflicts with the actual code (variable names, endpoints, UI labels, feature names, etc.), always use what's in the code/PR diffs. External discussions reflect intent; code reflects what shipped.
- **Be thorough in research** — the better the notes file, the better the docs output. Include code examples, config snippets, and specific UI details.
- **One file per feature** — don't combine unrelated features. If a deploy tag has 3 documentable features, create 3 files.
- **Focus on what's documentable** — not every PR needs docs. A CSS fix doesn't need a notes file. A new configuration option does.
- **Include the gap analysis** — this is the most valuable part. Telling the docs skill "page X says Y but should now say Z" saves significant research time.
- **Quote existing docs** when possible — paste the current text that needs updating so the docs skill can find and edit it precisely.
- **Suggest doc locations** — use docs search results and the groups defined in `docs.json` to recommend where content should live.
