"""Scrape @pavilhao_3 Instagram via instaloader. Anonymous mode first."""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Self-insert project root so `from tools._common import …` works for direct execution.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import instaloader
from rich.console import Console

from tools._common import RAW, write_json

console = Console()
TARGET = "pavilhao_3"


def scrape() -> None:
    out = RAW / "instagram"
    out.mkdir(parents=True, exist_ok=True)

    L = instaloader.Instaloader(
        dirname_pattern=str(out),
        filename_pattern="{date_utc:%Y%m%d}_{shortcode}_{mediaid}",
        download_videos=False,
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        max_connection_attempts=2,
    )

    user = os.environ.get("IG_USERNAME")
    pw = os.environ.get("IG_PASSWORD")
    if user and pw:
        try:
            L.login(user, pw)
            console.log(f"[green]Signed in as {user}[/green]")
        except Exception as e:
            console.log(f"[yellow]Login failed: {e} — falling back to anonymous[/yellow]")

    manifest = []
    try:
        profile = instaloader.Profile.from_username(L.context, TARGET)
        for post in profile.get_posts():
            try:
                L.download_post(post, target=TARGET)
                manifest.append({
                    "shortcode": post.shortcode,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "caption": (post.caption or "")[:500],
                    "date": post.date_utc.isoformat() if post.date_utc else None,
                })
            except Exception as e:
                console.log(f"[red]post {post.shortcode}: {e}[/red]")
    except instaloader.exceptions.LoginRequiredException:
        console.log("[bold red]Instagram requires login.[/bold red]")
        console.log("Set IG_USERNAME and IG_PASSWORD in .env and re-run.")
        sys.exit(2)
    except instaloader.exceptions.ConnectionException as e:
        console.log(f"[bold red]Rate-limited or connection issue: {e}[/bold red]")
        console.log("Wait 10 minutes, or sign in (set IG_USERNAME/IG_PASSWORD).")
        sys.exit(3)

    write_json(out / "instagram.json", manifest)
    console.log(f"[bold green]Done. {len(manifest)} posts -> {out}[/bold green]")


if __name__ == "__main__":
    scrape()
