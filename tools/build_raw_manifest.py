"""Merge pavilhao3 + instagram raw scrapes, dedup, write master manifest."""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

from tools._common import RAW, write_json
from tools.dedup import find_duplicates

console = Console()


def build():
    pav_dir = RAW / "pavilhao3"
    ig_dir = RAW / "instagram"
    all_files = []
    for d in (pav_dir, ig_dir):
        if d.exists():
            all_files += [p for p in d.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
    console.log(f"Total raw files: {len(all_files)}")

    dup_groups = find_duplicates(all_files)
    console.log(f"Duplicate groups: {len(dup_groups)}")

    drop: set[Path] = set()
    for group in dup_groups:
        keeper = max(group, key=lambda p: p.stat().st_size)
        for p in group:
            if p != keeper:
                drop.add(p)
    console.log(f"Dropping {len(drop)} duplicates")

    keep = [p for p in all_files if p not in drop]
    manifest = [
        {
            "path": str(p.relative_to(RAW.parent)).replace("\\", "/"),
            "source": p.parent.name,
            "size": p.stat().st_size,
        }
        for p in keep
    ]
    write_json(RAW / "raw_manifest.json", manifest)
    console.log(f"[green]Kept {len(keep)} unique images -> .tmp/raw_scrape/raw_manifest.json[/green]")
    return manifest


if __name__ == "__main__":
    build()
