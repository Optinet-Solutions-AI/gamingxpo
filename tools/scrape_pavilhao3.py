"""Scrape pavilhao3.com homepage + gallery for images."""
from __future__ import annotations
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
import httpx
from selectolax.parser import HTMLParser
from rich.console import Console

# Allow both `python tools/scrape_pavilhao3.py` and `python -m pytest` imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools._common import RAW, write_json

console = Console()
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def _normalise(url: str, base_url: str) -> str | None:
    """Resolve relative/protocol-relative URLs and strip fragments.

    Returns None if the result is not an https URL ending in an image extension.
    """
    if not url:
        return None
    # Protocol-relative
    if url.startswith("//"):
        url = "https:" + url
    absolute = urljoin(base_url, url)
    # Strip fragment (WordPress appends #post-id to some image src attrs)
    parsed = urlparse(absolute)
    absolute = urlunparse(parsed._replace(fragment=""))
    if not absolute.startswith("https://"):
        return None
    if absolute.lower().endswith(IMG_EXTS):
        return absolute
    return None


def extract_image_urls(html: str, base_url: str) -> list[str]:
    tree = HTMLParser(html)
    urls: set[str] = set()

    for img in tree.css("img"):
        attrs = img.attributes
        # Standard src + lazy-load variants
        for attr in ("src", "data-src", "data-lazyload", "data-lazy-src", "data-original"):
            val = attrs.get(attr)
            norm = _normalise(val, base_url) if val else None
            if norm:
                urls.add(norm)

        # srcset / data-srcset — pick the largest (highest width descriptor)
        for attr in ("srcset", "data-srcset"):
            srcset = attrs.get(attr)
            if not srcset:
                continue
            best_url: str | None = None
            best_w = -1
            for part in srcset.split(","):
                pieces = part.strip().split()
                if not pieces:
                    continue
                candidate_url = pieces[0]
                w = 0
                if len(pieces) > 1 and pieces[1].endswith("w"):
                    try:
                        w = int(pieces[1].rstrip("w"))
                    except ValueError:
                        pass
                if w > best_w:
                    best_w = w
                    best_url = candidate_url
            if best_url:
                norm = _normalise(best_url, base_url)
                if norm:
                    urls.add(norm)

    # <a href="...jpg"> direct image links
    for a in tree.css("a"):
        href = a.attributes.get("href", "")
        norm = _normalise(href, base_url)
        if norm:
            urls.add(norm)

    return sorted(urls)


def scrape() -> None:
    out = RAW / "pavilhao3"
    out.mkdir(parents=True, exist_ok=True)
    pages = [
        "https://pavilhao3.com/",
        "https://pavilhao3.com/portfolio/",
        "https://pavilhao3.com/galeria/",
    ]
    manifest = []
    with httpx.Client(
        follow_redirects=True,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 GamingxpoBot"},
    ) as client:
        all_urls: set[str] = set()
        for page in pages:
            try:
                r = client.get(page)
                if r.status_code != 200:
                    console.log(f"[yellow]skip {page} ({r.status_code})[/yellow]")
                    continue
                page_urls = extract_image_urls(r.text, page)
                console.log(f"[green]{page} -> {len(page_urls)} images[/green]")
                all_urls.update(page_urls)
            except httpx.HTTPError as e:
                console.log(f"[red]error {page}: {e}[/red]")

        for url in sorted(all_urls):
            fname = Path(urlparse(url).path).name
            dest = out / fname
            if dest.exists():
                continue
            try:
                resp = client.get(url)
                if resp.status_code == 200 and len(resp.content) > 5_000:
                    dest.write_bytes(resp.content)
                    manifest.append({"source": url, "file": fname, "page": "pavilhao3"})
            except httpx.HTTPError as e:
                console.log(f"[red]download {url}: {e}[/red]")

    write_json(out / "pavilhao3.json", manifest)
    console.log(f"[bold green]Done. {len(manifest)} images -> {out}[/bold green]")


if __name__ == "__main__":
    scrape()
