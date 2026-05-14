"""Run the sharp optimizer (via Node) and emit src/content/portfolio.json."""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

from tools._common import CLASSIFIED, ROOT, read_json

console = Console()
CONTENT = ROOT / "src" / "content"


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", name.lower())
    return re.sub(r"^-+|-+$", "", s)


def emit_content_manifest() -> None:
    raw = read_json(CLASSIFIED / "manifest.json") or []
    by_basename = {}
    for r in raw:
        p = r["path"].rsplit("/", 1)[-1]
        by_basename[p] = r

    portfolio_dir = ROOT / "public" / "images" / "portfolio"
    items = []
    for sub in sorted(portfolio_dir.iterdir()):
        if not sub.is_dir():
            continue
        meta = None
        # Match slug back to original filename (slug = slugify(stem))
        for original_name, r in by_basename.items():
            if slugify(Path(original_name).stem) == sub.name:
                meta = r
                break
        if meta is None or meta.get("quality") == "reject" or "error" in meta:
            console.log(f"[yellow]skipping {sub.name} (no meta or rejected)[/yellow]")
            continue
        items.append({
            "slug": sub.name,
            "subject": meta.get("subject", "other"),
            "quality": meta.get("quality", "social_only"),
            "src_base": f"/images/portfolio/{sub.name}",
            "widths": [640, 960, 1440, 1920],
            "alt": meta.get("subject", "iGaming booth").replace("_", " "),
        })

    CONTENT.mkdir(parents=True, exist_ok=True)
    (CONTENT / "portfolio.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    console.log(f"[green]Wrote {len(items)} portfolio entries -> src/content/portfolio.json[/green]")


def main() -> None:
    console.log("Running sharp optimizer...")
    subprocess.run(["node", "tools/optimize_images.mjs"], check=True, cwd=ROOT)
    emit_content_manifest()


if __name__ == "__main__":
    main()
