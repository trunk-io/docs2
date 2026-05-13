---
name: verify-docs-pr
description: Verify that features documented in open docs PRs are actually live in production before publishing the docs. Classifies each PR as live, staged, pending, blocked, or unknown using indirect signals (eng PR merge state, follow-up PRs in trunk2, Slack rollout chatter, e2e flag defaults, legacy code presence). Posts the verdict on the docs PR and the linked Linear ticket. Use when given a docs PR number, when running a sweep across all open docs PRs, or as the post-creation step inside write-docs.
allowed-tools: Bash(gh *), Bash(git *), Bash(grep *), Bash(jq *), Read, Grep, mcp__claude_ai_Linear__get_issue, mcp__claude_ai_Linear__list_comments, mcp__claude_ai_Linear__save_comment, mcp__claude_ai_Slack__slack_search_public_and_private
---

# Verify Docs PR

Verify whether the feature described in a docs PR is live in production before the docs get published.

## Inputs

- **PR number** (single mode): `/verify-docs-pr 589`
- **No arg** (sweep mode): runs across all open PRs in `trunk-io/docs2`
- **Auto-invoked from `write-docs`** Phase 4 with the freshly-created PR number

## Verdicts

| Verdict | Meaning |
|---|---|
| `live` | Customers can use the feature. Ready to publish. |
| `staged` | Feature on in staging, off in prod. Re-run after rollout. |
| `pending` | Eng work merged but feature flag still off in prod. Hold. |
| `blocked` | Eng PR is not merged or has been reverted. Hold. |
| `unknown` | Could not determine state from available signals. Manual check needed. |

## Workflow

### Phase 0: Resolve scope

1. If a single PR number is provided, scope = that one PR.
2. Otherwise, list all open PRs:
   ```
   gh pr list --repo trunk-io/docs2 --state open --limit 100 --json number,title,isDraft,headRefName
   ```
3. If scope > 13 PRs, dispatch parallel sub-agents in chunks of ~13 PRs each. See "Sweep parallelization" below.

### Phase 1: Per-PR check

For each docs PR in scope, run all five steps (A-E).

#### Step A: Parse PR body

1. Fetch PR data:
   ```
   gh pr view <NUM> --repo trunk-io/docs2 --json body,headRefName,isDraft,state,comments
   ```
2. If `state` is `MERGED` or `CLOSED`, print `PR #<NUM> already <state>; skipping` and move to the next PR.
3. From the body, extract:
   - **Eng PR refs**: match `trunk-io/(\w+)#(\d+)` and `https://github\.com/trunk-io/(\w+)/pull/(\d+)`
   - **Linear ticket IDs**: match `TRUNK-\d+`
4. If no eng PR refs were found:
   - Use `mcp__claude_ai_Linear__get_issue` for each Linear ticket ID
   - Read its `relations` for related engineering tickets
   - For each related eng ticket, look up its linked PRs via the same Linear MCP call

#### Step B: Check eng PR state

For each engineering PR reference:

5. Fetch state:
   ```
   gh pr view <num> --repo trunk-io/<repo> --json state,mergedAt,mergeCommit,files,body
   ```
6. If `state` is `OPEN` or `CLOSED` (not merged): tag this ref `blocked`. Skip to Step E.
7. If `state` is `MERGED`: continue. Verify the merge commit is still part of `main`:
   ```
   gh api repos/trunk-io/<repo>/compare/main...<mergeCommit.oid> --jq '.status'
   ```
   If the status is `identical` or `behind`, the merge commit is on main and the merge is intact. If `diverged`, the merge has been reverted. Tag the ref `blocked` with note "merged then reverted".

#### Step C: Find feature flags

For each merged eng PR:

8. Read the PR body for explicit flag mentions. Patterns:
   - Backticks adjacent to "flag" (e.g., `` gated behind the `enableFilteredUploadsPage` LaunchDarkly flag ``)
   - camelCase identifiers starting with `enable`, `show`, `use`
9. Pull the diff:
   ```
   gh pr diff <num> --repo trunk-io/<repo>
   ```
   Grep for:
   - `flags.ts` references
   - Strings inside `useFeatureFlag(...)` and `useFlag(...)` calls
   - LaunchDarkly URLs (e.g., `app.launchdarkly.com/projects/.../flags/<name>/`)
10. Collect unique flag names. If none found, set `flag=none` and proceed to Step E.

#### Step D: Gather rollout signals (per flag)

For each detected flag `<flag>`:

11. **Follow-up PRs in trunk2:**
    ```
    gh search prs --repo trunk-io/trunk2 "\"<flag>\"" --limit 30 --json number,title,state,createdAt,closedAt,url
    ```
    Note: the literal quotes around the flag name force exact-phrase matching. Without them, common substrings like `enable` or `show` would return unrelated PRs and bias the rollout signal count.

    Filter to PRs whose `createdAt` is after the original eng PR's `mergedAt`. Look in titles for keywords: "rollout", "100%", "delete legacy", "remove flag", "ramp up".

