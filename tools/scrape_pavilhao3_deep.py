"""Deep crawl of pavilhao3.com — recursive link discovery + WP sitemap probe."""
from __future__ import annotations
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
import re

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from selectolax.parser import HTMLParser
from rich.console import Console

from tools._common import RAW, write_json
from tools.scrape_pavilhao3 import extract_image_urls

console = Console()
BASE = "https://pavilhao3.com"
OUT = RAW / "pavilhao3"
HEADERS = {"User-Agent": "Mozilla/5.0 GamingxpoBot/1.0"}

CANDIDATE_PATHS = [
    "/", "/portfolio/", "/galeria/", "/gallery/",
    "/team/", "/equipa/", "/sobre/", "/about/",
    "/contactos/", "/contacto/", "/contact/",
    "/servicos/", "/services/",
    "/projects/", "/projetos/", "/work/",
    "/blog/", "/news/",
]
SITEMAP_PATHS = ["/wp-sitemap.xml", "/sitemap.xml", "/wp-sitemap-posts-page-1.xml"]


def extract_internal_links(html: str, base_url: str) -> set[str]:
    tree = HTMLParser(html)
    links = set()
    base_host = urlparse(BASE).netloc
    for a in tree.css("a"):
        href = a.attributes.get("href", "")
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.netloc != base_host:
            continue
        # strip fragment and query
        clean = urlunparse(parsed._replace(fragment="", query=""))
        # ignore image/file URLs (we want pages)
        if clean.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".pdf", ".zip", ".mp4")):
            continue
        links.add(clean)
    return links


def parse_sitemap(text: str) -> list[str]:
    return re.findall(r"<loc>([^<]+)</loc>", text)


def crawl():
    OUT.mkdir(parents=True, exist_ok=True)
    visited: set[str] = set()
    image_urls: set[str] = set()
    page_for_image: dict[str, str] = {}

    with httpx.Client(follow_redirects=True, timeout=30, headers=HEADERS) as client:
        # Seed queue: candidates + sitemap-discovered URLs
        queue: list[tuple[str, int]] = [(urljoin(BASE, p), 0) for p in CANDIDATE_PATHS]
        for sm in SITEMAP_PATHS:
            try:
                r = client.get(urljoin(BASE, sm))
                if r.status_code == 200 and "<loc>" in r.text:
                    urls = parse_sitemap(r.text)
                    console.log(f"[green]Sitemap {sm} -> {len(urls)} URLs[/green]")
                    for u in urls:
                        if u.startswith(BASE) and u not in [q[0] for q in queue]:
                            queue.append((u, 0))
            except Exception as e:
                console.log(f"[yellow]sitemap {sm}: {e}[/yellow]")

        # BFS-ish: pop, fetch, extract images + new links, push to queue
        pages_crawled = 0
        while queue and pages_crawled < 50:
            url, depth = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            try:
                r = client.get(url)
                time.sleep(0.5)
                if r.status_code != 200:
                    console.log(f"[dim]skip {url} ({r.status_code})[/dim]")
                    continue
                pages_crawled += 1
                pg_imgs = extract_image_urls(r.text, url)
                for img in pg_imgs:
                    if img not in image_urls:
                        image_urls.add(img)
                        page_for_image[img] = url
                console.log(f"[green]{url} → {len(pg_imgs)} images, {len(image_urls)} unique total[/green]")
                if depth < 2:
                    for link in extract_internal_links(r.text, url):
                        if link not in visited and link not in [q[0] for q in queue]:
                            queue.append((link, depth + 1))
            except Exception as e:
                console.log(f"[red]{url}: {e}[/red]")

        console.log(f"[bold]Crawled {pages_crawled} pages. Found {len(image_urls)} unique image URLs.[/bold]")

        # Download (skip files we already have)
        new_manifest = []
        for url in sorted(image_urls):
            fname = Path(urlparse(url).path).name
            dest = OUT / fname
            if dest.exists():
                new_manifest.append({"source": url, "file": fname, "page": page_for_image.get(url), "status": "already_have"})
                continue
            try:
                resp = client.get(url)
                if resp.status_code == 200 and len(resp.content) > 5_000:
                    dest.write_bytes(resp.content)
                    new_manifest.append({"source": url, "file": fname, "page": page_for_image.get(url), "status": "new"})
                    console.log(f"[green]NEW {fname} ({len(resp.content)//1024} KB)[/green]")
            except Exception as e:
                console.log(f"[red]download {url}: {e}[/red]")

    write_json(OUT / "pavilhao3_deep.json", new_manifest)
    new_count = sum(1 for m in new_manifest if m["status"] == "new")
    console.log(f"[bold green]Done. {new_count} new images added. Total in folder: {len(list(OUT.glob('*.jpg'))) + len(list(OUT.glob('*.png'))) + len(list(OUT.glob('*.jpeg')))}[/bold green]")


if __name__ == "__main__":
    crawl()
