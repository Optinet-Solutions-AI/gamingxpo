"""Shared helpers for the image pipeline."""
from __future__ import annotations
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".tmp"
RAW = TMP / "raw_scrape"
CLASSIFIED = TMP / "classified"
CLEANED = TMP / "cleaned"
PUBLIC_IMG = ROOT / "public" / "images"

for d in (RAW, CLASSIFIED, CLEANED, PUBLIC_IMG):
    d.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
