# Trunk Documentation

The Mintlify-powered source for [docs.trunk.io](https://docs.trunk.io). Pages live as `.mdx` files under product directories (`flaky-tests/`, `merge-queue/`, `setup-and-administration/`), with site configuration and navigation in `docs.json`. Merging to `main` deploys to production.

## Prerequisites

- Node.js ≥ 19
- The [Mintlify CLI](https://www.npmjs.com/package/mint) (`mint`)

## Local development

Clone and enter the repo:

```
git clone git@github.com:trunk-io/docs2.git
cd docs2
```

Install the CLI globally if you haven't already:

```
npm i -g mint
```

Start the dev server from the repo root (where `docs.json` lives):

```
mint dev
```

Open `http://localhost:3000`. If `:3000` is taken, the CLI auto-picks the next free port. Watch the startup log for the actual URL, or pin one with `mint dev --port 3005`.

### Enabling local search

The search box in `mint dev` proxies to Mintlify's hosted search and needs a CLI login:

```
mint login
```

The site renders fine without authenticating. Only search needs it.

## Useful commands

| Command | Purpose |
| --- | --- |
| `mint dev` | Local preview server |
| `mint validate` | Strict-mode build check; non-zero exit on warnings/errors. Good for CI. |
| `mint broken-links` | Link checker across the docs tree |
| `mint a11y` | Accessibility check |
| `mint status` | Show current auth state |
| `mint login` / `mint logout` | Manage CLI session |
| `mint version` | Show installed CLI version |
| `mint update` | Update the CLI to the latest version |

## Publishing changes

Mintlify's GitHub app watches the default branch, so merging to `main` deploys to production automatically. The app is installed and managed from the [Mintlify dashboard](https://dashboard.mintlify.com/settings/organization/github-app).

## PR labels

PRs in this repo are tagged by automated workflows that verify each doc change against the underlying product state. Labels fall into three groups.

### Feature lifecycle (set by `verify-docs-pr`)

Exactly one of these is applied to every docs PR. They reflect whether customers can actually use the feature being documented.

| Label | Color | Meaning |
|---|---|---|
| `ready to merge` | green | Customers can use this. Ready to publish. |
| `staged` | yellow | On in staging only. Re-run verify after prod rollout. |
| `pending` | orange | Eng merged but flag off in prod. Hold off. |
| `awaiting eng` | red | Eng PR not merged. Hold. |

### Code verification (set by `verify-docs-against-code`)

Applied when the PR's factual claims are checked against trunk-io source. Exactly one is set when verify runs.

| Label | Color | Meaning |
|---|---|---|
| `code-verified` | green | All factual claims confirmed in source. |
| `code-verified-partial` | yellow | Confirmed claims, some unverifiable. |
| `needs eng review` | red | At least one claim contradicts source. |

### Source / review flow

Sticky labels that mark how a PR was sourced or where it needs extra eyes. Additive — a PR can have multiple.

| Label | Color | Meaning |
|---|---|---|
| `changelog` | blue | PR touches the changelog (auto-generated drafts, hosting, formatting, indexing). |
| `needs review` | purple | PR sourced from customer-feedback-mining; needs human scrutiny for accuracy before merge. |

GitHub's default labels (`bug`, `documentation`, `enhancement`, etc.) are also present but not used in our automated workflows.

## Changelog automation

Changelog entries live in `changelog/*.mdx`. Each entry's frontmatter (`title`, `description`, `date`, `category`, `type`) is the single source of truth — the nav sidebar, master index, and product-page indexes are all generated from it.

### Adding a changelog entry

1. Create `changelog/YYYY-MM-DD-<slug>.mdx` with the required frontmatter.
2. Run `python3 scripts/sync-changelog.py` to regenerate the four nav files.
3. Commit both the new entry and the updated nav files.

### CI enforcement

Two GitHub Actions workflows keep things in sync:

- **`changelog-check.yml`** runs on PRs that touch changelog-related files. It calls `sync-changelog.py --check`, which exits non-zero if the nav files don't match what the entries would generate. If this check fails, run the sync script locally and push the result.
- **`changelog-sync.yml`** runs on pushes to `main`. If a changelog entry landed without the nav files being regenerated, the action auto-commits the fix. This is a safety net — the PR check should catch drift before merge.

## Troubleshooting

- **Dev server won't start or behaves oddly:** check `mint version`, then run `mint update` if you're behind.
- **404 on every page:** confirm you're running `mint dev` from the directory containing `docs.json` (the repo root).
- **Search shows "Login into CLI to enable search":** run `mint login`. The rest of the site still works without it.

## AI-assisted writing

Mintlify ships a documentation skill for Claude Code, Cursor, Windsurf, and similar tools:

```
npx skills add https://mintlify.com/docs
```

It includes component reference, writing standards, and workflow guidance.

## Resources

- [Mintlify docs](https://mintlify.com/docs)
- [Mintlify CLI on npm](https://www.npmjs.com/package/mint)
