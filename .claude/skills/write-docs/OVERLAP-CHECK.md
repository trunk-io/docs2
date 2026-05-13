# Duplicate & Overlap Check

Run these checks before starting any work. Stop and ask the user if any match is found.

## Step 1: Check for existing PRs/branches from this draft

1. Derive the expected branch topic from the draft filename (e.g., `flag-as-flaky.md` -> `flag-as-flaky`). Get the username prefix from `git config user.name` (kebab-cased).

2. Search for open PRs matching the branch:
   ```bash
   gh pr list --repo trunk-io/docs2 --state open --head "<username>/<topic>" --json number,title,url,headRefName
   ```
   Also search by topic keyword:
   ```bash
   gh pr list --repo trunk-io/docs2 --state open --json number,title,url,headRefName | jq '.[] | select(.headRefName | contains("<topic>"))'
   ```

3. Check local branches:
   ```bash
   git branch --list "*<topic>*"
   ```

4. **If a match is found**: Show the user the existing PR/branch and ask:
   - (a) Update the existing PR
   - (b) Close it and start fresh
   - (c) Skip this draft

   Do NOT proceed until the user responds.

## Step 2: Check for overlapping PRs from other authors

1. Read the draft to identify target docs files/product area.

2. List all open PRs:
   ```bash
   gh pr list --repo trunk-io/docs2 --state open --json number,title,headRefName,url --limit 50
   ```

3. For any PR that looks related (by title or branch name matching the same product area), check file overlap:
   ```bash
   gh pr view <number> --repo trunk-io/docs2 --json files --jq '[.files[].path]'
   ```

4. **If overlapping PRs are found**: Show the user the overlapping PR and affected files, then ask:
   - (a) Proceed anyway (changes will likely conflict)
   - (b) Wait for that PR to merge first
   - (c) Skip this draft

   Do NOT proceed until the user responds.

5. **If no overlaps found**: Continue to Step 3.

## Step 3: Check for existing Linear tickets

Automation (the daily DevRel scanner, the `/changelog` skill, others) may have already filed a planning ticket for this feature. Find it before creating a duplicate.

1. Extract feature keywords from the draft — topic name, product area, and any `TRUNK-NNNNN` refs already in the notes file.

2. **If the draft already references a `TRUNK-NNNNN` ticket**: fetch it directly via `mcp__claude_ai_Linear__get_issue` to confirm it's the right one and capture its current state. Proceed to Phase 1.

3. **Otherwise, search Linear** for matching tickets:
   - Tool: `mcp__claude_ai_Linear__list_issues`
   - Team ID: `16f26d2e-3c38-4c56-869d-9fea8f33321e` (Trunk Engineering)
   - Filter by feature keywords; look for ticket titles or descriptions mentioning the same feature name, product area, or carrying a `changelog` / `docs` label

4. **If matching tickets are found**: show the user the ticket links and titles, then ask:
   - (a) Link the new docs PR to this ticket and pull its context into the draft (no new ticket)
   - (b) Create a new ticket anyway and document why (rare — usually only if the existing ticket is closed or scoped to something unrelated)
   - (c) Skip this draft (someone else owns the planning)

   Do NOT proceed until the user responds.

5. **If no matching tickets are found**: continue to Phase 1. A new Linear ticket will be created in Phase 5 of `/write-docs`.
