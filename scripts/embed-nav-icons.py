#!/usr/bin/env python3
"""Inline the custom navigation icons in docs.json as data URIs.

Mintlify rewrites a nav `icon` that points at a repo file (e.g.
`/assets/icons/product-ci.svg`) to `/_mintlify/image/<project>/<path>`,
and that proxy URL is unsigned: CloudFront answers 403 MissingKey, so the
`<img class="sidebar-group-icon">` never loads and the group header shows
its label with a blank space where the icon belongs. Page images are fine
— those are rewritten to *signed* mintcdn.com URLs — the bug is specific
to nav icons.

The workaround is to give Mintlify an icon it has no reason to proxy: a
`data:` URI. These icons are ~1-2 KB, so the inlined cost is trivial.

The SVGs under assets/icons/ stay the source of truth. Edit one, re-run
this script, and commit the regenerated docs.json:

    python3 scripts/embed-nav-icons.py

Drop an entry from ICONS (and restore the plain path in docs.json) if
Mintlify ever signs nav-icon URLs properly.
"""

import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_JSON = ROOT / "docs.json"

# Nav group -> the SVG whose contents that group's icon should carry.
ICONS = {
    "Merge Queue": "assets/icons/product-merge-queue.svg",
    "Flaky Tests": "assets/icons/product-flaky-tests.svg",
    "CI": "assets/icons/product-ci.svg",
}


def data_uri(svg_path: pathlib.Path) -> str:
    encoded = base64.b64encode(svg_path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def main() -> None:
    docs = json.loads(DOCS_JSON.read_text())
    raw = DOCS_JSON.read_text()

    for group, rel_path in ICONS.items():
        uri = data_uri(ROOT / rel_path)
        found = False
        for tab in docs["navigation"]["tabs"]:
            for nav_group in tab.get("groups", []):
                if nav_group.get("group") == group and "icon" in nav_group:
                    # Rewrite in the raw text so the rest of docs.json keeps
                    # its hand-authored key order and formatting.
                    raw = re.sub(
                        r'("group": "%s",(?:.|\n)*?"icon": )"[^"]*"' % re.escape(group),
                        lambda m: m.group(1) + json.dumps(uri),
                        raw,
                        count=1,
                    )
                    found = True
        if not found:
            raise SystemExit(f'no nav group named "{group}" carries an icon')

    DOCS_JSON.write_text(raw)
    json.loads(raw)  # fail loudly rather than commit invalid JSON
    print(f"inlined {len(ICONS)} nav icons into docs.json")


if __name__ == "__main__":
    main()