12. **Slack search:**
    Use `mcp__claude_ai_Slack__slack_search_public_and_private` with:
    - Query: `<flag>`
    - Sort: `timestamp` (newest first)
    - Look for messages from the LaunchDarkly bot, eng confirmations of flag state, rollout dates
    - Recommended channels to scan in results: `#eng`, `#team-flaky-tests`, `#team-merge-queue`, `#production-notifications`, `#staging-notifications`
    
    A 0-result Slack search is itself a signal. It counts toward `pending`.

13. **e2e flag default:**
    ```
    gh api repos/trunk-io/trunk2/contents/ts/apps/e2e/flags.json --jq '.content' | base64 -d | jq '.flagValues["<flag>"]'
    ```
    A `true` here only confirms it works in tests, not prod.

14. **Legacy code presence:**
    Eng PR bodies often mention a legacy component being preserved (e.g., "When the flag is off, the legacy `<UploadsClient>` renders unchanged"). Extract the legacy name from the eng PR body (regex: `legacy \x60(\w+)\x60` and similar) and search trunk2:
    ```
    gh api 'search/code?q=<legacy-name>+repo:trunk-io/trunk2' --jq '.items[].path'
    ```
    Presence of the legacy code path in `main` = flag not yet 100% rolled out.

#### Step E: Classify

Apply rules in order. First match wins.

| Condition | Verdict |
|---|---|
| Any referenced eng PR is unmerged or reverted | `blocked` |
| Eng PR state itself was unavailable after retry (state unknown) | `unknown` |
| All eng PRs merged AND no flag found | `live` |
| Slack message confirms flag at 100% prod, OR a follow-up "delete legacy" PR is merged | `live` |
| Slack message dated AFTER the eng PR's `mergedAt` confirms flag on in staging, off in prod | `staged` |
| Eng PR merged, flag exists, no Slack rollout signals, legacy code still present | `pending` |
| Eng PR merged, flag exists, mixed or insufficient signals | `unknown` |

**Recency rule.** Slack messages from before the eng PR's `mergedAt` describe a state the eng PR may have changed. Treat pre-merge messages as background context only, not as current-state signals. A Slack message must be timestamped after `mergedAt` to count as a positive `live` or `staged` signal.

### Phase 2: Output

For each PR with a verdict:

15. **Console output.**
    - Single mode: print full reasoning (eng work, flag, signals checked, suggested next action).
    - Sweep mode: one line per PR, sorted by severity (`blocked` → `pending` → `staged` → `unknown` → `live`). End with a summary line.

16. **PR comment.**
    Body template (replace `<...>` placeholders):
    ```
    <!-- verify-docs-pr -->
    **Verification status (<DATE>): `<verdict>`**

    <verdict-opening-line, see "Verdict messages" below>

    - Eng PR: <links>
    - Flag: `<flag-name>` (or "none" if ungated)
    - Signals: <bulleted list of rollout signals checked>

    <suggested next action>
    ```
    Check for an existing `<!-- verify-docs-pr -->` comment in the PR's `comments` array. If present, edit it via `gh api` (`PATCH /repos/.../issues/comments/<id>` with the new body). Otherwise post a new comment via `gh pr comment <num> --body "<body>" --repo trunk-io/docs2`.

    Do not use em dashes (U+2014) in the comment body. Use periods, commas, or parentheses instead.

17. **Linear comment.**
    Find the linked Linear ticket from the docs PR body. Use `mcp__claude_ai_Linear__list_comments` with the issue ID to find any existing `<!-- verify-docs-pr -->` comment.
    - If present, update via `mcp__claude_ai_Linear__save_comment` with the comment ID.
    - Otherwise create a new comment with `mcp__claude_ai_Linear__save_comment`.
    
    Body template:
    ```
    <!-- verify-docs-pr -->
    Verification status (<DATE>): `<verdict>`

    Docs PR: https://github.com/trunk-io/docs2/pull/<NUM>

    <same body as PR comment, minus the marker>
    ```

    Do not use em dashes (U+2014) in the comment body. Use periods, commas, or parentheses instead.

