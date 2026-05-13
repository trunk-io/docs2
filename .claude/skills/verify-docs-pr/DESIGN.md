# verify-docs-pr — Design

**Date:** 2026-05-06
**Author:** Sam Gutentag (with Claude)
**Status:** Approved, pending implementation plan

## Problem

A docs PR can be perfectly written but premature to publish if the underlying feature is not actually live for customers. The canonical case: docs PR #589 documented the new filtered Uploads page; the eng PR (trunk-io/trunk2#3670) was merged on 2026-04-28 but gated behind LaunchDarkly flag `enableFilteredUploadsPage`, which was on in staging and off in prod. Without verification, those docs would have shipped pointing customers to a feature they could not yet use.

## Goal

A skill that verifies whether features documented in open docs PRs are live in production, classifies each PR's state, and posts the verdict on the PR and the linked Linear ticket. Runs manually on a single PR or as a sweep across all open docs PRs, and integrates into the existing `write-docs` flow as a post-creation step.

## Decisions (agreed via brainstorming)

| Area | Decision |
|---|---|
| Live signal | Multi-signal classification: `live` / `staged` / `pending` / `blocked` / `unknown` |
| Inputs | Single PR by number AND sweep all open docs PRs (no arg) |
| Outputs | Terminal report + comment on docs PR + comment on linked Linear ticket |
| `write-docs` integration | Post-Phase 4. PR opens as draft, verification runs at the end |
| Signal sources | Indirect only — eng PR merge state, follow-up PRs, Slack search, e2e flags.json, legacy code presence |
| Skill style | Pure prose (matches `write-docs`). Sweep mode dispatches parallel agents when input >10 PRs |
| Source of truth | `gutils/claude-code/skills/trunk/verify-docs-pr/` |
| Symlinks | `~/.claude/skills/verify-docs-pr` and `<docs>/.claude/skills/verify-docs-pr` |

## Per-PR verification logic

For each docs PR, the skill runs five steps.

### Step A — Parse PR body

Extract:
- trunk2 PR references (`trunk-io/trunk2#NNNN` or full URLs). Generalized: any `trunk-io/<repo>#NNN` reference works; flag detection only runs against trunk2.
- Linear ticket IDs (`TRUNK-XXXXX`).
- Slack thread links (kept for context; not searched directly here).

If the PR body has no engineering PR references, fall back to the linked Linear ticket and check its `relations` for related engineering tickets, then trace from those tickets to their PRs.

### Step B — Check eng PR state

For each engineering PR reference:
- `gh pr view <num> --repo trunk-io/<repo>` to retrieve state, `mergedAt`, files changed.
- If state is `open` or `closed` (not merged): mark `blocked` and stop further checks for that reference.
- If state is `merged`: continue.
- If the merge commit is no longer reachable from `main` (eng PR was reverted): treat as `blocked` with a "reverted" note.

### Step C — Find feature flags

From the merged eng PR's diff:
- Grep changed files for LaunchDarkly flag patterns: `enable*`, `show*`, references to `flags.ts`, strings inside `useFeatureFlag()` / `useFlag()` calls.
- Pull flag names mentioned in the PR body itself (eng PRs frequently say "gated behind the `enableFooBar` flag" — easy regex on backticks adjacent to "flag").

If no flags found anywhere, the feature is ungated. Skip to classification with `flag=none`.

### Step D — Gather rollout signals (per flag)

