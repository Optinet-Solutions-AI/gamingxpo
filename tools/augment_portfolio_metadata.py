"""Join optimized portfolio entries with their source pages for project metadata."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools._common import RAW, ROOT, CLASSIFIED, read_json

PORTFOLIO_JSON = ROOT / "src" / "data" / "portfolio.json"


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", name.lower())
    return re.sub(r"^-+|-+$", "", s)


def slugify_project(slug: str) -> str:
    return slug.replace("-", " ").title()


def main():
    portfolio = json.loads(PORTFOLIO_JSON.read_text(encoding="utf-8"))
    classified = read_json(CLASSIFIED / "manifest.json") or []
    deep = read_json(RAW / "pavilhao3" / "pavilhao3_deep.json") or []

    # Build lookup: filename -> source page (from deep scrape manifest)
    page_for_file: dict[str, str] = {entry["file"]: entry.get("page", "") for entry in deep}

    # Build lookup: slug -> classified entry (slug = slugify(stem of path basename))
    slug_to_cls: dict[str, dict] = {}
    for cls in classified:
        basename = cls["path"].rsplit("/", 1)[-1]
        stem = Path(basename).stem
        slug = slugify(stem)
        slug_to_cls[slug] = cls

    augmented = []
    for entry in portfolio:
        slug = entry["slug"]
        cls = slug_to_cls.get(slug)
        if cls:
            fname = cls["path"].rsplit("/", 1)[-1]
            page = page_for_file.get(fname, "")
            if page:
                entry["source_page"] = page
                # /blog/portfolio-item/<slug>/ -> project name
                m = re.search(r"/blog/portfolio-item/([^/]+)/?$", page)
                if m:
                    entry["project"] = slugify_project(m.group(1))
                # /we/ -> team photo override
                elif page.rstrip("/").endswith("/we"):
                    entry["subject"] = "team"
                # facility pages
                elif "/pavilhao3-3" in page or "/contatos" in page:
                    entry["subject"] = "facility"
        augmented.append(entry)

    PORTFOLIO_JSON.write_text(
        json.dumps(augmented, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Print summary
    by_subject: dict[str, int] = {}
    by_project: dict[str, int] = {}
    with_source_page = 0
    for e in augmented:
        subj = e.get("subject", "?")
        by_subject[subj] = by_subject.get(subj, 0) + 1
        if e.get("project"):
            proj = e["project"]
            by_project[proj] = by_project.get(proj, 0) + 1
        if e.get("source_page"):
            with_source_page += 1

    print(f"Total entries: {len(augmented)}")
    print(f"With source_page: {with_source_page}")
    print(f"By subject: {by_subject}")
    print(f"Named projects: {by_project}")


if __name__ == "__main__":
    main()