18. **PR state action.**

    **Draft flag.**
    - `live`: no draft change.
    - Anything else: if `isDraft` is `false`, flip to draft via `gh pr ready <num> --undo --repo trunk-io/docs2`. If already draft, no-op.

    **Title prefix.** Adds a visible queue signal so anyone scanning open PRs can see the verdict without opening the PR. `live` PRs get a positive cue, non-`live` PRs get a hold cue.

    Known prefixes managed by this skill: `[ready to merge]`, `[staged]`, `[feature not live]`, `[blocked]`. Treat them as case-sensitive and bracket-anchored.

    Per verdict:

    | Verdict | Title prefix |
    |---|---|
    | `live` | `[ready to merge]` |
    | `staged` | `[staged]` |
    | `pending` | `[feature not live]` |
    | `blocked` | `[blocked]` |
    | `unknown` | none (the verdict is already non-actionable; an extra prefix would be noise) |

    Algorithm:
    1. Read the current title from the PR data fetched in Step A.
    2. Strip any leading known prefix to derive the base title. Match the regex `^\[(ready to merge|staged|feature not live|blocked)\] ` (anchored, single trailing space).
    3. Compose the new title: if the verdict has a prefix, `<prefix> <base>`; otherwise just `<base>`.
    4. If the new title differs from the current title, update via:
       ```
       gh pr edit <num> --repo trunk-io/docs2 --title "<new title>"
       ```
       If they match, no-op.

    This keeps the title in sync with the verdict on every run. The prefix lifecycle is fully automatic in both directions: a PR that was `pending` and flips to `live` swaps `[feature not live]` for `[ready to merge]`; a PR whose eng work gets reverted swaps `[ready to merge]` for `[blocked]`.

    Do not stack prefixes. If you ever see a title with multiple known prefixes (e.g., a manual edit that added `[blocked][staged]`), treat the leftmost match as the only one to strip and let the next verification settle the rest.

## Verdict messages

Per verdict, use this opening line in the comment body:

| Verdict | Opening line |
|---|---|
| `live` | "Verified: customers can use this. Ready to publish." |
| `staged` | "On in staging only. Re-run after prod rollout." |
| `pending` | "Eng merged but flag off in prod. Hold off." |
| `blocked` | "Eng PR not merged. Hold." |
| `unknown` | "Could not determine state from available signals. Manual check needed." |

## Sweep parallelization

When scope > 13 PRs:

1. Split the PR list into chunks of up to 13 each (4 chunks for 41 PRs).
2. For each chunk, dispatch a sub-agent. Brief the agent to run Phase 1 and Phase 2 for each PR in its chunk and return a structured result: `{pr, verdict, summary_line, comment_posted, linear_updated}`.
3. Run all agents concurrently.
4. Collect results. If an agent fails, list its PRs as "unverified" and suggest re-running them individually with `/verify-docs-pr <num>`.
5. Sort the combined results by severity and print the summary table.

## Edge cases

- **PR has no eng refs and no Linear ticket:** verdict = `unknown`. Comment lists what's missing.
- **Eng PR is in a non-trunk2 repo (e.g., analytics-cli, flake-farm):** treat the merge state check the same way. Skip flag detection (only trunk2 has the LD flag patterns).
- **Multiple flags from the same eng PR:** gather signals for all; classify on the most conservative result.
- **Multiple eng PRs with mixed states:** `blocked` wins if any is unmerged.
- **Stacked merges:** If the merged eng PR's body mentions "stacked PRs", "Trunk Merge Queue", or lists multiple `trunk-io/<repo>#NNN` references in its body, recursively run Step C (find feature flags) on each child PR. The merge commit's flat diff may not surface flag definitions added in earlier child PRs of the stack. Real-world example: trunk2#3583 (Test Collections) merged children #3545-#3550 and the docs PR for it (docs#554) was incorrectly classified as `live` because the child PR contents weren't inspected.
- **API timeouts (`gh` or Slack):** retry once. On second failure, set verdict = `unknown` with a note about the unavailable signal.
- **PR already merged:** print "PR #N already merged; skipping" and skip entirely. Do not comment.
- **Docs PR body has no `TRUNK-XXX` reference:** The skill cannot find the linked Linear ticket reliably. Print a warning ("No Linear ticket found in PR body; skipping Linear comment") and proceed without posting to Linear. Do NOT guess at which ticket to post to.

## Manual validation cases

When changes ship to this skill, verify all six cases pass:

1. `/verify-docs-pr 589` → verdict `pending`, references `enableFilteredUploadsPage`.
2. `/verify-docs-pr 534` → verdict `live` (no flag found).
3. `/verify-docs-pr 522` → verdict `live` (pure docs change, no eng PR found).
4. `/verify-docs-pr` → all open PRs classified, summary printed sorted by severity.
5. Run `/verify-docs-pr 589` twice → existing comment is edited, no duplicate posted.
6. Title prefix lifecycle: run on a `pending` PR with no prefix → title gets `[feature not live]` prepended. Re-run with the verdict still `pending` → no further change. Simulate the verdict flipping to `live` → `[feature not live]` is replaced with `[ready to merge]`. Simulate the eng PR being reverted (verdict flips to `blocked`) → `[ready to merge]` is replaced with `[blocked]`.
