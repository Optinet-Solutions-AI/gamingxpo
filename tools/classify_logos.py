"""Use Google Gemini vision to classify watermark vs. physical logos in each image."""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rich.console import Console
from rich.progress import Progress

from tools._common import CLASSIFIED, RAW, read_json, write_json

console = Console()
MODEL = "gemini-2.5-flash"

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


def classify_all() -> None:
    from google import genai
    manifest = read_json(RAW / "raw_manifest.json") or []
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        console.print("[bold red]GEMINI_API_KEY missing in .env[/bold red]")
        sys.exit(1)
    client = genai.Client(api_key=api_key)
    results = []
    with Progress() as progress:
        task = progress.add_task("Classifying", total=len(manifest))
        for entry in manifest:
            path = (RAW.parent / entry["path"]).resolve()
            try:
                result = classify_one(client, path)
                results.append({
                    "path": entry["path"],
                    "has_watermark": result.has_watermark,
                    "watermark_boxes": [b.__dict__ for b in result.watermark_boxes],
                    "physical_logos": result.physical_logos,
                    "quality": result.quality,
                    "subject": result.subject,
                })
            except Exception as e:
                console.log(f"[red]{path.name}: {e}[/red]")
                results.append({"path": entry["path"], "error": str(e)})
            progress.advance(task)
    write_json(CLASSIFIED / "manifest.json", results)
    console.log(f"[bold green]Done. {len(results)} classified -> .tmp/classified/manifest.json[/bold green]")
    # Print a summary
    by_quality = {}
    by_watermark = 0
    for r in results:
        q = r.get("quality", "error")
        by_quality[q] = by_quality.get(q, 0) + 1
        if r.get("has_watermark"):
            by_watermark += 1
    console.print(f"By quality: {by_quality}")
    console.print(f"Has watermark: {by_watermark}")


if __name__ == "__main__":
    classify_all()
