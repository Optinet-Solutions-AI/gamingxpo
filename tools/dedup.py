"""Group near-duplicate images by perceptual hash."""
from __future__ import annotations
from pathlib import Path
from PIL import Image
import imagehash


def find_duplicates(paths: list[Path], threshold: int = 4) -> list[list[Path]]:
    hashes = {}
    for p in paths:
        try:
            img = Image.open(p)
            hashes[p] = (imagehash.phash(img), imagehash.colorhash(img))
        except Exception:
            continue
    seen: set[Path] = set()
    groups: list[list[Path]] = []
    items = list(hashes.items())
    for i, (p1, (ph1, ch1)) in enumerate(items):
        if p1 in seen:
            continue
        group = [p1]
        for p2, (ph2, ch2) in items[i + 1:]:
            if p2 in seen:
                continue
            if (ph1 - ph2) <= threshold and (ch1 - ch2) <= threshold:
                group.append(p2)
                seen.add(p2)
        if len(group) > 1:
            groups.append(group)
            seen.add(p1)
    return groups
