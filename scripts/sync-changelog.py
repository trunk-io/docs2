#!/usr/bin/env python3
"""Sync the changelog navigation across the four sites it lives on.

The single source of truth is the frontmatter of each `changelog/*.mdx` entry:

    title:       Quoted, "Product: Title" format
    description: Quoted, one-sentence summary used in the <Update> body
    date:        Unquoted ISO date (YYYY-MM-DD)
    category:    Unquoted product name — Merge Queue / Flaky Tests / Code Quality
                 / CI Autopilot / Web App
    type:        Optional. "new-feature" or "update". Not used in nav rendering.

This script rewrites four files from those entries:

    1. docs.json
       Surgically replaces the `Changelog` tab's year-group `pages` arrays.
       Newest entries first.

    2. changelog/index.mdx
       Master index page with the tag-filter UI. One <Update> block per entry,
       grouped by `## YYYY` and `### Month YYYY`. Newest first.

    3. merge-queue/changelog.mdx
       Product-page index. Same shape as the master, but filtered to
       `category: Merge Queue`.

    4. flaky-tests/changelog.mdx
       Same as above, filtered to `category: Flaky Tests`.

Categories without a product-page index (Code Quality, CI Autopilot, Web App)
still appear in docs.json and the master index but get no product-page entry.

Usage:
    python3 scripts/sync-changelog.py            apply changes in place
    python3 scripts/sync-changelog.py --check    exit 1 if any file would change
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_DIR = REPO_ROOT / "changelog"
DOCS_JSON = REPO_ROOT / "docs.json"
MASTER_INDEX = CHANGELOG_DIR / "index.mdx"
PRODUCT_PAGES = {
    "Merge Queue": REPO_ROOT / "merge-queue" / "changelog.mdx",
    "Flaky Tests": REPO_ROOT / "flaky-tests" / "changelog.mdx",
}

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def parse_frontmatter(path: Path) -> dict | None:
    """Read YAML frontmatter from an MDX file. Returns None for files that
    don't open with a `---` frontmatter delimiter (e.g., the index file)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        out[key] = value
    return out


def load_entries() -> list[dict]:
    """Read every entry under changelog/, drop the index, return sorted (newest first)."""
    entries = []
    for mdx in sorted(CHANGELOG_DIR.glob("*.mdx")):
        if mdx.name == "index.mdx":
            continue
        fm = parse_frontmatter(mdx)
        if not fm:
            raise SystemExit(f"FATAL: {mdx} has no readable frontmatter")
        required = ("title", "description", "date", "category")
        missing = [k for k in required if k not in fm]
        if missing:
            raise SystemExit(f"FATAL: {mdx} missing required frontmatter: {missing}")
        try:
            dt = date.fromisoformat(fm["date"])
        except ValueError:
            raise SystemExit(f"FATAL: {mdx} has unparseable date: {fm['date']!r}")
        entries.append(
            {
                "slug": mdx.stem,
                "title": fm["title"],
                "description": fm["description"],
                "date": dt,
                "category": fm["category"],
                "path": f"changelog/{mdx.stem}",
            }
        )
    # Newest first. Stable order within a day: filename (slug) alphabetical.
    entries.sort(key=lambda e: (-e["date"].toordinal(), e["slug"]))
    return entries


def label_for(dt: date) -> str:
    """Render the date as `Month D, YYYY` for the <Update label="..."> attribute."""
    return f"{MONTHS[dt.month - 1]} {dt.day}, {dt.year}"


def render_update_block(entry: dict) -> str:
    """Render a single <Update> block. Indentation matches existing files (2 spaces)."""
    return (
        f'<Update label="{label_for(entry["date"])}" tags={{["{entry["category"]}"]}}>\n'
        f'  **[{entry["title"]}](/{entry["path"]})**\n'
        f"\n"
        f"  {entry['description']}\n"
        f"</Update>\n"
    )


def render_mdx_body(entries: list[dict]) -> str:
    """Render the year/month-grouped body of an index .mdx file.
    Caller is responsible for the frontmatter."""
    lines: list[str] = []

    # Group by year, then by month within each year.
    by_year: dict[int, list[dict]] = {}
    for e in entries:
        by_year.setdefault(e["date"].year, []).append(e)

    years_sorted = sorted(by_year.keys(), reverse=True)
    for i, year in enumerate(years_sorted):
        if i > 0:
            lines.append("")
        lines.append("")
        lines.append(f"## {year}")
        lines.append("")

        by_month: dict[int, list[dict]] = {}
        for e in by_year[year]:
            by_month.setdefault(e["date"].month, []).append(e)
        months_sorted = sorted(by_month.keys(), reverse=True)
        for j, month in enumerate(months_sorted):
            if j > 0:
                lines.append("")
            lines.append(f"### {MONTHS[month - 1]} {year}")
            lines.append("")
            month_entries = by_month[month]
            for k, e in enumerate(month_entries):
                lines.append(render_update_block(e).rstrip())
                if k < len(month_entries) - 1:
                    lines.append("")
    lines.append("")
    return "\n".join(lines)


