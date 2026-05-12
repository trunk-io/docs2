# Trunk Documentation

The Mintlify-powered version of [docs.trunk.io](https://docs.trunk.io). Pages live as `.mdx` files under topic directories (`flaky-tests/`, `merge-queue/`, `setup-and-administration/`), with site configuration in `docs.json`.

## Prerequisites

- Node.js ≥ 19
- The [Mintlify CLI](https://www.npmjs.com/package/mint) (`mint`). Tested with `4.2.559`.

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

Open `http://localhost:3000`. If `:3000` is taken, the CLI auto-picks the next free port — watch the startup log for the actual URL. Pin a specific port with `mint dev --port 3005`.

### Enabling local search

Search in `mint dev` proxies to Mintlify's hosted search service and requires a CLI login:

```
mint login
```

The site itself renders fine without authenticating; only the search box needs it. _(Login flow details — browser vs. terminal, SSO behavior — to be filled in after first successful run.)_

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

Mintlify's GitHub app watches the default branch — merging to `main` deploys to production automatically. The app is installed and managed from the [Mintlify dashboard](https://dashboard.mintlify.com/settings/organization/github-app).

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
