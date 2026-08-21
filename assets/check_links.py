"""Walk every page and resolve every first-party link against the filesystem.

Catches the two failures a static site actually ships: an href pointing at a
path that no longer exists, and a fragment pointing at an id nobody ever added.
Both survive a visual review because a browser renders a dead link exactly like
a live one.

External links are listed but not fetched. The sandbox this runs in cannot
reach the public internet, and a checker that reports every outbound link as
broken is worse than no checker.
"""
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = (".cejel", ".playwright-mcp", ".git", "node_modules")

HREF = re.compile(r'(?:href|src)="([^"]+)"')
ID = re.compile(r'\bid="([^"]+)"')


def pages() -> list[Path]:
    out = []
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        out.append(path)
    return out


def resolve(target: str, page: Path) -> Path | None:
    """Map a site path or relative path onto a file on disk."""
    clean = unquote(target)
    base = ROOT if clean.startswith("/") else page.parent
    candidate = (base / clean.lstrip("/")).resolve()
    if candidate.is_dir():
        candidate = candidate / "index.html"
    return candidate if candidate.exists() else None


def main() -> int:
    ids: dict[Path, set[str]] = {}
    all_pages = pages()
    for path in all_pages:
        ids[path] = set(ID.findall(path.read_text(encoding="utf-8", errors="replace")))

    broken, missing_anchor, external = [], [], set()
    for path in all_pages:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in HREF.findall(text):
            if raw.startswith(("http://", "https://")):
                external.add(urlsplit(raw).netloc)
                continue
            if raw.startswith(("mailto:", "tel:", "data:", "javascript:", "#")):
                if raw.startswith("#") and len(raw) > 1:
                    if raw[1:] not in ids[path]:
                        missing_anchor.append(f"{rel} -> {raw}")
                continue

            split = urlsplit(raw)
            if not split.path:
                continue
            target = resolve(split.path, path)
            if target is None:
                broken.append(f"{rel} -> {raw}")
                continue
            if split.fragment and target in ids and split.fragment not in ids[target]:
                missing_anchor.append(f"{rel} -> {raw}")

    print(f"pages checked: {len(all_pages)}")
    print(f"broken internal links: {len(broken)}")
    for b in broken:
        print(f"  {b}")
    print(f"missing anchors: {len(missing_anchor)}")
    for m in missing_anchor:
        print(f"  {m}")
    print(f"external hosts referenced ({len(external)}, not fetched):")
    for host in sorted(external):
        print(f"  {host}")
    return 1 if broken or missing_anchor else 0


if __name__ == "__main__":
    sys.exit(main())
