"""Inpaint watermark boxes using OpenCV (Telea algorithm).

Lighter alternative to IOPaint/LaMa for small corner overlays.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2
import numpy as np
from PIL import Image
from rich.console import Console
from rich.progress import Progress

from tools._common import CLASSIFIED, CLEANED, RAW, read_json

console = Console()
DIFFS = CLEANED / "_diffs"
DIFFS.mkdir(parents=True, exist_ok=True)
FEATHER_PX = 8
INPAINT_RADIUS = 6  # cv2 inpaint radius


def build_mask(shape: tuple[int, int], boxes: list[dict]) -> np.ndarray:
    """Binary mask, 255 inside watermark boxes, 0 elsewhere."""
    h, w = shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    for b in boxes:
        x1 = max(0, int(b["x"] * w) - FEATHER_PX)
        y1 = max(0, int(b["y"] * h) - FEATHER_PX)
        x2 = min(w, int((b["x"] + b["w"]) * w) + FEATHER_PX)
        y2 = min(h, int((b["y"] + b["h"]) * h) + FEATHER_PX)
        mask[y1:y2, x1:x2] = 255
    return mask


def inpaint_image(src_path: Path, boxes: list[dict], dest_path: Path) -> None:
    img = cv2.imread(str(src_path), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"cv2 failed to read {src_path}")
    mask = build_mask(img.shape, boxes)
    cleaned = cv2.inpaint(img, mask, INPAINT_RADIUS, cv2.INPAINT_TELEA)
    cv2.imwrite(str(dest_path), cleaned, [cv2.IMWRITE_JPEG_QUALITY, 92])


def make_diff(original: Path, cleaned: Path, dest: Path) -> None:
    a = Image.open(original).convert("RGB")
    b = Image.open(cleaned).convert("RGB")
    h = max(a.height, b.height)
    a_resized = a.resize((int(a.width * h / a.height), h))
    b_resized = b.resize((int(b.width * h / b.height), h))
    combined = Image.new("RGB", (a_resized.width + b_resized.width + 8, h), "black")
    combined.paste(a_resized, (0, 0))
    combined.paste(b_resized, (a_resized.width + 8, 0))
    combined.save(dest, "PNG", optimize=True)


def inpaint_all() -> None:
    results = read_json(CLASSIFIED / "manifest.json") or []
    kept = [r for r in results if r.get("quality") != "reject" and "error" not in r]
    with_wm = [r for r in kept if r.get("has_watermark") and r.get("watermark_boxes")]
    without_wm = [r for r in kept if not r.get("has_watermark") or not r.get("watermark_boxes")]
    console.log(f"Kept: {len(kept)}  with watermark: {len(with_wm)}  passthrough: {len(without_wm)}")

    with Progress() as progress:
        task = progress.add_task("Inpainting", total=len(with_wm))
        for r in with_wm:
            src = (RAW.parent / r["path"]).resolve()
            cleaned_path = CLEANED / src.name
            try:
                inpaint_image(src, r["watermark_boxes"], cleaned_path)
                make_diff(src, cleaned_path, DIFFS / (src.stem + ".png"))
            except Exception as e:
                console.log(f"[red]{src.name}: {e}[/red]")
            progress.advance(task)

    # Passthrough: copy non-watermarked, non-rejected images straight through.
    for r in without_wm:
        src = (RAW.parent / r["path"]).resolve()
        dest = CLEANED / src.name
        if not dest.exists():
            dest.write_bytes(src.read_bytes())

    console.log(f"[bold green]Done. Cleaned -> .tmp/cleaned/  Diffs -> .tmp/cleaned/_diffs/[/bold green]")


if __name__ == "__main__":
    inpaint_all()
