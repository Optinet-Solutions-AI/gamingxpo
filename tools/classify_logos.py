"""Use Google Gemini vision to classify watermark vs. physical logos in each image.

Resilient version with checkpointing + parallel requests + per-call retries.
"""
from __future__ import annotations
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console

from tools._common import CLASSIFIED, RAW, read_json, write_json

console = Console()
MODEL = "gemini-2.5-flash"
WORKERS = 6        # parallel requests
RETRIES = 3        # per-call retries on transient errors
BACKOFF = 4        # seconds between retries
CHECKPOINT = 10    # save manifest every N completions

PROMPT = """\
You are classifying logos in a photo of an iGaming event booth.

Return JSON with this exact shape:
{
  "has_watermark": bool,
  "watermark_boxes": [{"x": float, "y": float, "w": float, "h": float, "label": str}],
  "physical_logos": [{"label": str}],
  "quality": "portfolio_grade" | "social_only" | "reject",
  "subject": "booth_exterior" | "booth_interior" | "crowd" | "team" | "detail" | "other"
}

Rules:
- watermark_boxes coordinates are normalized 0-1 of image dimensions (x,y = top-left; w,h = size).
- A WATERMARK is a logo/text overlay added on top of the photo by the publisher (e.g. an Instagram handle in the corner, a faded brand mark, a repeating text pattern). It is NOT physically part of the scene.
- A PHYSICAL LOGO is a logo that exists IN the scene -- on a booth wall, on a t-shirt, on signage, on a screen displayed at the booth. NEVER mark these as watermarks. They are social proof and must be kept.
- quality: "portfolio_grade" = sharp, well-composed, shows booth or product clearly. "social_only" = usable but lower quality (motion blur, poor angle). "reject" = screenshot, meme, blurry, off-topic, avatar/profile picture.
- subject: classify as "team" if the photo is a posed portrait of a single person against a plain studio background. Otherwise pick the closest match.

Respond with ONLY the JSON object, no prose or markdown fences."""

RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["has_watermark", "watermark_boxes", "physical_logos", "quality", "subject"],
    "properties": {
        "has_watermark": {"type": "boolean"},
        "watermark_boxes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["x", "y", "w", "h", "label"],
                "properties": {
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "w": {"type": "number"},
                    "h": {"type": "number"},
                    "label": {"type": "string"},
                },
            },
        },
        "physical_logos": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["label"],
                "properties": {"label": {"type": "string"}},
            },
        },
        "quality": {"type": "string", "enum": ["portfolio_grade", "social_only", "reject"]},
        "subject": {
            "type": "string",
            "enum": ["booth_exterior", "booth_interior", "crowd", "team", "detail", "other"],
        },
    },
}


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float
    label: str = ""


@dataclass
class ClassificationResult:
    has_watermark: bool
    watermark_boxes: list[Box] = field(default_factory=list)
    physical_logos: list[dict] = field(default_factory=list)
    quality: Literal["portfolio_grade", "social_only", "reject"] = "social_only"
    subject: str = "other"


def parse_response(raw: str) -> ClassificationResult:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    data = json.loads(text)
    return ClassificationResult(
        has_watermark=bool(data.get("has_watermark", False)),
        watermark_boxes=[Box(**b) for b in data.get("watermark_boxes", [])],
        physical_logos=list(data.get("physical_logos", [])),
        quality=data.get("quality", "social_only"),
        subject=data.get("subject", "other"),
    )


def classify_one(client, image_path: Path) -> ClassificationResult:
    from google.genai import types
    mime = "image/jpeg" if image_path.suffix.lower() in (".jpg", ".jpeg") else f"image/{image_path.suffix[1:].lower()}"
    image_part = types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime)

    last_exc = None
    for attempt in range(RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[image_part, PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RESPONSE_SCHEMA,
                    temperature=0.0,
                ),
            )
            return parse_response(response.text)
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            if attempt < RETRIES - 1 and any(s in msg for s in ("10054", "connection", "timeout", "429", "503", "504")):
                time.sleep(BACKOFF * (attempt + 1))
                continue
            raise
    raise last_exc  # pragma: no cover


def classify_all() -> None:
    from google import genai

    manifest = read_json(RAW / "raw_manifest.json") or []
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]GEMINI_API_KEY missing in .env[/bold red]")
        sys.exit(1)

    # Resume: skip entries already in the existing manifest (matched by `path`)
    existing = read_json(CLASSIFIED / "manifest.json") or []
    done_paths = {r["path"] for r in existing if r.get("path") and "error" not in r}
    todo = [e for e in manifest if e["path"] not in done_paths]
    console.print(f"[cyan]Manifest: {len(manifest)} total · {len(done_paths)} already classified · {len(todo)} to do[/cyan]")

    results = list(existing)
    client = genai.Client(api_key=api_key)

    completed = 0

    def work(entry):
        path = (RAW.parent / entry["path"]).resolve()
        try:
            result = classify_one(client, path)
            return entry["path"], {
                "path": entry["path"],
                "has_watermark": result.has_watermark,
                "watermark_boxes": [b.__dict__ for b in result.watermark_boxes],
                "physical_logos": result.physical_logos,
                "quality": result.quality,
                "subject": result.subject,
            }, None
        except Exception as e:
            return entry["path"], {"path": entry["path"], "error": str(e)}, str(e)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = [ex.submit(work, e) for e in todo]
        for fut in as_completed(futures):
            p, rec, err = fut.result()
            results.append(rec)
            completed += 1
            tag = f"[red]ERR[/red]" if err else f"[green]ok[/green] {rec.get('quality','?')[:4]}/{rec.get('subject','?')[:6]}"
            console.log(f"  [{completed}/{len(todo)}] {tag} {Path(p).name[:55]}")
            if completed % CHECKPOINT == 0:
                write_json(CLASSIFIED / "manifest.json", results)
                console.log(f"  [dim]checkpoint @ {completed}[/dim]")

    write_json(CLASSIFIED / "manifest.json", results)
    by_quality: dict[str, int] = {}
    by_subject: dict[str, int] = {}
    errors = 0
    watermarks = 0
    for r in results:
        if "error" in r:
            errors += 1
            continue
        by_quality[r["quality"]] = by_quality.get(r["quality"], 0) + 1
        by_subject[r["subject"]] = by_subject.get(r["subject"], 0) + 1
        if r["has_watermark"]:
            watermarks += 1
    console.print(f"[bold green]Done. {len(results)} classified → .tmp/classified/manifest.json[/bold green]")
    console.print(f"  errors: {errors}")
    console.print(f"  by_quality: {by_quality}")
    console.print(f"  by_subject: {by_subject}")
    console.print(f"  has_watermark: {watermarks}")


if __name__ == "__main__":
    classify_all()
