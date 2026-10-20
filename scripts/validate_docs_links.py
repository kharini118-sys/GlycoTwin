"""
scripts/validate_docs_links.py
Validates internal documentation links across all Markdown files in the
GlycoTwin project.

Checks performed
----------------
1. Hyperlinks  [text](relative/path)  -- resolved against the file system.
   External URLs (http/https/mailto/ftp) and pure in-page anchors (#id)
   are skipped.
2. Backtick filename references  `path/to/file.ext`  -- when the code span
   looks like a file path (contains '/' and a dot), the exact path is
   resolved and its case verified against the real filesystem entry.  This
   catches wrong-capitalisation bugs that are invisible on Windows but break
   on Linux / GitHub.

Scope
-----
Every *.md file in the project tree excluding .venv and .pytest_cache.

Usage
-----
    python scripts/validate_docs_links.py

Exit codes
----------
    0  -- all links valid
    1  -- at least one broken or wrong-case link found
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# -- Collect all Markdown files -----------------------------------------------
MD_FILES = sorted(
    p for p in PROJECT_ROOT.rglob("*.md")
    if ".venv" not in p.parts and ".pytest_cache" not in p.parts
)

# -- Regex patterns ------------------------------------------------------------
# Hyperlinks: [text](target)  or  [text](target#anchor)
HYPERLINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\n]+)\)")

# Backtick code spans that look like local file paths: `some/path.ext`
# Matches tokens that contain '/' and a dot extension, no spaces.
BACKTICK_PATH_RE = re.compile(r"`([a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+)`")

EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "ftp://", "//")

# Paths that are intentionally absent from a clean checkout (gitignored or
# generated at runtime).  These are valid documentation references and must
# not be flagged as broken.
GITIGNORED_PATHS = {
    "instance/glycotwin.db",       # SQLite DB created at runtime; in .gitignore
    "data/raw/cgmacros/CGMacros/", # Raw dataset; users download separately
}

broken_links = []   # (source_rel, line_no, kind, text, target, resolved)
ok_count = 0


def real_name(path: Path) -> str:
    """Return the actual on-disk filename (exact case) for path.name."""
    try:
        for entry in path.parent.iterdir():
            if entry.name.lower() == path.name.lower():
                return entry.name
    except (PermissionError, OSError):
        pass
    return path.name


def check_hyperlinks(md_path, lines, rel_source):
    global ok_count
    for lineno, line in enumerate(lines, 1):
        for m in HYPERLINK_RE.finditer(line):
            text = m.group(1)
            raw = m.group(2).strip()
            target = raw.split("#")[0].strip()
            if '"' in target:
                target = target[: target.index('"')].strip()
            if "'" in target:
                target = target[: target.index("'")].strip()
            if not target:
                continue
            if any(target.startswith(p) for p in EXTERNAL_PREFIXES):
                continue
            resolved = (md_path.parent / target).resolve()
            if not resolved.exists():
                broken_links.append(
                    (rel_source, lineno, "hyperlink", text, target, resolved)
                )
            else:
                actual = real_name(resolved)
                if actual != resolved.name:
                    broken_links.append((
                        rel_source, lineno, "hyperlink (wrong case)",
                        text, target, resolved.parent / actual,
                    ))
                else:
                    ok_count += 1


def check_backtick_paths(md_path, lines, rel_source):
    """Flag backtick spans that look like project-relative file paths but
    whose path does not exist or has wrong case."""
    global ok_count
    for lineno, line in enumerate(lines, 1):
        for m in BACKTICK_PATH_RE.finditer(line):
            candidate = m.group(1)
            # Only process if there is at least one slash (path-like)
            if "/" not in candidate:
                continue
            if any(candidate.startswith(p) for p in EXTERNAL_PREFIXES):
                continue
            # Skip intentionally-absent runtime/gitignored paths
            if any(candidate == p or candidate.startswith(p) for p in GITIGNORED_PATHS):
                continue
            # Try project-root-relative first, then file-directory-relative
            resolved = (PROJECT_ROOT / candidate).resolve()
            if not resolved.exists():
                resolved = (md_path.parent / candidate).resolve()
                if not resolved.exists():
                    broken_links.append((
                        rel_source, lineno, "backtick path (missing)",
                        candidate, candidate, resolved,
                    ))
                    continue
            actual = real_name(resolved)
            if actual != resolved.name:
                broken_links.append((
                    rel_source, lineno, "backtick path (wrong case)",
                    candidate, candidate, resolved.parent / actual,
                ))
            else:
                ok_count += 1



# -- Main scan -----------------------------------------------------------------
for md in MD_FILES:
    try:
        lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as exc:
        print(f"WARN: cannot read {md}: {exc}")
        continue
    rel = md.relative_to(PROJECT_ROOT)
    check_hyperlinks(md, lines, rel)
    check_backtick_paths(md, lines, rel)

# -- Report --------------------------------------------------------------------
total = ok_count + len(broken_links)
print(f"\nScanned {len(MD_FILES)} Markdown files -- {total} internal references checked.\n")

if broken_links:
    print(f"FAIL  {len(broken_links)} broken or wrong-case reference(s) found:\n")
    for src, lineno, kind, text, target, resolved in broken_links:
        print(f"  [{kind}]  {src}:{lineno}")
        print(f"    reference : {text!r}")
        print(f"    target    : {target!r}")
        print(f"    resolved  : {resolved}")
        print()
    sys.exit(1)
else:
    print(f"OK  All {ok_count} internal references are valid.\n")
    sys.exit(0)
