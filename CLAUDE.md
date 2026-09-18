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

## Gated sections

Dynamic CI and Workspaces are restricted per page with `groups:` frontmatter
(`["dynamic-ci"]` / `["firewatch"]`). They live in the **Overview** tab's
sidebar rather than in tabs of their own: Mintlify filters gated *pages* out of
the navigation but leaves the emptied tab behind, so a tab of their own would
show the product name to signed-out visitors. Nested under Overview the shells
are empty groups, which do not render, and the tab still has `index` to stand
on. Empty group names do remain in the page's JSON payload — they are not
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
