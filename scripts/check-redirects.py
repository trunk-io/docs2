#!/usr/bin/env python3
"""Check that every docs.json redirect lands on a page a signed-out reader can open.

See "Redirects" in CLAUDE.md for why a destination cannot be a directory page.

    python3 scripts/check-redirects.py            exit 1 if a destination is not a <page>.mdx
    python3 scripts/check-redirects.py --live URL exit 1 if URL sends a source to login
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_JSON = ROOT / "docs.json"
LOGIN_PATHS = ("app.trunk.io/mintlify-login", "app.mintlify.com/api/end-user-auth")


def page_exists(path: str) -> bool:
    return (ROOT / f"{path}.mdx").is_file()


def gated(path: str) -> bool:
    page = ROOT / f"{path}.mdx"
    if not page.is_file():
        page = ROOT / f"{path}/index.mdx"
    return page.is_file() and re.search(r"^groups:", page.read_text(), re.M) is not None


def destination_problem(destination: str) -> str | None:
    if destination == "/":
        return None
    if not destination.startswith("/"):
        return "is not a site path"
    path = destination.lstrip("/")
    if ":" in path:
        prefix = path.split("/:", 1)[0]
        if not any((ROOT / prefix).glob("**/*.mdx")):
            return f"is a wildcard over {prefix}/, which holds no pages"
        return None
    if page_exists(path):
        return None
    if page_exists(f"{path}/index"):
        return f"is a directory page; serve it from {path}.mdx"
    if path.endswith("/index") and page_exists(path):
        return f"is a directory page; serve it from {path[: -len('/index')]}.mdx"
    return "names no page"


def check(redirects: list[dict[str, str]]) -> int:
    problems = [
        (r["source"], r["destination"], problem)
        for r in redirects
        if (problem := destination_problem(r["destination"]))
    ]
    problems += [
        (r["source"], r["destination"], "redirects to itself; Mintlify drops /index")
        for r in redirects
        if r["source"].removesuffix("/index") == r["destination"]
    ]
    for source, destination, problem in problems:
        print(f"{source} -> {destination}: {problem}")
    if problems:
        print(
            f"\n{len(problems)} redirect(s) send signed-out readers to login. "
            "See \"Redirects\" in CLAUDE.md.",
            file=sys.stderr,
        )
        return 1
    return 0


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def live(base: str, redirects: list[dict[str, str]]) -> int:
    opener = urllib.request.build_opener(NoRedirect)
    sources = [
        r["source"]
        for r in redirects
        if ":" not in r["source"] and not gated(r["destination"].lstrip("/"))
    ]

    def probe(source: str) -> tuple[str, str | None]:
        url = f"{base.rstrip('/')}{source}?redirect-check=1"
        try:
            with opener.open(url, timeout=30) as response:
                return source, response.headers.get("Location")
        except urllib.error.HTTPError as error:
            return source, error.headers.get("Location")

    with ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(probe, sources))
    bounced = [s for s, location in results if location and any(p in location for p in LOGIN_PATHS)]
    for source in bounced:
        print(f"{source}: sent to login")
    print(f"{len(bounced)} of {len(sources)} redirect sources sent to login.")
    return 1 if bounced else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--live", metavar="URL")
    args = parser.parse_args()
    redirects = json.loads(DOCS_JSON.read_text())["redirects"]
    if args.live:
        return live(args.live, redirects)
    return check(redirects)


if __name__ == "__main__":
    sys.exit(main())
