#!/usr/bin/env python3
"""Docs lint: deterministic structural checks for Trunk docs (.mdx).

Three rules, all whole-repo blocking gates:

  1. Broken asset reference — an image referenced from an .mdx file
     (`src="/assets/..."` or `![](/assets/...)`) that does not exist on disk.
  2. Unbalanced <Frame> tags — an .mdx file with a different number of
     `<Frame` and `</Frame>` tags.
  3. Nav separator format — between two **bold** UI labels the separator must
     be exactly " -> " written as the arrow U+2192 with one space each side
     (e.g. `**Settings** -> **Repositories**`). This enforces only the
     deterministic *format* half of the CONTRIBUTING.md navigation standard.
     It never judges whether a click-path is *correct* against the live UI.

Run from the repo root:  python3 scripts/check-docs.py
Exits 0 when clean, 1 when any violation is found.
"""

import os
import re
import sys
from glob import glob

# Skip generated / vendored / working trees. In CI these don't exist, but this
# keeps local runs from scanning other worktrees under .claude/.
SKIP_DIRS = (".claude/", "node_modules/")

IMG_EXT = r"(?:png|jpe?g|gif|svg|webp|avif)"
# Root-absolute image references only (the docs2 convention). External http(s)
# URLs and bare relative paths are left alone.
SRC_REF = re.compile(rf'src="(/[^"]+\.{IMG_EXT})"')
MD_REF = re.compile(rf'!\[[^\]]*\]\((/[^)\s]+\.{IMG_EXT})\)')

# A nav separator sitting between two bold labels. The bold-on-both-sides
# requirement is what keeps this off prose ">", "CI/CD", file paths, version
# ranges, and "read more ->" link affordances.
NAV_SEP = re.compile(r"\*\*[^*\n]+?\*\*( *(?:->|»|‹|›|→|>) *)\*\*[^*\n]+?\*\*")
CANONICAL = " → "  # space, U+2192 arrow, space


def mdx_files():
    for path in sorted(glob("**/*.mdx", recursive=True)):
        if any(seg in path for seg in SKIP_DIRS):
            continue
        yield path


def lines_with_code_flag(text):
    """Yield (lineno, line, in_fenced_code) for each line of an .mdx file."""
    in_code = False
    for n, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            yield n, line, True  # the fence line itself counts as code
            continue
        yield n, line, in_code


def strip_inline_code(line):
    return re.sub(r"`[^`]*`", "", line)


def check_assets(path, text):
    out = []
    for n, line, in_code in lines_with_code_flag(text):
        if in_code:
            continue
        for m in list(SRC_REF.finditer(line)) + list(MD_REF.finditer(line)):
            ref = m.group(1)
            if not os.path.exists(ref.lstrip("/")):
                out.append((n, f"broken asset reference: {ref}"))
    return out


def check_frames(path, text):
    opens = closes = 0
    for _, line, in_code in lines_with_code_flag(text):
        if in_code:
            continue
        opens += line.count("<Frame")
        closes += line.count("</Frame>")
    if opens != closes:
        return [(0, f"unbalanced <Frame> tags: {opens} opening, {closes} closing")]
    return []


def check_nav(path, text):
    out = []
    for n, line, in_code in lines_with_code_flag(text):
        if in_code or line.lstrip().startswith(">"):
            continue
        for m in NAV_SEP.finditer(strip_inline_code(line)):
            sep = m.group(1)
            if sep != CANONICAL:
                shown = sep.replace("→", "U+2192")
                out.append(
                    (n, f"nav separator must be ' -> ' (U+2192, one space each side); found '{shown}'")
                )
    return out


RULES = (check_assets, check_frames, check_nav)


def main():
    findings = {}
    for path in mdx_files():
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as e:
            findings.setdefault(path, []).append((0, f"could not read file: {e}"))
            continue
        for rule in RULES:
            for lineno, msg in rule(path, text):
                findings.setdefault(path, []).append((lineno, msg))

    if not findings:
        print("Docs lint: clean (0 issues).")
        return 0

    total = sum(len(v) for v in findings.values())
    print(f"Docs lint: {total} issue(s) in {len(findings)} file(s)\n")
    for path in sorted(findings):
        for lineno, msg in sorted(findings[path]):
            loc = f"{path}:{lineno}" if lineno else path
            print(f"  {loc}  {msg}")
    print("\nSee CONTRIBUTING.md for the navigation format standard.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
