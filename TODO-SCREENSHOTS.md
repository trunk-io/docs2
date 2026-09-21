# TODO — screenshots needed (Test Collections, Sept 2026)

**Owner: Tyler.** Nothing in this branch is blocked on these — every page renders
correctly today. But six images are now either stale or missing, and the pages
they sit on read thinner without them. Capture against a **`MIGRATION_IN_PROGRESS`
org** unless a row says otherwise, and produce a light and a dark variant for
every one.

---

## Stale — the screenshot no longer matches the product

### 1. Collections list header · `migration-legacy-view-button-{light,dark}.png`

- **Page:** `flaky-tests/get-started/migrate-to-test-collections.mdx` (§ Both views, while you migrate)
- **Why:** the visible **Create Collection** button is gone. The header is now
  `Legacy view` + search + an actions (☰) menu whose one item is
  **Create collection**.
- **Shoot:** the collections list header on an org with at least one collection,
  wide enough to show all three controls. The alt text in the page has already
  been corrected to say "an actions menu" — match it.

### 2. Empty collections state — **new image, no existing file**

- **Page:** `flaky-tests/test-collections.mdx` (§ Create a collection)
- **Why:** an org with zero collections now lands on an inline form headed
  **"Create your first Test Collection"** — no product title, no list, no create
  menu. The docs describe this in prose and show nothing, which is the one screen
  every migrating customer sees first.
- **Shoot:** an org with **no collections at all**, whole viewport.
- **Suggested filename:** `assets/flaky-tests/get-started/first-collection-form-{light,dark}.png`

---

## Missing — new surfaces with no image at all

### 3. Migrate monitors from a repository — **the highest-value one**

- **Page:** `flaky-tests/get-started/migrate-to-test-collections.mdx`
  (§ Bring your repository monitors across)
- **Why:** three comparison groups and a field-level diff are hard to picture from
  prose alone, and this is the step that saves a migrating team the most work.
- **Shoot:** `/{orgSlug}/flaky-tests/collections/{shortId}/monitors/migrate`, with
  a repository picked that yields **at least one row in each of the three groups** —
  *Not in this collection*, *Settings differ* (expanded far enough to show the
  repo-vs-collection diff), and *Already in this collection*. The fourth,
  collection-only group visible below if it fits.
- **Also worth a second, smaller shot:** the **Migrate from a repository** callout
  on the Monitors tab, which is how anyone finds the page.
- **Suggested filename:** `assets/flaky-tests/get-started/migrate-monitors-{light,dark}.png`

### 4. "Copy from a repo" in the ticketing picker

- **Page:** `flaky-tests/get-started/migrate-to-test-collections.mdx`
  (§ Bring a ticketing connection across)
- **Shoot:** **Settings → Organization → Ticketing**, add-connection picker open,
  showing **Copy from a repo** beside the three providers. Ideally then the dialog
  itself, with one row disabled as already-copied — that refusal is the part people
  hit and don't understand.
- **Suggested filename:** `assets/flaky-tests/management/ticketing/copy-from-repo-{light,dark}.png`

### 5. Five-step setup checklist

- **Page:** `flaky-tests/test-collections.mdx` (§ Finish setting up a collection)
- **Why:** the step count changed from four to five and the page has never had an
  image of the checklist.
- **Shoot:** the checklist on a collection's **Settings** tab with **Review
  ticketing** outstanding, so the reader sees `4 of 5 complete` and the fifth row.
- **Suggested filename:** `assets/flaky-tests/get-started/collection-setup-checklist-{light,dark}.png`

### 6. Seeded monitors on a brand-new collection

- **Page:** `flaky-tests/test-collections.mdx` (§ What a new collection starts with)
- **Why:** the new table lists five monitors; an image of the Monitors tab as it
  actually arrives would confirm the reader is looking at defaults, not at
  something a teammate configured.
- **Shoot:** the **Monitors** tab of a collection created minutes ago and never
  edited.
- **Suggested filename:** `assets/flaky-tests/get-started/seeded-monitors-{light,dark}.png`
- **Lowest priority of the six** — the table carries the information; this is
  reassurance.

---

## Not needed

- Collection Overview, collections list rows, quarantining settings, and the
  ticketing provider forms are all still accurate. Don't re-shoot them.

## Delete this file once the six are in.
