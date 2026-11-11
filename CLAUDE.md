# Working in this repo

Mintlify docs site. `docs.json` holds the navigation; content is `.mdx` under
the product directories. Preview locally with `mint dev` (see CONTRIBUTING.md).

## Scripts

### `scripts/embed-nav-icons.py` — navigation icons

Run this after editing any product icon SVG, and commit the regenerated
`docs.json`:

```sh
python3 scripts/embed-nav-icons.py
```

A navigation `icon` **cannot** point at a repo file — neither a group icon in
`docs.json` nor a page's `icon:` frontmatter. Mintlify
rewrites such a path to `/_mintlify/image/<project>/<path>`, which is unsigned,
so CloudFront answers `403 MissingKey`: the sidebar `<img>` loads nothing and
the group header shows a blank gap where the icon belongs. This is specific to
nav icons — anything inside a page, including a `<Card icon="...">`, is
rewritten to a *signed* `mintcdn.com` URL and loads fine, so leave those as
plain paths.

So the icons are inlined into `docs.json` as `data:` URIs, which Mintlify has no
reason to proxy. The SVGs under `assets/icons/` stay the source of truth; the
script regenerates the inlined copies from them. Add a new product icon by
dropping the SVG in `assets/icons/` and adding a `group -> path` entry to the
script's `GROUP_ICONS` map (or `PAGE_ICONS`, for a page's frontmatter icon).

If Mintlify ever signs nav-icon URLs, drop the entry and restore the plain path.
Built-in icon names (`"flask"`, Lucide/Font Awesome) are unaffected by this bug
and can be used instead of a custom SVG at any time.

### `scripts/sync-changelog.py` — changelog navigation

Regenerates the changelog nav across the sites it appears on from each
`changelog/*.mdx` frontmatter. See the script's docstring.

## Conventions

- **Custom SVGs are authored solid black.** `styles.css` inverts them for dark
  mode, so do not add theme variants or use `currentColor` — it resolves to
  black inside an `<img>` and defeats nothing, but the literal color is what the
  stylesheet's comment documents.
- **`<Columns cols={n}>` accepts 1-4.** A larger value is not an error and does
  not fail the build; it just does not render that many across.

## Runners and Workspaces pages

`runners/` and `trunk-workspaces/` used to be generated from
`apps/firewatch/docs` in `trunk-io/trunk-cloud`. That sync is removed, so these
pages are edited here like any other. The `.sync.json` files and the
"Generated in trunk-io/docs2" comments are leftovers of the sync. Runners
pages are public; Workspaces pages stay gated (below).

## API reference

All API pages are in the **API Reference** tab, under `/api`. The tab has two
top-level groups: **Getting started** (`api.mdx`, `api/*.mdx`) and
**Resources**, which nests one collapsed group per v2 OpenAPI tag, then
Webhooks and the **Legacy API** group. Nest new resources inside Resources: a
top-level group renders with a separator, and the resources are meant to read
as one list. The v2 endpoint groups generate their pages from `openapi-v2.json`
into `/api/<tag>/<slug>`, and the legacy group from `openapi.json` into
`/api/v1/<slug>`. In page text, v2 is "the API" and v1 is "the legacy API".
Product guides that use the API, such as `merge-queue/using-the-queue/api`,
stay in their product's tab. The old product URLs redirect to `/api` in
`docs.json`.

## Hidden API pages

The three v2 endpoints that Trunk's analytics-cli and test-runner plugins call
are deliberately **not** in `docs.json`: `POST /v2/test-collections/{id}/uploads`,
`POST /v2/test-collections/{id}/quarantine-status` and
`POST /v2/test-collections/{id}/all-quarantined-tests`. Their shapes follow what
the CLI needs and may change with it, so each has a page reachable only by URL:
a `hidden: true` `.mdx` under `flaky-tests/reference/api-reference/v2-internal/`
that renders the operation from `openapi-v2.json`. When a re-synced spec has
operations no page lists, do not add these three to the sidebar. Their
descriptions in the spec start with "**Internal.**", which marks them.

The legacy Flaky Tests endpoints (`/flaky-tests/*` in `openapi.json`) are
hidden the same way, as `hidden: true` pages under `api/v1/` that keep their
generated `/api/v1/<slug>` URLs, and so are the two Flaky Tests migration
guides (`api/v1/migrate-flaky-tests`,
`flaky-tests/get-started/migrate-to-test-collections`). Don't link them from
other pages or add them back to the sidebar. The exceptions are `api/v1.mdx`'s
link to the Flaky Tests migration guide and the changelog's old links.

## Redirects

- A redirect's `destination` must be a plain `<page>.mdx` (or `/`), never a
  directory page (`<dir>/index.mdx`), in any spelling: `/<dir>`, `/<dir>/` and
  `/<dir>/index` all fail. Mintlify's auth proxy treats such a destination as
  gated and sends a signed-out reader to `app.trunk.io/mintlify-login`, though
  the page itself is public. Signed-in readers are redirected normally, so the
  break shows only when you are signed out. `public: true` does not help.
- To redirect to a directory page, serve it from `<dir>.mdx` beside `<dir>/`:
  the URL stays the same. Relative links resolve against the **file**, so a
  moved file's relative links must change (write them absolute). Do not add a
  `/<dir>/index` → `/<dir>` redirect: Mintlify reads that source as `/<dir>`, so
  the page redirects to itself.
- `python3 scripts/check-redirects.py` enforces this in CI. `--live <url>`
  requests every source signed out; a daily job runs it against docs.trunk.io,
  because a change on Mintlify's side would pass the static check.
- The site root is `/`; there is no `/welcome`.
- A destination inside an OpenAPI `directory` that `docs.json` names (such as
  `/api/v1/...`) is a generated endpoint page with no `.mdx` file. The check
  accepts it without looking for a file.

## Gated sections

Workspaces is restricted per page with `groups:` frontmatter (`["firewatch"]`).
It lives in the **Overview** tab's sidebar rather than in a tab of its own:
Mintlify filters gated *pages* out of the navigation but leaves the emptied tab
behind, so a tab of its own would show the product name to signed-out visitors.
Nested under Overview the shell is an empty group, which does not render, and
the tab still has `index` to stand on. Empty group names do remain in the page's JSON payload — they are not
secret, just not displayed.

A tab marked `"hidden": true` is invisible to everyone, authorized users
included, but its pages stay reachable by URL and still render that tab's own
sidebar. That is how Changelog works.

## Verifying a change

Mintlify's checks pass on things that are visibly broken — an out-of-range prop
or an icon that 403s fails nothing. For anything visual, open the branch's
preview deployment and look at it:

```sh
id=$(gh api repos/trunk-io/docs2/deployments --jq '.[0].id')
gh api repos/trunk-io/docs2/deployments/$id/statuses --jq '.[0].environment_url'
```

The sidebar renders client-side, so curl will not show it. When checking an
image, read its `naturalWidth` — a broken image is present in the DOM and
reports 0.