def render_mdx_file(entries: list[dict], frontmatter: str) -> str:
    """Compose the full .mdx file: frontmatter + autogen body."""
    return frontmatter + render_mdx_body(entries)


def extract_existing_frontmatter(path: Path) -> str:
    """Return the literal `---\\n...\\n---\\n` frontmatter from an existing file,
    so the script preserves it byte-for-byte (title, description, rss flag, etc.)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit(f"FATAL: {path} missing frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise SystemExit(f"FATAL: {path} frontmatter not closed")
    return text[: end + len("\n---\n")]


def render_docs_json(entries: list[dict]) -> str:
    """Surgically rewrite the Changelog tab's year-group pages.
    Round-trips through json with indent=2 and a trailing newline."""
    doc = json.loads(DOCS_JSON.read_text(encoding="utf-8"))
    tabs = doc.get("navigation", {}).get("tabs", [])
    changelog_tab = next(
        (t for t in tabs if isinstance(t, dict) and t.get("tab") == "Changelog"), None
    )
    if changelog_tab is None:
        raise SystemExit("FATAL: docs.json has no Changelog tab")

    # Bucket entries by year, then by month within each year.
    by_year: dict[int, dict[int, list[dict]]] = {}
    for e in entries:
        by_year.setdefault(e["date"].year, {}).setdefault(e["date"].month, []).append(e)

    # Preserve the leading "changelog/index" entry and rebuild the nav as
    # year -> month -> entries, newest first, so the sidebar is parseable by
    # both year and month. Month labels are unqualified (e.g. "June") since the
    # parent group already carries the year.
    new_pages: list = ["changelog/index"]
    for year in sorted(by_year.keys(), reverse=True):
        month_groups: list = []
        for month in sorted(by_year[year].keys(), reverse=True):
            month_groups.append(
                {
                    "group": MONTHS[month - 1],
                    "pages": [e["path"] for e in by_year[year][month]],
                }
            )
        new_pages.append(
            {
                "group": str(year),
                "pages": month_groups,
            }
        )
    changelog_tab["pages"] = new_pages

    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def maybe_write(
    path: Path, new_text: str, check_only: bool, *, semantic_json: bool = False
) -> bool:
    """Compare desired content against current. Return True if a change is/would-be made.

    With semantic_json=True, compare parsed JSON instead of raw text: prettier owns
    docs.json's formatting (e.g. it collapses short arrays onto one line), so a
    byte-for-byte comparison against json.dumps output would report perpetual drift."""
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if current == new_text:
        return False
    if semantic_json and current:
        try:
            if json.loads(current) == json.loads(new_text):
                return False
        except json.JSONDecodeError:
            pass
    if check_only:
        print(f"DRIFT: {path.relative_to(REPO_ROOT)}")
        return True
    path.write_text(new_text, encoding="utf-8")
    print(f"wrote: {path.relative_to(REPO_ROOT)}")
    return True


def main() -> int:
    check_only = "--check" in sys.argv[1:]

    entries = load_entries()

    drift = False

    # 1. docs.json
    drift |= maybe_write(
        DOCS_JSON, render_docs_json(entries), check_only, semantic_json=True
    )

    # 2. changelog/index.mdx (all entries)
    fm = extract_existing_frontmatter(MASTER_INDEX)
    drift |= maybe_write(MASTER_INDEX, render_mdx_file(entries, fm), check_only)

    # 3 & 4. product-page indexes (filtered)
    for category, path in PRODUCT_PAGES.items():
        filtered = [e for e in entries if e["category"] == category]
        fm = extract_existing_frontmatter(path)
        drift |= maybe_write(path, render_mdx_file(filtered, fm), check_only)

    counts = {}
    for e in entries:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
    print()
    print(f"Total entries: {len(entries)}")
    for cat in sorted(counts):
        in_product = " (rendered to product page)" if cat in PRODUCT_PAGES else ""
        print(f"  {cat}: {counts[cat]}{in_product}")

    if check_only and drift:
        print(
            "\nERROR: changelog nav is out of sync. Run `python3 scripts/sync-changelog.py`."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