For each detected flag:
- `gh search prs --repo trunk-io/trunk2 <flag-name>` — find any follow-up PRs touching it (rollout, deletion, ramp-up).
- Slack search via MCP across `#eng`, `#team-flaky-tests`, `#team-merge-queue`, `#production-notifications`, `#staging-notifications` for the flag name. Look for LaunchDarkly bot announcements and manual confirmations.
- Read `ts/apps/e2e/flags.json` from trunk2 main. Note: a `true` default here only confirms it works in tests, not prod.
- Grep trunk2 main for any "legacy" code path mentioned in the eng PR (e.g., `UploadsClient` for #3670). If still present, flag is not yet 100% rolled out.

### Step E — Classify

| Verdict | Conditions |
|---|---|
| `live` | Eng PR merged AND (no flag found OR Slack confirms 100% prod OR legacy code deleted) |
| `staged` | Slack confirms flag on in staging, off in prod |
| `pending` | Eng PR merged, flag still off (no rollout signals) |
| `blocked` | Eng PR not merged, or merge commit reverted |
| `unknown` | Could not determine; flagged for manual review |

Multiple eng PRs with mixed states: most conservative verdict wins. If any referenced eng PR is unmerged, the docs PR is `blocked`.

## Outputs

### Terminal — single mode

```
verify-docs-pr #589 (2026-05-06)
Verdict: pending

Eng work:
  trunk-io/trunk2#3670 — merged 2026-04-28
Feature flag:
  enableFilteredUploadsPage (LaunchDarkly)
Rollout signals:
  - No follow-up PRs touched the flag in trunk2 main
  - Slack: Tyler Jang in #eng (2026-04-16) — "flagged on in staging, off in prod"
  - Legacy UploadsClient still referenced in trunk2 main
  - e2e flags.json default: true (test only)

Reasoning:
  Eng merged but flag is gated off in prod. Customers cannot use this feature.

Suggested next:
  Ping @mb1206 for prod rollout ETA. Re-run /verify-docs-pr 589 after rollout.
```

### Terminal — sweep mode

```
verify-docs-pr — sweep across 41 open PRs (2026-05-06)

#589 pending   Uploads page         trunk2#3670 merged; flag off in prod
#534 live      Test case labels     trunk2#3501 merged; no flag
...

Summary: 24 live, 4 staged, 8 pending, 3 blocked, 2 unknown
```

Sorted by verdict severity: `blocked` → `pending` → `staged` → `unknown` → `live`. Most actionable first.

### PR comment

Posted as a one-block markdown comment. Re-runs **edit the existing comment** in place — skill detects its own prior comment via the HTML marker `<!-- verify-docs-pr -->`.

```markdown
<!-- verify-docs-pr -->
**Verification status (2026-05-06): `pending`**

Eng work merged but feature flag still off in prod.

- Eng PR: trunk-io/trunk2#3670 — merged 2026-04-28
- Flag: `enableFilteredUploadsPage`
- State: on in staging, off in prod (per #eng, 2026-04-16)
- Legacy `UploadsClient` code path still present in trunk2 main

Hold off on publishing. Re-run `/verify-docs-pr 589` after rollout.
```

Verdict-specific opening line:
- `live` — "Verified: customers can use this. Ready to publish."
- `staged` — "On in staging only. Re-run after prod rollout."
- `pending` — "Eng merged but flag off in prod. Hold off."
- `blocked` — "Eng PR not merged. Hold."
- `unknown` — "Could not determine state from available signals. Manual check needed."

### Linear ticket comment

Mirrors the PR comment with the docs PR link added at the top. Same `<!-- verify-docs-pr -->` marker for idempotent re-runs.

### PR state action

- `live` — no PR state change.
- `staged` / `pending` / `blocked` / `unknown` — if PR is `ready`, flip to `draft`. If already draft, no-op. Belt-and-suspenders against accidental auto-merge.
- PR already merged — skip entirely. Skill prints "PR #N already merged; skipping" and moves on.

## `write-docs` integration

A new Phase 5 at the end of `write-docs`:

> After PR #N is opened: invoke `verify-docs-pr` with PR number N.

Behavior:
- Runs the per-PR verification logic.
- Posts the verdict comment on the new draft PR.
- Posts the verdict comment on the linked Linear ticket.
- Prints terminal output to the user.

Does **not** block PR opening (already opened by Phase 4), change PR labels, move Linear status, or fail `write-docs` if verification errors. A skill error prints a warning and continues.

## Sweep parallelization

| PR count | Strategy |
|---|---|
| ≤10 | Sequential. Agent-spawn overhead exceeds savings |
| >10 | Dispatch parallel sub-agents in chunks of ~13 PRs each |

Each agent's job:
- Run the per-PR verification on its assigned chunk.
- Post the comment on PR + Linear.
- Return a structured result back to main: `{pr, verdict, summary_line}`.

Main thread aggregates, sorts by severity, and prints the summary table. If an agent dies before reporting, main lists the PRs in that chunk as "unverified" so they can be retried individually with `/verify-docs-pr <num>`.

## Errors and edge cases

| Case | Handling |
|---|---|
| PR body has no eng PR refs | Fall back to linked Linear ticket. Read its `relations` for related engineering tickets, then check those tickets' linked PRs. |
| No Linear ticket either | Verdict = `unknown`. Comment lists what's missing. |
| Eng PR is in a non-trunk2 repo (e.g., `analytics-cli`, `flake-farm`) | Generic handling. Any `trunk-io/<repo>#NNN` reference gets the same merge-state + diff inspection. Flag detection only runs against trunk2. |
| Slack search returns zero hits for a flag | Not an error. Counts as a `pending` signal ("no rollout chatter found"). |
| `gh` or Slack API timeout | Retry once. On second failure, continue with partial data and mark verdict as `unknown` with a note about the unavailable signal. |
| Multiple eng PRs with mixed states | Most conservative wins. Any unmerged ref → `blocked`. |
| Eng PR merged then reverted | Detect by checking merge commit reachability from `main`. Treat as `blocked` with a "reverted" note. |
| Re-run when prior `<!-- verify-docs-pr -->` comment exists | Edit the existing comment in place. Same on Linear. Verdict timestamp updates. |

## Testing

No unit tests. Validation checklist before merging the skill:

1. **Pending case** — `/verify-docs-pr 589` classifies as `pending`, references `enableFilteredUploadsPage`.
2. **Live case** — `/verify-docs-pr 534` (test case labels) classifies as `live` (eng merged, no flag found).
3. **No eng refs case** — `/verify-docs-pr 522` (org slug audit, pure docs bug fix) classifies as `live` or `unknown` with reason "no eng PR found, pure docs change".
4. **Sweep case** — `/verify-docs-pr` against current 41 open PRs. Spot-check 5 random verdicts against manual judgment.
5. **Re-run idempotency** — run twice on #589, existing comment is edited, no duplicate.
6. **`write-docs` integration** — open a fresh draft PR via `write-docs`, verify Phase 5 fires automatically and posts a verdict.

## Implementation phases

This work has two phases. The first must complete before the second starts.

### Phase 1 — migrate existing docs skills to gutils

The repo-specific skills currently live only in `<docs>/.claude/skills/`. Migrate them to follow the same dual-symlink pattern as the new skill.

Skills to migrate:
- `write-docs`
- `outline-docs`
- `review-docs`

End state for each:
- Physical files: `gutils/claude-code/skills/trunk/<skill>/`
- Symlink: `~/.claude/skills/<skill>` → gutils
- Symlink: `<docs>/.claude/skills/<skill>` → gutils

### Phase 2 — build verify-docs-pr

Create the new skill following the patterns established in Phase 1.

End state:
- Physical files: `gutils/claude-code/skills/trunk/verify-docs-pr/`
- Symlink: `~/.claude/skills/verify-docs-pr` → gutils
- Symlink: `<docs>/.claude/skills/verify-docs-pr` → gutils
- `SKILL.md` implementing the design above
- `write-docs/SKILL.md` updated to invoke verify-docs-pr at the end of Phase 4
