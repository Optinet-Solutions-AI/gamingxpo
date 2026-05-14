"""Scrape @pavilhao_3 Instagram via a logged-in Playwright browser.

Uses a persistent Chromium profile at .tmp/ig_browser_profile so login state
persists between runs. First run opens a headed browser; user logs in once,
the script auto-detects when the profile grid is visible and starts scraping.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from playwright.sync_api import sync_playwright
from rich.console import Console

from tools._common import RAW, TMP, write_json

console = Console()
TARGET = "pavilhao_3"
PROFILE_URL = f"https://www.instagram.com/{TARGET}/"
PROFILE_DIR = TMP / "ig_browser_profile"
OUT = RAW / "instagram"


def wait_for_grid(page, max_wait_s: int = 600) -> bool:
    """Poll the page every 3s until the profile post grid is visible (= logged in)."""
    console.print("[yellow]Browser opened. If asked to log in, do it in the browser window.[/yellow]")
    console.print(f"[yellow]Once you see the post grid at {PROFILE_URL}, the scrape will auto-start.[/yellow]")
    console.print("[dim]Polling every 3s. Total wait budget: 10 minutes.[/dim]")
    deadline = time.time() + max_wait_s
    while time.time() < deadline:
        try:
            count = page.evaluate('document.querySelectorAll(\'a[href*="/p/"]\').length')
            if count >= 1:
                console.print(f"[green]Detected {count} post tiles - proceeding to scrape.[/green]")
                return True
        except Exception:
            pass
        time.sleep(3)
    return False


def scroll_to_bottom(page, max_iters: int = 80):
    console.log("Scrolling profile to load all posts...")
    prev_height = 0
    stable = 0
    last_count = 0
    for i in range(max_iters):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.8)
        height = page.evaluate("document.body.scrollHeight")
        count = page.evaluate('document.querySelectorAll(\'a[href*="/p/"]\').length')
        console.log(f"  scroll {i+1:>2}: height={height} posts_visible={count}")
        if height == prev_height and count == last_count:
            stable += 1
            if stable >= 3:
                break
        else:
            stable = 0
        prev_height, last_count = height, count


def extract_image_urls(page) -> list[str]:
    urls = page.evaluate(
        """
        () => {
          const imgs = Array.from(document.querySelectorAll('main article img, main img[srcset]'));
          const out = new Set();
          for (const img of imgs) {
            if (img.srcset) {
              const parts = img.srcset.split(',').map(s => s.trim().split(' '));
              parts.sort((a, b) => parseInt(b[1] || '0', 10) - parseInt(a[1] || '0', 10));
              if (parts[0] && parts[0][0]) out.add(parts[0][0]);
            } else if (img.src && img.src.startsWith('https://')) {
              out.add(img.src);
            }
          }
          return [...out];
        }
        """
    )
    return urls


def download(urls: list[str]) -> list[dict]:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    with httpx.Client(timeout=30, follow_redirects=True, headers={"Referer": "https://www.instagram.com/"}) as client:
        for i, url in enumerate(urls):
            fname = f"ig_{i:03d}.jpg"
            dest = OUT / fname
            if dest.exists():
                manifest.append({"source": url, "file": fname, "page": "instagram"})
                continue
            try:
                r = client.get(url)
                if r.status_code == 200 and len(r.content) > 5_000:
                    dest.write_bytes(r.content)
                    manifest.append({"source": url, "file": fname, "page": "instagram"})
                    console.log(f"  [{i+1:>3}/{len(urls)}] {fname} ({len(r.content)//1024} KB)")
                else:
                    console.log(f"  [{i+1:>3}/{len(urls)}] skip status={r.status_code} size={len(r.content)}")
            except Exception as e:
                console.log(f"  [red][{i+1:>3}/{len(urls)}] FAIL {url}: {e}[/red]")
    return manifest


def scrape():
    OUT.mkdir(parents=True, exist_ok=True)
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=60_000)

        if not wait_for_grid(page):
            console.print("[bold red]Timed out waiting for login / grid. Exiting.[/bold red]")
            context.close()
            sys.exit(4)

        scroll_to_bottom(page)
        urls = extract_image_urls(page)
        console.print(f"[bold]Found {len(urls)} unique image URLs[/bold]")

        manifest = download(urls)
        write_json(OUT / "instagram.json", manifest)
        console.print(f"[bold green]Done. {len(manifest)} images -> {OUT}[/bold green]")
        context.close()


if __name__ == "__main__":
    scrape()
