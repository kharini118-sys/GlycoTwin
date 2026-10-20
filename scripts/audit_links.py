"""
scripts/audit_links.py
Full audit of all internal Markdown links in the GlycoTwin project.

Prints every broken link with file, line number, link text, target, and
the resolved path that does not exist. External URLs and pure anchors are skipped.

Exit code: 1 if any broken links; 0 if all links are valid.

Usage:
    python scripts/audit_links.py
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Collect every .md file except inside .venv / .pytest_cache
MD_FILES = [
    p for p in PROJECT_ROOT.rglob("*.md")
    if ".venv" not in p.parts and ".pytest_cache" not in p.parts
]

# Regex: captures link text and target from [text](target) or [text](target#anchor)
LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)\n]+)\)')

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "//")

broken = []   # (source_path, line_no, text, raw_target, resolved_path)
ok_count = 0

for md in sorted(MD_FILES):
    try:
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        print(f"WARN: cannot read {md}: {e}")
        continue

    for lineno, line in enumerate(lines, 1):
        for m in LINK_RE.finditer(line):
            text = m.group(1)
            raw = m.group(2).strip()

            # Strip inline anchor and title
            target = raw.split("#")[0].strip()
            # Strip optional link title  e.g.  path "title"
            target = target.split('"')[0].strip()
            target = target.split("'")[0].strip()

            # Skip pure anchors and external URLs
            if not target:
                continue
            if any(target.startswith(p) for p in EXTERNAL_PREFIXES):
                continue

            # Resolve relative to the Markdown file's directory
            resolved = (md.parent / target).resolve()
            rel_source = md.relative_to(PROJECT_ROOT)

            if resolved.exists():
                ok_count += 1
            else:
                broken.append((rel_source, lineno, text, target, resolved))

# ── Report ────────────────────────────────────────────────────────────────────
total = ok_count + len(broken)
print(f"\nScanned {len(MD_FILES)} Markdown files — {total} internal links checked.\n")

if broken:
    print(f"BROKEN LINKS: {len(broken)}\n")
    for src, lineno, text, target, resolved in broken:
        print(f"  {src}:{lineno}")
        print(f"    text     : {text!r}")
        print(f"    target   : {target!r}")
        print(f"    resolved : {resolved}")
        print()
    sys.exit(1)
else:
    print(f"OK: All {ok_count} internal links are valid.")
    sys.exit(0)
