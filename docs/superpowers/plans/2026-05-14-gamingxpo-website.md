# Gamingxpo.com Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a premium, agency-grade marketing site for Gamingxpo.com — a global iGaming booth/stand builder — with a Python image pipeline that scrapes, classifies, inpaints, and optimizes assets, and an Astro+Tailwind static site that consumes them.

**Architecture:** Two-layer system. (1) Python tools in `tools/` scrape `pavilhao3.com` and `@pavilhao_3` on Instagram, classify watermark vs. physical logos with Claude vision, inpaint watermarks with IOPaint/LaMa locally, and emit optimized AVIF + WebP to `public/images/`. (2) Astro + Tailwind static site reads `public/images/` and `src/content/` to render 5 pages (Home/Services/Portfolio/About/Contact). Mockup-first — no backend in v1.

**Tech Stack:** Astro 4, Tailwind CSS 3, TypeScript, Python 3.11+ (httpx, selectolax, instaloader, imagehash, IOPaint), Anthropic SDK, sharp (via npx), Playwright (testing), Vercel.

**Authoritative spec:** [docs/superpowers/specs/2026-05-14-gamingxpo-website-design.md](../specs/2026-05-14-gamingxpo-website-design.md)

---

## Execution overview (phase gates)

| Phase | Tasks | User gate |
|---|---|---|
| 0 — Scaffold | 1–6 | `npm run dev` serves blank Astro at `localhost:4321` |
| 1 — Scrape | 7–12 | Raw image folders populated, user confirms count is sufficient |
| 2 — Clean + optimize | 13–18 | User audits `.tmp/cleaned/_diffs/`; signs off on inpaint quality |
| 3 — Design system | 19–25 | User approves `/__styleguide` visually |
| 4 — Page assembly | 26–33 | User walks live preview, approves copy/content |
| 5 — Launch polish | 34–41 | Lighthouse ≥95, production deploy live |

Each phase is its own git branch (`phase-0-scaffold`, `phase-1-scrape`, …). Branches merge to `main` only after the user's gate-pass.

---

# PHASE 0 — Scaffold

### Task 1: Initialize git and base config files

**Files:**
- Create: `.gitignore`
- Create: `.claudeignore`
- Create: `.env.example`

- [ ] **Step 1: Initialize git repo**

```bash
git init
git checkout -b phase-0-scaffold
```

- [ ] **Step 2: Write `.gitignore`**

```
node_modules/
dist/
.astro/
.tmp/
.env
.env.local
.DS_Store
*.log
public/images/portfolio/
public/images/services/
# (we COMMIT optimized images later via `git add -f` when phase 2 user-approved)
```

- [ ] **Step 3: Write `.claudeignore`**

```
node_modules/
dist/
.astro/
.tmp/
public/images/
package-lock.json
bun.lockb
yarn.lock
pnpm-lock.yaml
*.min.js
*.min.css
*.map
*.log
```

- [ ] **Step 4: Write `.env.example`**

```
ANTHROPIC_API_KEY=
IG_USERNAME=
IG_PASSWORD=
PUBLIC_SITE_URL=http://localhost:4321
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore .claudeignore .env.example
git commit -m "chore: init repo + ignores"
```

---

### Task 2: Scaffold Astro + Tailwind

**Files:**
- Create: `package.json`, `astro.config.mjs`, `tailwind.config.cjs`, `tsconfig.json`, `src/styles/global.css`, `src/pages/index.astro`, `src/layouts/Base.astro`

- [ ] **Step 1: Bootstrap Astro project (non-interactive)**

```bash
npm create astro@latest . -- --template minimal --typescript strict --no-git --skip-houston --yes
```

Expected: project files written into current directory.

- [ ] **Step 2: Add Tailwind integration**

```bash
npx astro add tailwind --yes
```

Expected: `@astrojs/tailwind` and `tailwindcss` installed; `astro.config.mjs` updated.

- [ ] **Step 3: Replace `src/pages/index.astro` with a placeholder**

```astro
---
import Base from '../layouts/Base.astro';
---
<Base title="Gamingxpo — Coming soon">
  <main class="min-h-screen flex items-center justify-center bg-neutral-950 text-neutral-100">
    <h1 class="text-4xl font-semibold tracking-tight">Gamingxpo.com</h1>
  </main>
</Base>
```

- [ ] **Step 4: Create `src/layouts/Base.astro`**

```astro
---
const { title = 'Gamingxpo' } = Astro.props;
---
<!doctype html>
<html lang="en" class="bg-neutral-950">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <link rel="stylesheet" href="/src/styles/global.css" />
  </head>
  <body class="font-sans antialiased">
    <slot />
  </body>
</html>
```

- [ ] **Step 5: Create `src/styles/global.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --bg: #0A0A0B;
  --fg: #F5F4F1;
  --accent: #E6FF3D;
}

html, body { background: var(--bg); color: var(--fg); }
```

- [ ] **Step 6: Verify dev server**

```bash
npm run dev
```

Expected: Astro reports `Local: http://localhost:4321/`. Visit it and confirm "Gamingxpo.com" renders.

- [ ] **Step 7: Stop dev server (Ctrl+C) and commit**

```bash
git add .
git commit -m "feat(phase-0): scaffold astro + tailwind"
```

---

### Task 3: Tailwind theme tokens

**Files:**
- Modify: `tailwind.config.cjs`
- Modify: `src/styles/global.css`

- [ ] **Step 1: Update `tailwind.config.cjs`**

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0A0B',
        fg: '#F5F4F1',
        accent: '#E6FF3D',
        muted: '#A1A09B',
        line: '#1E1E20',
      },
      fontFamily: {
        sans: ['"Inter"', 'system-ui', 'sans-serif'],
        display: ['"Inter Tight"', '"Inter"', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display-xl': ['clamp(3rem, 6vw, 6rem)', { lineHeight: '0.95', letterSpacing: '-0.02em' }],
        'display-lg': ['clamp(2.25rem, 4vw, 4rem)', { lineHeight: '1.0', letterSpacing: '-0.02em' }],
        'display-md': ['clamp(1.5rem, 2.5vw, 2.25rem)', { lineHeight: '1.15', letterSpacing: '-0.01em' }],
        body: ['1.125rem', { lineHeight: '1.6' }],
      },
      maxWidth: { prose: '65ch', layout: '1440px' },
      spacing: { section: '6rem', 'section-sm': '3rem' },
    },
  },
  plugins: [],
};
```

- [ ] **Step 2: Update `src/styles/global.css` to use tokens**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html, body { @apply bg-bg text-fg font-sans antialiased; }
  h1, h2, h3, h4 { @apply font-display tracking-tight; }
  ::selection { background: var(--accent); color: var(--bg); }
}

:root {
  --bg: #0A0A0B;
  --fg: #F5F4F1;
  --accent: #E6FF3D;
}
```

- [ ] **Step 3: Verify dev server still renders**

```bash
npm run dev
```

Open `http://localhost:4321/` — should look identical (still placeholder) but with tokenized styles applied.

- [ ] **Step 4: Stop dev server and commit**

```bash
git add tailwind.config.cjs src/styles/global.css
git commit -m "feat(phase-0): add tailwind theme tokens"
```

---

### Task 4: Self-host Inter + Inter Tight fonts

**Files:**
- Create: `public/fonts/inter-var.woff2`, `public/fonts/inter-tight-var.woff2`
- Modify: `src/styles/global.css`

- [ ] **Step 1: Download Inter and Inter Tight variable fonts**

```bash
mkdir -p public/fonts
curl -L -o public/fonts/inter-var.woff2 "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Variable.woff2"
curl -L -o public/fonts/inter-tight-var.woff2 "https://github.com/google/fonts/raw/main/ofl/intertight/InterTight%5Bwght%5D.woff2"
```

Expected: both files > 100KB. Verify with `ls -la public/fonts/`.

- [ ] **Step 2: Add `@font-face` declarations to `src/styles/global.css`**

Add at the top of the file, before `@tailwind base`:

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
@font-face {
  font-family: 'Inter Tight';
  src: url('/fonts/inter-tight-var.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
}
```

- [ ] **Step 3: Verify fonts load**

```bash
npm run dev
```

DevTools → Network → filter `woff2`. Both files load with status 200. Heading should render in Inter Tight.

- [ ] **Step 4: Commit**

```bash
git add public/fonts/ src/styles/global.css
git commit -m "feat(phase-0): self-host inter + inter tight"
```

---

### Task 5: Python tools skeleton + workflows

**Files:**
- Create: `tools/__init__.py`, `tools/_common.py`, `pyproject.toml`, `workflows/scrape_and_clean_images.md`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "gamingxpo-tools"
version = "0.0.1"
requires-python = ">=3.11"
dependencies = [
  "httpx>=0.27",
  "selectolax>=0.3",
  "instaloader>=4.13",
  "imagehash>=4.3",
  "Pillow>=10.4",
  "anthropic>=0.40",
  "iopaint>=1.4",
  "python-dotenv>=1.0",
  "rich>=13.7",
]

[tool.pytest.ini_options]
testpaths = ["tools/tests"]
```

- [ ] **Step 2: Install Python deps in a venv**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
pip install pytest pytest-mock
```

- [ ] **Step 3: Create `tools/_common.py`**

```python
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
```

- [ ] **Step 4: Create `tools/__init__.py`** (empty file)

- [ ] **Step 5: Create `workflows/scrape_and_clean_images.md`**

```markdown
# SOP — Scrape and Clean Images

## Inputs
- `https://pavilhao3.com` (public web)
- `https://www.instagram.com/pavilhao_3` (anonymous first; sign-in if rate-limited)

## Steps

1. `python tools/scrape_pavilhao3.py` → writes `.tmp/raw_scrape/pavilhao3/*.jpg` + `pavilhao3.json`
2. `python tools/scrape_instagram.py` → writes `.tmp/raw_scrape/instagram/*.jpg` + `instagram.json`
3. `python tools/classify_logos.py` → writes `.tmp/classified/manifest.json`
4. `python tools/inpaint_watermarks.py` → writes `.tmp/cleaned/*.jpg` + `_diffs/*.png`
5. **User review gate** — open `.tmp/cleaned/_diffs/` and confirm inpaint quality
6. `python tools/optimize_images.py` → writes `public/images/portfolio/<slug>/*.{avif,webp}` and `src/content/portfolio.json`

## Gotchas captured during execution
(Update this section each time we learn something new.)

- Instagram rate-limits anonymous mode at ~50 requests; sign in early if scraping a large account.
- pavilhao3.com's gallery uses lightbox JS; original images live in `<a href>` not `<img src>` — see scraper.
```

- [ ] **Step 6: Commit**

```bash
git add tools/ pyproject.toml workflows/scrape_and_clean_images.md
git commit -m "feat(phase-0): python tools skeleton + first SOP"
```

---

### Task 6: Phase 0 gate-pass

- [ ] **Step 1: Run dev server one final time**

```bash
npm run dev
```

Confirm:
- `http://localhost:4321/` renders "Gamingxpo.com"
- Inter Tight loaded
- No console errors

- [ ] **Step 2: Take a screenshot via Playwright**

```bash
npx playwright install chromium
npx playwright open --viewport-size=1440,900 http://localhost:4321 --save-trace .tmp/trace.zip
```

Or, simpler: use the `webapp-testing` skill or `seo-visual` subagent to capture `http://localhost:4321/` and save to `.tmp/phase-0-screenshot.png`.

- [ ] **Step 3: User reviews screenshot, confirms gate**

Show user screenshot, ask: "Phase 0 gate — confirm to proceed to Phase 1 (scraping)?"

- [ ] **Step 4: On approval, merge branch**

```bash
git checkout -b main 2>nul || git checkout main
git merge phase-0-scaffold --no-ff -m "merge: phase 0 scaffold"
```

---

# PHASE 1 — Scrape

Create branch:

```bash
git checkout -b phase-1-scrape
```

### Task 7: Pavilhao3 scraper — fixture-based test

**Files:**
- Create: `tools/tests/__init__.py`, `tools/tests/test_scrape_pavilhao3.py`, `tools/tests/fixtures/pavilhao3_home.html`

- [ ] **Step 1: Save a fixture of pavilhao3.com homepage**

```bash
curl -L -A "Mozilla/5.0" https://pavilhao3.com/ -o tools/tests/fixtures/pavilhao3_home.html
```

Expected: HTML file > 10KB. Inspect it has `<img>` tags and gallery links.

- [ ] **Step 2: Write failing test**

`tools/tests/test_scrape_pavilhao3.py`:

```python
from pathlib import Path
from tools.scrape_pavilhao3 import extract_image_urls

FIXTURE = Path(__file__).parent / "fixtures" / "pavilhao3_home.html"


def test_extract_image_urls_returns_absolute_urls():
    html = FIXTURE.read_text(encoding="utf-8")
    urls = extract_image_urls(html, base_url="https://pavilhao3.com/")
    assert len(urls) > 0
    for u in urls:
        assert u.startswith("https://"), f"not absolute: {u}"
        assert u.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
```

- [ ] **Step 3: Run test to verify it fails**

```bash
pytest tools/tests/test_scrape_pavilhao3.py -v
```

Expected: ImportError or ModuleNotFoundError on `tools.scrape_pavilhao3`.

- [ ] **Step 4: Commit failing test**

```bash
git add tools/tests/
git commit -m "test(phase-1): failing test for pavilhao3 image extraction"
```

---

### Task 8: Pavilhao3 scraper — implementation

**Files:**
- Create: `tools/scrape_pavilhao3.py`

- [ ] **Step 1: Implement minimal `extract_image_urls`**

```python
"""Scrape pavilhao3.com homepage + gallery for images."""
from __future__ import annotations
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
import httpx
from selectolax.parser import HTMLParser
from rich.console import Console

from tools._common import RAW, write_json

console = Console()
IMG_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def extract_image_urls(html: str, base_url: str) -> list[str]:
    tree = HTMLParser(html)
    urls: set[str] = set()
    # <img src>
    for img in tree.css("img"):
        src = img.attributes.get("src") or img.attributes.get("data-src")
        if src:
            absolute = urljoin(base_url, src)
            if absolute.lower().endswith(IMG_EXTS):
                urls.add(absolute)
        # <img srcset> — take largest
        srcset = img.attributes.get("srcset") or img.attributes.get("data-srcset")
        if srcset:
            largest = max(
                (s.strip().split(" ") for s in srcset.split(",")),
                key=lambda p: int(p[1].rstrip("w")) if len(p) > 1 and p[1].endswith("w") else 0,
                default=None,
            )
            if largest:
                absolute = urljoin(base_url, largest[0])
                if absolute.lower().endswith(IMG_EXTS):
                    urls.add(absolute)
    # <a href> pointing to images (lightbox pattern)
    for a in tree.css("a"):
        href = a.attributes.get("href", "")
        if href.lower().endswith(IMG_EXTS):
            urls.add(urljoin(base_url, href))
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
    with httpx.Client(follow_redirects=True, timeout=30, headers={"User-Agent": "Mozilla/5.0 GamingxpoBot"}) as client:
        all_urls: set[str] = set()
        for page in pages:
            try:
                r = client.get(page)
                if r.status_code != 200:
                    console.log(f"[yellow]skip {page} ({r.status_code})[/yellow]")
                    continue
                page_urls = extract_image_urls(r.text, page)
                console.log(f"[green]{page} → {len(page_urls)} images[/green]")
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
    console.log(f"[bold green]Done. {len(manifest)} images → {out}[/bold green]")


if __name__ == "__main__":
    scrape()
```

- [ ] **Step 2: Run unit test**

```bash
pytest tools/tests/test_scrape_pavilhao3.py -v
```

Expected: PASS.

- [ ] **Step 3: Run real scrape against live site**

```bash
python tools/scrape_pavilhao3.py
```

Expected: `.tmp/raw_scrape/pavilhao3/` populated with N images and `pavilhao3.json`. Check `ls .tmp/raw_scrape/pavilhao3/ | wc -l`.

- [ ] **Step 4: Commit**

```bash
git add tools/scrape_pavilhao3.py
git commit -m "feat(phase-1): pavilhao3 scraper"
```

---

### Task 9: Instagram scraper — anonymous mode

**Files:**
- Create: `tools/scrape_instagram.py`

- [ ] **Step 1: Implement scraper**

```python
"""Scrape @pavilhao_3 Instagram via instaloader. Anonymous mode first."""
from __future__ import annotations
import os
import sys
from pathlib import Path
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
        console.log(f"[bold red]Rate-limited: {e}[/bold red]")
        console.log("Wait 10 minutes, or sign in (set IG_USERNAME/IG_PASSWORD).")
        sys.exit(3)

    write_json(out / "instagram.json", manifest)
    console.log(f"[bold green]Done. {len(manifest)} posts → {out}[/bold green]")


if __name__ == "__main__":
    scrape()
```

- [ ] **Step 2: Run real scrape**

```bash
python tools/scrape_instagram.py
```

Expected: `.tmp/raw_scrape/instagram/` populated, or exit code 2/3 if blocked. If exit 3, set credentials in `.env` and re-run.

- [ ] **Step 3: Commit**

```bash
git add tools/scrape_instagram.py
git commit -m "feat(phase-1): instagram scraper (anonymous + optional login)"
```

---

### Task 10: Deduplicate images via perceptual hash

**Files:**
- Create: `tools/dedup.py`, `tools/tests/test_dedup.py`

- [ ] **Step 1: Write failing test**

`tools/tests/test_dedup.py`:

```python
from PIL import Image
from pathlib import Path
from tools.dedup import find_duplicates


def _make(path: Path, color):
    Image.new("RGB", (64, 64), color).save(path, "JPEG")


def test_finds_identical_images(tmp_path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    c = tmp_path / "c.jpg"
    _make(a, "red")
    _make(b, "red")
    _make(c, "blue")
    dups = find_duplicates([a, b, c])
    assert any({a, b}.issubset(set(group)) for group in dups)
    assert not any(c in group for group in dups)
```

- [ ] **Step 2: Verify fail**

```bash
pytest tools/tests/test_dedup.py -v
```

Expected: ImportError.

- [ ] **Step 3: Implement `tools/dedup.py`**

```python
"""Group near-duplicate images by perceptual hash."""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from PIL import Image
import imagehash


def find_duplicates(paths: list[Path], threshold: int = 4) -> list[list[Path]]:
    hashes = {}
    for p in paths:
        try:
            hashes[p] = imagehash.phash(Image.open(p))
        except Exception:
            continue
    seen: set[Path] = set()
    groups: list[list[Path]] = []
    items = list(hashes.items())
    for i, (p1, h1) in enumerate(items):
        if p1 in seen:
            continue
        group = [p1]
        for p2, h2 in items[i + 1 :]:
            if p2 in seen:
                continue
            if (h1 - h2) <= threshold:
                group.append(p2)
                seen.add(p2)
        if len(group) > 1:
            groups.append(group)
            seen.add(p1)
    return groups
```

- [ ] **Step 4: Run test**

```bash
pytest tools/tests/test_dedup.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/dedup.py tools/tests/test_dedup.py
git commit -m "feat(phase-1): perceptual-hash deduper"
```

---

### Task 11: Apply dedup to raw scrape

**Files:**
- Create: `tools/build_raw_manifest.py`

- [ ] **Step 1: Implement**

```python
"""Merge pavilhao3 + instagram raw scrapes, dedup, write master manifest."""
from __future__ import annotations
from pathlib import Path
from rich.console import Console

from tools._common import RAW, read_json, write_json
from tools.dedup import find_duplicates

console = Console()


def build():
    all_files = list((RAW / "pavilhao3").glob("*.jpg")) \
              + list((RAW / "pavilhao3").glob("*.jpeg")) \
              + list((RAW / "pavilhao3").glob("*.png")) \
              + list((RAW / "instagram").rglob("*.jpg"))
    console.log(f"Total raw files: {len(all_files)}")

    dup_groups = find_duplicates(all_files)
    console.log(f"Duplicate groups: {len(dup_groups)}")

    drop: set[Path] = set()
    for group in dup_groups:
        # Keep the largest file in each group
        keeper = max(group, key=lambda p: p.stat().st_size)
        for p in group:
            if p != keeper:
                drop.add(p)
    console.log(f"Dropping {len(drop)} duplicates")

    keep = [p for p in all_files if p not in drop]
    manifest = [
        {"path": str(p.relative_to(RAW.parent)), "source": p.parent.name, "size": p.stat().st_size}
        for p in keep
    ]
    write_json(RAW / "raw_manifest.json", manifest)
    console.log(f"[green]Kept {len(keep)} unique images → .tmp/raw_scrape/raw_manifest.json[/green]")


if __name__ == "__main__":
    build()
```

- [ ] **Step 2: Run**

```bash
python tools/build_raw_manifest.py
```

Expected: prints counts; writes `.tmp/raw_scrape/raw_manifest.json`.

- [ ] **Step 3: Commit**

```bash
git add tools/build_raw_manifest.py
git commit -m "feat(phase-1): merge + dedup raw scrape into master manifest"
```

---

### Task 12: Phase 1 user gate

- [ ] **Step 1: Print summary for user**

```bash
python -c "import json,pathlib; m=json.loads(pathlib.Path('.tmp/raw_scrape/raw_manifest.json').read_text()); print(f'Unique images: {len(m)}'); print(f'From pavilhao3: {sum(1 for x in m if x[\"source\"]==\"pavilhao3\")}'); print(f'From instagram: {sum(1 for x in m if x[\"source\"]==\"instagram\" or x[\"source\"]==\"pavilhao_3\")}')"
```

- [ ] **Step 2: User reviews**

Ask user: "Phase 1 gate — total of N unique images. Sufficient to proceed to classification + cleanup?"

- [ ] **Step 3: On approval, merge**

```bash
git checkout main
git merge phase-1-scrape --no-ff -m "merge: phase 1 scrape"
```

---

# PHASE 2 — Clean + optimize

Create branch:

```bash
git checkout -b phase-2-clean
```

### Task 13: Vision classifier — schema + fixture test

**Files:**
- Create: `tools/classify_logos.py`, `tools/tests/test_classify_logos.py`, `tools/tests/fixtures/sample_response.json`

- [ ] **Step 1: Save a fixture response**

`tools/tests/fixtures/sample_response.json`:

```json
{
  "has_watermark": true,
  "watermark_boxes": [
    {"x": 0.85, "y": 0.92, "w": 0.13, "h": 0.06, "label": "@pavilhao_3 corner watermark"}
  ],
  "physical_logos": [
    {"label": "client logo on booth wall — KEEP"}
  ],
  "quality": "portfolio_grade",
  "subject": "booth_exterior"
}
```

- [ ] **Step 2: Write failing test**

```python
import json
from pathlib import Path
from tools.classify_logos import ClassificationResult, parse_response

FIXTURE = Path(__file__).parent / "fixtures" / "sample_response.json"


def test_parse_response_returns_result():
    raw = FIXTURE.read_text(encoding="utf-8")
    result = parse_response(raw)
    assert isinstance(result, ClassificationResult)
    assert result.has_watermark is True
    assert len(result.watermark_boxes) == 1
    assert result.watermark_boxes[0].x == 0.85
    assert result.quality == "portfolio_grade"
```

- [ ] **Step 3: Verify fail**

```bash
pytest tools/tests/test_classify_logos.py -v
```

Expected: ImportError.

- [ ] **Step 4: Commit**

```bash
git add tools/tests/test_classify_logos.py tools/tests/fixtures/sample_response.json
git commit -m "test(phase-2): failing test for classification parser"
```

---

### Task 14: Vision classifier — implementation

**Files:**
- Create: `tools/classify_logos.py`

- [ ] **Step 1: Implement**

```python
"""Use Claude vision to classify watermark vs. physical logos in each image."""
from __future__ import annotations
import base64
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from anthropic import Anthropic
from rich.console import Console
from rich.progress import Progress

from tools._common import CLASSIFIED, RAW, read_json, write_json

console = Console()
MODEL = "claude-sonnet-4-6"

PROMPT = """\
You are classifying logos in a photo of an iGaming event booth.

Return JSON with EXACTLY this shape:
{
  "has_watermark": bool,
  "watermark_boxes": [{"x": float, "y": float, "w": float, "h": float, "label": str}],
  "physical_logos": [{"label": str}],
  "quality": "portfolio_grade" | "social_only" | "reject",
  "subject": "booth_exterior" | "booth_interior" | "crowd" | "team" | "detail" | "other"
}

Rules:
- watermark_boxes are normalized 0–1 coordinates (x,y = top-left; w,h = size).
- A WATERMARK is a logo/text overlay added on top of the photo by the publisher (e.g. an Instagram handle in the corner, a faded brand mark, repeating text pattern). It is NOT physically part of the scene.
- A PHYSICAL LOGO is a logo that exists IN the scene — on a booth wall, on a t-shirt, on signage, on a screen displayed at the booth. NEVER mark these as watermarks. They are social proof.
- quality: "portfolio_grade" = sharp, well-composed, shows booth or product clearly. "social_only" = usable but lower quality (motion blur, poor angle). "reject" = screenshot, meme, blurry, off-topic.

Respond with ONLY the JSON object, no prose."""


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
    data = json.loads(raw)
    return ClassificationResult(
        has_watermark=bool(data.get("has_watermark", False)),
        watermark_boxes=[Box(**b) for b in data.get("watermark_boxes", [])],
        physical_logos=list(data.get("physical_logos", [])),
        quality=data.get("quality", "social_only"),
        subject=data.get("subject", "other"),
    )


def classify_one(client: Anthropic, image_path: Path) -> ClassificationResult:
    media_type = "image/jpeg" if image_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
    msg = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
                {"type": "text", "text": PROMPT, "cache_control": {"type": "ephemeral"}},
            ],
        }],
    )
    text = msg.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    return parse_response(text)


def classify_all() -> None:
    manifest = read_json(RAW / "raw_manifest.json") or []
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    results = []
    with Progress() as progress:
        task = progress.add_task("Classifying", total=len(manifest))
        for entry in manifest:
            path = (RAW.parent / entry["path"]).resolve()
            try:
                result = classify_one(client, path)
                results.append({"path": entry["path"], **result.__dict__,
                                "watermark_boxes": [b.__dict__ for b in result.watermark_boxes]})
            except Exception as e:
                console.log(f"[red]{path.name}: {e}[/red]")
                results.append({"path": entry["path"], "error": str(e)})
            progress.advance(task)
    write_json(CLASSIFIED / "manifest.json", results)
    console.log(f"[bold green]Done. {len(results)} classified → .tmp/classified/manifest.json[/bold green]")


if __name__ == "__main__":
    classify_all()
```

- [ ] **Step 2: Run unit test**

```bash
pytest tools/tests/test_classify_logos.py -v
```

Expected: PASS.

- [ ] **Step 3: Run a tiny smoke test against 3 real images**

Modify temporarily to limit `manifest = manifest[:3]`, run `python tools/classify_logos.py`, inspect `.tmp/classified/manifest.json`. Revert the limit.

- [ ] **Step 4: Run full classification**

```bash
python tools/classify_logos.py
```

Expected: progress bar, then `.tmp/classified/manifest.json` with N entries. Cost reminder: ~$0.003/image.

- [ ] **Step 5: Commit**

```bash
git add tools/classify_logos.py
git commit -m "feat(phase-2): claude vision logo classifier"
```

---

### Task 15: Install IOPaint locally

**Files:** (none — system setup)

- [ ] **Step 1: Install IOPaint**

```bash
.venv\Scripts\activate
pip install iopaint
iopaint download --model lama
```

Expected: LaMa model downloads (~200MB) to `~/.cache/torch/`.

- [ ] **Step 2: Smoke test IOPaint CLI**

```bash
iopaint --help
```

Expected: help text prints.

- [ ] **Step 3: Note IOPaint version in workflow**

Update `workflows/scrape_and_clean_images.md` "Gotchas" section with the IOPaint version: `iopaint --version`.

- [ ] **Step 4: Commit workflow update**

```bash
git add workflows/scrape_and_clean_images.md
git commit -m "docs(phase-2): note iopaint version + install"
```

---

### Task 16: Inpaint watermarks

**Files:**
- Create: `tools/inpaint_watermarks.py`

- [ ] **Step 1: Implement**

```python
"""Inpaint watermark boxes using IOPaint (LaMa model)."""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw
from rich.console import Console
from rich.progress import Progress

from tools._common import CLASSIFIED, CLEANED, RAW, read_json

console = Console()
DIFFS = CLEANED / "_diffs"
DIFFS.mkdir(parents=True, exist_ok=True)


def build_mask(image_path: Path, boxes: list[dict], feather_px: int = 6) -> Path:
    """Build a white-on-black mask sized to the image."""
    img = Image.open(image_path)
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    for b in boxes:
        x1 = max(0, int(b["x"] * w) - feather_px)
        y1 = max(0, int(b["y"] * h) - feather_px)
        x2 = min(w, int((b["x"] + b["w"]) * w) + feather_px)
        y2 = min(h, int((b["y"] + b["h"]) * h) + feather_px)
        draw.rectangle([x1, y1, x2, y2], fill=255)
    mask_path = image_path.parent / (image_path.stem + "_mask.png")
    mask.save(mask_path)
    return mask_path


def make_diff(original: Path, cleaned: Path, dest: Path) -> None:
    a = Image.open(original).convert("RGB")
    b = Image.open(cleaned).convert("RGB")
    h = max(a.height, b.height)
    a = a.resize((int(a.width * h / a.height), h))
    b = b.resize((int(b.width * h / b.height), h))
    combined = Image.new("RGB", (a.width + b.width + 8, h), "black")
    combined.paste(a, (0, 0))
    combined.paste(b, (a.width + 8, 0))
    combined.save(dest, "PNG", optimize=True)


def inpaint_all() -> None:
    results = read_json(CLASSIFIED / "manifest.json") or []
    targets = [r for r in results if r.get("has_watermark") and r.get("watermark_boxes")]
    if not targets:
        console.log("[yellow]No watermarks flagged — copying classified images straight through.[/yellow]")
        for r in results:
            if r.get("quality") == "reject":
                continue
            src = (RAW.parent / r["path"]).resolve()
            dest = CLEANED / src.name
            if not dest.exists():
                dest.write_bytes(src.read_bytes())
        return

    with Progress() as progress:
        task = progress.add_task("Inpainting", total=len(targets))
        for r in targets:
            src = (RAW.parent / r["path"]).resolve()
            mask_path = build_mask(src, r["watermark_boxes"])
            cleaned_path = CLEANED / src.name
            cmd = [
                sys.executable, "-m", "iopaint", "run",
                "--model", "lama",
                "--device", "cpu",
                "--image", str(src),
                "--mask", str(mask_path),
                "--output", str(CLEANED),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            mask_path.unlink(missing_ok=True)
            make_diff(src, cleaned_path, DIFFS / (src.stem + ".png"))
            progress.advance(task)

    # Also copy the non-watermarked, non-reject images straight through.
    for r in results:
        if r.get("quality") == "reject" or r.get("has_watermark"):
            continue
        src = (RAW.parent / r["path"]).resolve()
        dest = CLEANED / src.name
        if not dest.exists():
            dest.write_bytes(src.read_bytes())

    console.log(f"[bold green]Done. Cleaned → .tmp/cleaned/  Diffs → .tmp/cleaned/_diffs/[/bold green]")


if __name__ == "__main__":
    inpaint_all()
```

- [ ] **Step 2: Run on smallest set first**

```bash
python tools/inpaint_watermarks.py
```

Expected: progress bar; `.tmp/cleaned/` populated; `.tmp/cleaned/_diffs/` has side-by-side PNGs.

- [ ] **Step 3: User review gate**

Ask user: "Open `.tmp/cleaned/_diffs/` and audit ~10 diffs. Any that look wrong (over-inpainted, missed watermarks, damaged physical content)?"

- [ ] **Step 4: If issues, capture them in workflow gotchas, then re-tune the prompt in `tools/classify_logos.py` and re-run from Task 14**

- [ ] **Step 5: Commit**

```bash
git add tools/inpaint_watermarks.py
git commit -m "feat(phase-2): iopaint watermark removal + side-by-side diffs"
```

---

### Task 17: Image optimizer (sharp via npx)

**Files:**
- Create: `tools/optimize_images.py`, `tools/optimize_images.mjs`

- [ ] **Step 1: Create `tools/optimize_images.mjs`** (Node script — sharp is best installed via npm)

```js
import sharp from 'sharp';
import { readdir, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const SRC  = '.tmp/cleaned';
const DEST = 'public/images/portfolio';
const WIDTHS = [640, 960, 1440, 1920];

const files = (await readdir(SRC, { withFileTypes: true }))
  .filter(f => f.isFile() && /\.(jpe?g|png|webp)$/i.test(f.name));

for (const f of files) {
  const slug = path.parse(f.name).name.toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-|-$/g, '');
  const outDir = path.join(DEST, slug);
  if (!existsSync(outDir)) await mkdir(outDir, { recursive: true });
  const input = path.join(SRC, f.name);
  for (const w of WIDTHS) {
    const base = sharp(input).resize({ width: w, withoutEnlargement: true });
    await base.clone().avif({ quality: 60 }).toFile(path.join(outDir, `${w}.avif`));
    await base.clone().webp({ quality: 78 }).toFile(path.join(outDir, `${w}.webp`));
  }
  console.log(`${slug} → ${WIDTHS.length} sizes × 2 formats`);
}
```

- [ ] **Step 2: Install `sharp`**

```bash
npm install --save-dev sharp
```

- [ ] **Step 3: Create `tools/optimize_images.py`** (Python wrapper that also emits the content manifest)

```python
"""Run the sharp optimizer (via Node) and emit src/content/portfolio.json."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from rich.console import Console

from tools._common import CLEANED, CLASSIFIED, ROOT, read_json

console = Console()
CONTENT = ROOT / "src" / "content"


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", name.lower())
    return re.sub(r"^-|-$", "", s)


def emit_content_manifest() -> None:
    classified = {r["path"].rsplit("/", 1)[-1]: r for r in (read_json(CLASSIFIED / "manifest.json") or [])}
    items = []
    for sub in (ROOT / "public" / "images" / "portfolio").iterdir():
        if not sub.is_dir():
            continue
        original_name = next(
            (n for n in classified if Path(n).stem.lower().replace("_", "-") == sub.name),
            None,
        )
        meta = classified.get(original_name, {}) if original_name else {}
        items.append({
            "slug": sub.name,
            "subject": meta.get("subject", "other"),
            "quality": meta.get("quality", "social_only"),
            "src_base": f"/images/portfolio/{sub.name}",
            "widths": [640, 960, 1440, 1920],
            "alt": meta.get("subject", "iGaming booth").replace("_", " "),
        })
    CONTENT.mkdir(parents=True, exist_ok=True)
    (CONTENT / "portfolio.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    console.log(f"[green]Wrote {len(items)} portfolio entries → src/content/portfolio.json[/green]")


def main() -> None:
    console.log("Running sharp optimizer…")
    subprocess.run(["node", "tools/optimize_images.mjs"], check=True)
    emit_content_manifest()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run optimizer**

```bash
python tools/optimize_images.py
```

Expected: `public/images/portfolio/<slug>/{640,960,1440,1920}.{avif,webp}` for each cleaned image. `src/content/portfolio.json` written.

- [ ] **Step 5: Force-add public/images for committing**

```bash
git add -f public/images/portfolio/
git add src/content/portfolio.json tools/optimize_images.py tools/optimize_images.mjs package.json package-lock.json
git commit -m "feat(phase-2): sharp optimizer + content manifest"
```

---

### Task 18: Phase 2 user gate

- [ ] **Step 1: Summarize for user**

```bash
python -c "import json,pathlib; p=json.loads(pathlib.Path('src/content/portfolio.json').read_text()); print(f'Portfolio entries: {len(p)}'); print(f'portfolio_grade: {sum(1 for x in p if x[\"quality\"]==\"portfolio_grade\")}')"
```

- [ ] **Step 2: Ask user to spot-check `.tmp/cleaned/_diffs/`**

- [ ] **Step 3: On approval, merge**

```bash
git checkout main
git merge phase-2-clean --no-ff -m "merge: phase 2 clean + optimize"
```

---

# PHASE 3 — Design system

Create branch:

```bash
git checkout -b phase-3-design-system
```

### Task 19: Nav + Footer components

**Files:**
- Create: `src/components/Nav.astro`, `src/components/Footer.astro`

- [ ] **Step 1: Create `src/components/Nav.astro`**

```astro
---
const links = [
  { href: '/', label: 'Home' },
  { href: '/services', label: 'Services' },
  { href: '/portfolio', label: 'Portfolio' },
  { href: '/about', label: 'About' },
  { href: '/contact', label: 'Contact' },
];
const current = Astro.url.pathname;
---
<nav class="sticky top-0 z-50 bg-bg/85 backdrop-blur border-b border-line">
  <div class="max-w-layout mx-auto flex items-center justify-between px-6 py-5">
    <a href="/" class="font-display text-xl tracking-tight">Gamingxpo<span class="text-accent">.</span></a>
    <ul class="hidden md:flex gap-8 text-sm">
      {links.map(l => (
        <li>
          <a href={l.href} class={`hover:text-accent transition-colors ${current === l.href ? 'text-accent' : 'text-fg/80'}`}>{l.label}</a>
        </li>
      ))}
    </ul>
    <a href="/contact" class="hidden md:inline-flex items-center gap-2 bg-accent text-bg font-medium px-4 py-2 rounded-full text-sm hover:opacity-90 transition">Start a project →</a>
  </div>
</nav>
```

- [ ] **Step 2: Create `src/components/Footer.astro`**

```astro
---
const year = new Date().getFullYear();
---
<footer class="border-t border-line mt-section">
  <div class="max-w-layout mx-auto px-6 py-12 grid md:grid-cols-3 gap-8 text-sm text-muted">
    <div>
      <div class="font-display text-fg text-lg">Gamingxpo<span class="text-accent">.</span></div>
      <p class="mt-2 max-w-prose">Premium booths and stands for the iGaming sector, worldwide.</p>
    </div>
    <div>
      <div class="text-fg font-medium">Contact</div>
      <p class="mt-2">hello@gamingxpo.com</p>
      <p>+351 — TBD</p>
    </div>
    <div>
      <div class="text-fg font-medium">Follow</div>
      <p class="mt-2"><a href="https://www.instagram.com/pavilhao_3" class="hover:text-accent">Instagram</a></p>
    </div>
  </div>
  <div class="border-t border-line">
    <div class="max-w-layout mx-auto px-6 py-4 flex justify-between text-xs text-muted">
      <span>© {year} Gamingxpo. All rights reserved.</span>
      <span>Site by Gamingxpo</span>
    </div>
  </div>
</footer>
```

- [ ] **Step 3: Wire Nav + Footer into Base layout**

Update `src/layouts/Base.astro`:

```astro
---
import Nav from '../components/Nav.astro';
import Footer from '../components/Footer.astro';
const { title = 'Gamingxpo' } = Astro.props;
---
<!doctype html>
<html lang="en" class="bg-bg">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  </head>
  <body class="font-sans antialiased bg-bg text-fg">
    <Nav />
    <slot />
    <Footer />
  </body>
</html>
```

- [ ] **Step 4: Verify in browser**

```bash
npm run dev
```

Visit `http://localhost:4321/` — sticky nav + footer visible.

- [ ] **Step 5: Commit**

```bash
git add src/components/Nav.astro src/components/Footer.astro src/layouts/Base.astro
git commit -m "feat(phase-3): nav + footer + base layout wiring"
```

---

### Task 20: Hero component

**Files:**
- Create: `src/components/Hero.astro`

- [ ] **Step 1: Write component**

```astro
---
import portfolio from '../content/portfolio.json';
const cover = portfolio.find(p => p.quality === 'portfolio_grade' && p.subject === 'booth_exterior') ?? portfolio[0];
const { eyebrow = 'Booths & Stands for iGaming', headline = 'Stand out at every iGaming event in the world.', sub = 'We design, build, and ship booths for SiGMA, ICE, G2E, BiS and everywhere your brand needs to win the room.', cta = { href: '/contact', label: 'Start your booth →' } } = Astro.props;
---
<section class="relative min-h-[88vh] overflow-hidden">
  {cover && (
    <picture class="absolute inset-0 -z-10">
      <source type="image/avif" srcset={`${cover.src_base}/1920.avif`} />
      <img src={`${cover.src_base}/1920.webp`} alt={cover.alt} class="w-full h-full object-cover scale-105 motion-safe:animate-[kenburns_24s_ease-out_infinite_alternate]" />
    </picture>
  )}
  <div class="absolute inset-0 -z-10 bg-gradient-to-b from-bg/40 via-bg/60 to-bg" />
  <div class="max-w-layout mx-auto px-6 pt-32 pb-section flex flex-col justify-end min-h-[88vh]">
    <p class="text-accent text-sm tracking-[0.2em] uppercase">{eyebrow}</p>
    <h1 class="font-display text-display-xl max-w-[14ch] mt-3">{headline}</h1>
    <p class="mt-6 max-w-prose text-fg/80 text-body">{sub}</p>
    <div class="mt-8 flex gap-4">
      <a href={cta.href} class="inline-flex items-center gap-2 bg-accent text-bg font-medium px-6 py-3 rounded-full hover:opacity-90 transition">{cta.label}</a>
      <a href="/portfolio" class="inline-flex items-center gap-2 border border-line text-fg px-6 py-3 rounded-full hover:border-accent transition">See portfolio</a>
    </div>
  </div>
</section>

<style>
  @keyframes kenburns {
    from { transform: scale(1.05); }
    to   { transform: scale(1.15) translate(-1%, -1%); }
  }
</style>
```

- [ ] **Step 2: Render Hero on homepage**

Update `src/pages/index.astro`:

```astro
---
import Base from '../layouts/Base.astro';
import Hero from '../components/Hero.astro';
---
<Base title="Gamingxpo — Booths & Stands for iGaming">
  <Hero />
</Base>
```

- [ ] **Step 3: Verify**

```bash
npm run dev
```

Visit `/` — full-bleed hero with image, headline in Inter Tight, accent CTA. Ken Burns animation slowly zooming.

- [ ] **Step 4: Commit**

```bash
git add src/components/Hero.astro src/pages/index.astro
git commit -m "feat(phase-3): hero component with ken-burns + portfolio cover"
```

---

### Task 21: SectionHeader + MetricStrip + MarqueeBrands

**Files:**
- Create: `src/components/SectionHeader.astro`, `src/components/MetricStrip.astro`, `src/components/MarqueeBrands.astro`

- [ ] **Step 1: `SectionHeader.astro`**

```astro
---
const { eyebrow, title, kicker } = Astro.props;
---
<header class="max-w-layout mx-auto px-6 py-section">
  {eyebrow && <p class="text-accent text-sm tracking-[0.2em] uppercase">{eyebrow}</p>}
  <h2 class="font-display text-display-lg mt-3 max-w-[18ch]">{title}</h2>
  {kicker && <p class="mt-4 max-w-prose text-body text-fg/80">{kicker}</p>}
</header>
```

- [ ] **Step 2: `MetricStrip.astro`**

```astro
---
const { items = [
  { value: '200+', label: 'booths built' },
  { value: '14', label: 'countries' },
  { value: '9', label: 'years' },
  { value: '40+', label: 'iGaming clients' },
] } = Astro.props;
---
<section class="border-y border-line">
  <div class="max-w-layout mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8">
    {items.map(i => (
      <div>
        <div class="font-display text-display-md text-accent">{i.value}</div>
        <div class="text-muted text-sm mt-1">{i.label}</div>
      </div>
    ))}
  </div>
</section>
```

- [ ] **Step 3: `MarqueeBrands.astro`**

```astro
---
const { items = ['SiGMA','ICE London','G2E Las Vegas','BiS SiGMA','GAT Expo','iGaming Next','SBC Summit'] } = Astro.props;
---
<section class="overflow-hidden border-y border-line">
  <div class="flex gap-16 py-8 whitespace-nowrap motion-safe:animate-[marquee_30s_linear_infinite]">
    {[...items, ...items].map(name => (
      <span class="font-display text-2xl text-muted hover:text-fg transition-colors">{name}</span>
    ))}
  </div>
</section>

<style>
  @keyframes marquee {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
  }
</style>
```

- [ ] **Step 4: Commit**

```bash
git add src/components/SectionHeader.astro src/components/MetricStrip.astro src/components/MarqueeBrands.astro
git commit -m "feat(phase-3): section header, metric strip, marquee brands"
```

---

### Task 22: CaseCard + ServiceTile

**Files:**
- Create: `src/components/CaseCard.astro`, `src/components/ServiceTile.astro`

- [ ] **Step 1: `CaseCard.astro`**

```astro
---
const { slug, title, event, year, src_base, alt } = Astro.props;
---
<a href={`/portfolio/${slug}`} class="group block">
  <div class="aspect-[4/3] overflow-hidden bg-line">
    <picture>
      <source type="image/avif" srcset={`${src_base}/640.avif 640w, ${src_base}/960.avif 960w, ${src_base}/1440.avif 1440w`} sizes="(min-width: 768px) 33vw, 100vw" />
      <img src={`${src_base}/960.webp`} alt={alt} class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" loading="lazy" />
    </picture>
  </div>
  <div class="pt-4">
    <div class="text-xs text-muted uppercase tracking-widest">{event ?? '—'} · {year ?? ''}</div>
    <div class="text-display-md font-display mt-1 group-hover:text-accent transition-colors">{title ?? alt}</div>
  </div>
</a>
```

- [ ] **Step 2: `ServiceTile.astro`**

```astro
---
const { title, blurb, src_base, alt, href } = Astro.props;
---
<a href={href ?? '/services'} class="group block border border-line p-6 hover:border-accent transition-colors">
  {src_base && (
    <div class="aspect-[16/10] overflow-hidden bg-bg mb-6">
      <img src={`${src_base}/960.webp`} alt={alt} class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" loading="lazy" />
    </div>
  )}
  <div class="font-display text-display-md">{title}</div>
  <p class="text-muted mt-2 max-w-prose">{blurb}</p>
  <span class="inline-block mt-4 text-accent text-sm">Learn more →</span>
</a>
```

- [ ] **Step 3: Commit**

```bash
git add src/components/CaseCard.astro src/components/ServiceTile.astro
git commit -m "feat(phase-3): case card + service tile"
```

---

### Task 23: FilterBar + ContactSplit

**Files:**
- Create: `src/components/FilterBar.astro`, `src/components/ContactSplit.astro`

- [ ] **Step 1: `FilterBar.astro`**

```astro
---
const { groups = [] } = Astro.props;
// groups: [{name: 'Event', key: 'event', options: ['SiGMA','ICE','G2E']}]
---
<div class="border-b border-line">
  <div class="max-w-layout mx-auto px-6 py-6 flex flex-wrap gap-6" data-filter-bar>
    {groups.map(g => (
      <div class="flex flex-wrap gap-2 items-center">
        <span class="text-xs uppercase tracking-widest text-muted">{g.name}:</span>
        <button data-filter-key={g.key} data-filter-value="*" class="filter-chip is-active">All</button>
        {g.options.map(o => (
          <button data-filter-key={g.key} data-filter-value={o} class="filter-chip">{o}</button>
        ))}
      </div>
    ))}
  </div>
</div>

<style>
  .filter-chip { @apply text-sm px-3 py-1 rounded-full border border-line text-fg/80 hover:border-accent transition; }
  .filter-chip.is-active { @apply bg-accent text-bg border-accent; }
</style>

<script>
  const bar = document.querySelector('[data-filter-bar]') as HTMLElement | null;
  if (bar) {
    const state: Record<string,string> = {};
    bar.addEventListener('click', (e) => {
      const btn = (e.target as HTMLElement).closest('[data-filter-key]') as HTMLElement | null;
      if (!btn) return;
      const key = btn.dataset.filterKey!;
      const value = btn.dataset.filterValue!;
      state[key] = value;
      bar.querySelectorAll(`[data-filter-key="${key}"]`).forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      try { localStorage.setItem('gx_filters', JSON.stringify(state)); } catch {}
      document.querySelectorAll('[data-card]').forEach(card => {
        const el = card as HTMLElement;
        const visible = Object.entries(state).every(([k,v]) => v === '*' || el.dataset[k] === v);
        el.style.display = visible ? '' : 'none';
      });
    });
    try {
      const saved = JSON.parse(localStorage.getItem('gx_filters') || '{}');
      for (const [k,v] of Object.entries(saved)) {
        const btn = bar.querySelector(`[data-filter-key="${k}"][data-filter-value="${v}"]`) as HTMLElement | null;
        btn?.click();
      }
    } catch {}
  }
</script>
```

- [ ] **Step 2: `ContactSplit.astro`**

```astro
---
const { email = 'hello@gamingxpo.com', whatsapp = '+351000000000' } = Astro.props;
---
<section class="border-t border-line">
  <div class="max-w-layout mx-auto px-6 py-section grid md:grid-cols-2 gap-12">
    <div>
      <h2 class="font-display text-display-lg">Tell us about your event.</h2>
      <p class="mt-4 max-w-prose text-fg/80">We'll come back with a concept, a render, and a budget — usually within 48 hours.</p>
      <ul class="mt-8 space-y-2 text-fg/80">
        <li>Email: <a href={`mailto:${email}`} class="text-accent">{email}</a></li>
        <li>WhatsApp: <a href={`https://wa.me/${whatsapp.replace(/[^0-9]/g,'')}`} class="text-accent">{whatsapp}</a></li>
      </ul>
    </div>
    <form class="space-y-4" data-mockup-form>
      <input class="w-full bg-bg border border-line px-4 py-3" placeholder="Your name" name="name" required />
      <input class="w-full bg-bg border border-line px-4 py-3" placeholder="Company" name="company" />
      <input class="w-full bg-bg border border-line px-4 py-3" placeholder="Email" type="email" name="email" required />
      <select class="w-full bg-bg border border-line px-4 py-3" name="event">
        <option value="">Event (optional)</option>
        <option>SiGMA Malta</option><option>SiGMA Europe</option><option>ICE London</option>
        <option>G2E Las Vegas</option><option>BiS SiGMA</option><option>Other</option>
      </select>
      <textarea class="w-full bg-bg border border-line px-4 py-3 h-32" placeholder="Project notes (size, dates, references)" name="notes"></textarea>
      <button class="bg-accent text-bg font-medium px-6 py-3 rounded-full hover:opacity-90 transition">Send (mockup)</button>
      <p class="text-xs text-muted">This form is a placeholder — a real backend lands in a later milestone.</p>
    </form>
  </div>
</section>

<script>
  document.querySelectorAll('[data-mockup-form]').forEach(f => {
    f.addEventListener('submit', e => {
      e.preventDefault();
      (f as HTMLElement).innerHTML = '<div class="text-display-md font-display text-accent">Thanks — we\'ll be in touch.</div><p class="text-muted mt-2">(Mock success: no message was sent.)</p>';
    });
  });
</script>
```

- [ ] **Step 3: Commit**

```bash
git add src/components/FilterBar.astro src/components/ContactSplit.astro
git commit -m "feat(phase-3): filter bar + contact split (mockup form)"
```

---

### Task 24: Styleguide page

**Files:**
- Create: `src/pages/__styleguide.astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../layouts/Base.astro';
import Hero from '../components/Hero.astro';
import SectionHeader from '../components/SectionHeader.astro';
import MetricStrip from '../components/MetricStrip.astro';
import MarqueeBrands from '../components/MarqueeBrands.astro';
import CaseCard from '../components/CaseCard.astro';
import ServiceTile from '../components/ServiceTile.astro';
import FilterBar from '../components/FilterBar.astro';
import ContactSplit from '../components/ContactSplit.astro';
import portfolio from '../content/portfolio.json';

const sample = portfolio[0];
---
<Base title="Styleguide">
  <Hero />
  <MetricStrip />
  <MarqueeBrands />
  <SectionHeader eyebrow="Case studies" title="What we’ve built." kicker="A sample of the most recent stands we’ve produced for iGaming clients across Europe and LATAM." />
  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-3 gap-8">
    {portfolio.slice(0,6).map(p => <CaseCard {...p} title={p.alt} event="SiGMA Malta" year={2025} />)}
  </div>
  <SectionHeader eyebrow="Services" title="What we do." />
  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-3 gap-8">
    {['Design','Build','Branding','AV / Tech','On-site assembly'].map(s => (
      <ServiceTile title={s} blurb="Brief description of the service goes here." src_base={sample?.src_base} alt={s} />
    ))}
  </div>
  <FilterBar groups={[
    {name:'Event', key:'event', options:['SiGMA','ICE','G2E','BiS']},
    {name:'Year',  key:'year',  options:['2024','2025']},
  ]} />
  <ContactSplit />
</Base>
```

- [ ] **Step 2: Verify in browser**

```bash
npm run dev
```

Visit `http://localhost:4321/__styleguide`. Confirm every component renders without overlap.

- [ ] **Step 3: Screenshot via Playwright**

Capture full-page screenshot via the `webapp-testing` skill, save to `.tmp/phase-3-styleguide.png`.

- [ ] **Step 4: User gate**

Show user the screenshot. Iterate on spacing, color, or component design until approved.

- [ ] **Step 5: Commit**

```bash
git add src/pages/__styleguide.astro
git commit -m "feat(phase-3): styleguide page assembling all components"
```

---

### Task 25: Phase 3 merge

- [ ] **Step 1: After user approves styleguide**

```bash
git checkout main
git merge phase-3-design-system --no-ff -m "merge: phase 3 design system"
```

---

# PHASE 4 — Page assembly

Create branch:

```bash
git checkout -b phase-4-pages
```

### Task 26: Content collections for portfolio + services

**Files:**
- Create: `src/content/config.ts`
- Create: `src/content/services/design.md`, `build.md`, `branding.md`, `av-tech.md`, `on-site.md`

- [ ] **Step 1: `src/content/config.ts`**

```ts
import { defineCollection, z } from 'astro:content';

const services = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    intro: z.string(),
    deliverables: z.array(z.string()),
    featured_portfolio_slugs: z.array(z.string()).optional(),
  }),
});

export const collections = { services };
```

- [ ] **Step 2: Create 5 service MDs**

`src/content/services/design.md`:

```markdown
---
title: Design
intro: From mood board to 3D render in days, not weeks. Booth concepts grounded in your brand and the way your event audience actually moves through a hall.
deliverables:
  - Concept moodboards
  - 3D renders & walkthroughs
  - Final technical drawings
  - Material & lighting spec
---
We start with a one-hour discovery call and a quick sketch, not a 60-page brief. Then we render, iterate, and lock the design — usually inside a week — so production can begin without rework.
```

`src/content/services/build.md`:

```markdown
---
title: Build
intro: Fabrication in our workshops, then trucked or shipped to wherever your event lands.
deliverables:
  - Custom carpentry & metalwork
  - Modular reusable systems
  - Crates & global freight
  - Insurance handled
---
We build everything in-house so quality is consistent. Reusable modular systems mean you can re-stage the same booth at three events for the cost of one custom build.
```

`src/content/services/branding.md`:

```markdown
---
title: Branding
intro: Large-format graphics, signage, and lighting design that read clearly from 30 metres away.
deliverables:
  - Large-format printing
  - Vinyl & 3D lettering
  - LED & ambient lighting
  - Brand guidelines for booths
---
A booth lives or dies at the first three seconds of eye contact. We design the brand hits to land at distance, then refine the close-in details so the booth rewards a longer look.
```

`src/content/services/av-tech.md`:

```markdown
---
title: AV & Tech
intro: Screens, interactive demos, and the wiring nobody sees.
deliverables:
  - LED video walls
  - Touchscreen demos
  - Audio & lighting control
  - On-stand wifi & device fleet
---
We supply, install, and operate the full AV stack. If you want a slot machine playing live or a Vegas-grade LED wall, we wire it, drive it, and break it down.
```

`src/content/services/on-site.md`:

```markdown
---
title: On-site Assembly
intro: Our crew lands before you do and packs up after.
deliverables:
  - Build & teardown
  - On-site technicians
  - Daily refresh & cleaning
  - Emergency repair
---
Every project ships with a named on-site lead. They handle venue rules, freight check-in, last-minute changes, and the things you don't want your marketing team thinking about.
```

- [ ] **Step 3: Commit**

```bash
git add src/content/
git commit -m "feat(phase-4): content collections + 5 service entries"
```

---

### Task 27: Homepage build

**Files:**
- Modify: `src/pages/index.astro`

- [ ] **Step 1: Replace homepage**

```astro
---
import Base from '../layouts/Base.astro';
import Hero from '../components/Hero.astro';
import SectionHeader from '../components/SectionHeader.astro';
import MetricStrip from '../components/MetricStrip.astro';
import MarqueeBrands from '../components/MarqueeBrands.astro';
import CaseCard from '../components/CaseCard.astro';
import ServiceTile from '../components/ServiceTile.astro';
import ContactSplit from '../components/ContactSplit.astro';
import { getCollection } from 'astro:content';
import portfolio from '../content/portfolio.json';

const services = await getCollection('services');
const featured = portfolio.filter(p => p.quality === 'portfolio_grade').slice(0, 6);
---
<Base title="Gamingxpo — Booths & Stands for iGaming">
  <Hero />
  <MetricStrip />

  <SectionHeader eyebrow="Selected work" title="Booths that earn the room." kicker="A small sample. Every booth we've built was custom-designed for the event, the brand, and the crowd in front of it." />
  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-2 lg:grid-cols-3 gap-8">
    {featured.map(p => <CaseCard {...p} title={p.alt} event="iGaming event" year={2025} />)}
  </div>

  <div class="max-w-layout mx-auto px-6 mt-section text-center">
    <a href="/portfolio" class="inline-flex items-center gap-2 border border-line text-fg px-6 py-3 rounded-full hover:border-accent transition">See all projects →</a>
  </div>

  <SectionHeader eyebrow="What we do" title="Five things, done end-to-end." kicker="From the first concept sketch to the moment our crew packs up after the show." />
  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-3 gap-8">
    {services.slice(0,5).map(s => (
      <ServiceTile title={s.data.title} blurb={s.data.intro} href={`/services#${s.slug}`} />
    ))}
  </div>

  <MarqueeBrands />
  <ContactSplit />
</Base>
```

- [ ] **Step 2: Verify**

```bash
npm run dev
```

Visit `/` — full page renders, no console errors.

- [ ] **Step 3: Commit**

```bash
git add src/pages/index.astro
git commit -m "feat(phase-4): homepage assembled"
```

---

### Task 28: Services page

**Files:**
- Create: `src/pages/services.astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../layouts/Base.astro';
import SectionHeader from '../components/SectionHeader.astro';
import ContactSplit from '../components/ContactSplit.astro';
import { getCollection } from 'astro:content';

const services = await getCollection('services');
---
<Base title="Services — Gamingxpo">
  <SectionHeader eyebrow="Services" title="From concept to teardown." kicker="Five disciplines. One in-house team. Every booth shipped on the date written on the contract." />

  <div class="max-w-layout mx-auto px-6 space-y-section pb-section">
    {services.map(async (s) => {
      const { Content } = await s.render();
      return (
        <article id={s.slug} class="grid md:grid-cols-12 gap-8 border-t border-line pt-12 scroll-mt-24">
          <div class="md:col-span-4">
            <p class="text-accent text-sm tracking-[0.2em] uppercase">{s.data.title}</p>
          </div>
          <div class="md:col-span-8 max-w-prose">
            <h2 class="font-display text-display-lg">{s.data.intro}</h2>
            <div class="mt-6 prose prose-invert text-fg/80"><Content /></div>
            <ul class="mt-6 grid grid-cols-2 gap-2 text-sm text-muted">
              {s.data.deliverables.map(d => <li>· {d}</li>)}
            </ul>
          </div>
        </article>
      );
    })}
  </div>

  <ContactSplit />
</Base>
```

- [ ] **Step 2: Install Tailwind typography (for `prose` classes)**

```bash
npm install -D @tailwindcss/typography
```

Update `tailwind.config.cjs` `plugins`:

```js
plugins: [require('@tailwindcss/typography')],
```

- [ ] **Step 3: Verify**

```bash
npm run dev
```

Visit `/services` — 5 service sections rendered, anchors work (`/services#design`).

- [ ] **Step 4: Commit**

```bash
git add src/pages/services.astro tailwind.config.cjs package.json package-lock.json
git commit -m "feat(phase-4): services page + tailwind typography"
```

---

### Task 29: Portfolio index page with filters

**Files:**
- Create: `src/pages/portfolio.astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../layouts/Base.astro';
import SectionHeader from '../components/SectionHeader.astro';
import CaseCard from '../components/CaseCard.astro';
import FilterBar from '../components/FilterBar.astro';
import portfolio from '../content/portfolio.json';

const items = portfolio.filter(p => p.quality !== 'reject');
const events = Array.from(new Set(items.map(p => p.event ?? 'Other'))).sort();
const years = Array.from(new Set(items.map(p => String(p.year ?? '2025')))).sort();
---
<Base title="Portfolio — Gamingxpo">
  <SectionHeader eyebrow="Portfolio" title="The room, the booth, the brand." kicker="Filter by event, year, or scope. Every project tells the same story differently: the brand had a moment to be unmissable, and we built that moment." />
  <FilterBar groups={[
    {name:'Event', key:'event', options:events},
    {name:'Year',  key:'year',  options:years},
  ]} />
  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-2 lg:grid-cols-3 gap-8 py-section">
    {items.map(p => (
      <div data-card data-event={p.event ?? 'Other'} data-year={String(p.year ?? '2025')}>
        <CaseCard {...p} title={p.alt} event={p.event ?? '—'} year={p.year ?? 2025} />
      </div>
    ))}
  </div>
</Base>
```

- [ ] **Step 2: Verify filter behaviour**

```bash
npm run dev
```

Visit `/portfolio` — click filter chips, grid filters. Reload page, last filter restored from localStorage.

- [ ] **Step 3: Commit**

```bash
git add src/pages/portfolio.astro
git commit -m "feat(phase-4): portfolio grid with filters"
```

---

### Task 30: Case-study detail pages

**Files:**
- Create: `src/pages/portfolio/[slug].astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../../layouts/Base.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import ContactSplit from '../../components/ContactSplit.astro';
import portfolio from '../../content/portfolio.json';

export function getStaticPaths() {
  return portfolio.filter(p => p.quality !== 'reject').map(p => ({
    params: { slug: p.slug },
    props: { item: p },
  }));
}

const { item } = Astro.props;
const others = portfolio.filter(p => p.slug !== item.slug && p.quality === 'portfolio_grade').slice(0, 3);
---
<Base title={`${item.alt} — Gamingxpo Portfolio`}>
  <section class="relative min-h-[70vh]">
    <picture class="absolute inset-0 -z-10">
      <source type="image/avif" srcset={`${item.src_base}/1920.avif`} />
      <img src={`${item.src_base}/1920.webp`} alt={item.alt} class="w-full h-full object-cover" />
    </picture>
    <div class="absolute inset-0 -z-10 bg-gradient-to-b from-bg/30 via-bg/40 to-bg" />
    <div class="max-w-layout mx-auto px-6 pt-32 pb-24 flex flex-col justify-end min-h-[70vh]">
      <p class="text-accent text-sm tracking-[0.2em] uppercase">Case study</p>
      <h1 class="font-display text-display-xl max-w-[20ch] mt-3 capitalize">{item.alt}</h1>
    </div>
  </section>

  <article class="max-w-layout mx-auto px-6 py-section grid md:grid-cols-12 gap-8">
    <aside class="md:col-span-4 space-y-6 text-sm text-muted">
      <div><div class="text-fg font-medium">Subject</div><div class="capitalize">{item.subject?.replace('_',' ')}</div></div>
      <div><div class="text-fg font-medium">Quality tier</div><div class="capitalize">{item.quality}</div></div>
    </aside>
    <div class="md:col-span-8 prose prose-invert max-w-prose">
      <h2>The brief</h2>
      <p>Each project is custom-designed for the brand and the venue. Detailed case notes for this stand will be added during the launch polish phase.</p>
      <h2>What we built</h2>
      <p>Custom carpentry, large-format graphics, ambient lighting, and on-site assembly.</p>
    </div>
  </article>

  <SectionHeader eyebrow="More work" title="Other booths." />
  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-3 gap-8">
    {others.map(p => (
      <a href={`/portfolio/${p.slug}`} class="group block">
        <div class="aspect-[4/3] overflow-hidden bg-line">
          <img src={`${p.src_base}/960.webp`} alt={p.alt} class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" loading="lazy" />
        </div>
        <div class="pt-3 font-display group-hover:text-accent transition-colors">{p.alt}</div>
      </a>
    ))}
  </div>

  <ContactSplit />
</Base>
```

- [ ] **Step 2: Verify**

```bash
npm run build
```

Expected: build succeeds, prints N portfolio detail pages generated.

```bash
npm run dev
```

Click any portfolio card; case-study page renders.

- [ ] **Step 3: Commit**

```bash
git add src/pages/portfolio/
git commit -m "feat(phase-4): case-study detail pages"
```

---

### Task 31: About page

**Files:**
- Create: `src/pages/about.astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../layouts/Base.astro';
import SectionHeader from '../components/SectionHeader.astro';
import MetricStrip from '../components/MetricStrip.astro';
import MarqueeBrands from '../components/MarqueeBrands.astro';
import ContactSplit from '../components/ContactSplit.astro';
import portfolio from '../content/portfolio.json';

const cover = portfolio.find(p => p.quality === 'portfolio_grade') ?? portfolio[0];
---
<Base title="About — Gamingxpo">
  <SectionHeader eyebrow="About" title="A booth builder for the iGaming era." kicker="We started building stands for a Portuguese trade-show audience. Today we ship booths to wherever iGaming pitches its tent: Malta, London, Las Vegas, São Paulo, Cape Town." />

  {cover && (
    <div class="max-w-layout mx-auto px-6">
      <picture>
        <source type="image/avif" srcset={`${cover.src_base}/1920.avif`} />
        <img src={`${cover.src_base}/1920.webp`} alt={cover.alt} class="w-full aspect-[21/9] object-cover" loading="lazy" />
      </picture>
    </div>
  )}

  <MetricStrip />

  <div class="max-w-layout mx-auto px-6 py-section grid md:grid-cols-12 gap-8">
    <aside class="md:col-span-4">
      <p class="text-accent text-sm tracking-[0.2em] uppercase">Why us</p>
    </aside>
    <div class="md:col-span-8 max-w-prose space-y-6 text-fg/80 text-body">
      <p>The iGaming industry runs on a calendar of events. Operators that show up sharp at SiGMA, ICE, and G2E close deals. Ones that don't, disappear into the noise.</p>
      <p>We take that calendar seriously. Every booth we build is designed for the specific event — the booth that wins at SiGMA Malta is not the booth that wins at G2E Las Vegas. We know the difference, we know the halls, and we know the audience.</p>
      <p>We own the build end-to-end: design, fabrication, AV, branding, on-site crew. One vendor, one accountable lead, one budget. No subcontractor chains.</p>
    </div>
  </div>

  <MarqueeBrands />
  <ContactSplit />
</Base>
```

- [ ] **Step 2: Verify**

```bash
npm run dev
```

Visit `/about`.

- [ ] **Step 3: Commit**

```bash
git add src/pages/about.astro
git commit -m "feat(phase-4): about page"
```

---

### Task 32: Contact page (mockup-only)

**Files:**
- Create: `src/pages/contact.astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../layouts/Base.astro';
import SectionHeader from '../components/SectionHeader.astro';
import ContactSplit from '../components/ContactSplit.astro';
---
<Base title="Contact — Gamingxpo">
  <SectionHeader eyebrow="Contact" title="Let's build something unmissable." kicker="Tell us the event, the date, and the size of your booth. We'll respond with a concept, a render, and a budget — usually within 48 hours." />
  <ContactSplit />
</Base>
```

- [ ] **Step 2: Verify**

```bash
npm run dev
```

Submit the form — confirm static success state appears.

- [ ] **Step 3: Commit**

```bash
git add src/pages/contact.astro
git commit -m "feat(phase-4): contact page (mockup form)"
```

---

### Task 33: Phase 4 user gate

- [ ] **Step 1: Take screenshots of all 5 pages**

Use `webapp-testing` skill or `seo-visual` subagent to screenshot:
- `/`
- `/services`
- `/portfolio`
- `/portfolio/<first-slug>`
- `/about`
- `/contact`

Save to `.tmp/phase-4-screenshots/`.

- [ ] **Step 2: User walks the preview**

Ask user to load `localhost:4321` and click through every page. Capture any copy or layout requests.

- [ ] **Step 3: Iterate until approved, then merge**

```bash
git checkout main
git merge phase-4-pages --no-ff -m "merge: phase 4 pages"
```

---

# PHASE 5 — Launch polish

Create branch:

```bash
git checkout -b phase-5-polish
```

### Task 34: SEO metadata + OG images

**Files:**
- Modify: `src/layouts/Base.astro`
- Create: `src/components/SEO.astro`

- [ ] **Step 1: `src/components/SEO.astro`**

```astro
---
const {
  title = 'Gamingxpo',
  description = 'Premium booths and stands for the iGaming sector, worldwide.',
  image = '/images/brand/og-default.jpg',
  url = Astro.url.href,
} = Astro.props;
const siteUrl = import.meta.env.PUBLIC_SITE_URL || 'https://gamingxpo.com';
const fullImg = image.startsWith('http') ? image : `${siteUrl}${image}`;
---
<title>{title}</title>
<meta name="description" content={description} />
<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={fullImg} />
<meta property="og:url" content={url} />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="canonical" href={url} />
```

- [ ] **Step 2: Wire SEO into `Base.astro`**

Replace `<title>{title}</title>` block with:

```astro
import SEO from '../components/SEO.astro';
const { title, description, ogImage } = Astro.props;
```

And in `<head>`:

```astro
<SEO title={title} description={description} image={ogImage} />
```

- [ ] **Step 3: Create default OG image**

Place a 1200×630 PNG/JPG at `public/images/brand/og-default.jpg` (use a portfolio cover with a dark overlay and "Gamingxpo" wordmark — generate via a one-off Node script if needed, or screenshot the homepage hero).

- [ ] **Step 4: Commit**

```bash
git add src/components/SEO.astro src/layouts/Base.astro public/images/brand/
git commit -m "feat(phase-5): SEO meta + default OG image"
```

---

### Task 35: Sitemap + robots

**Files:** auto-generated config

- [ ] **Step 1: Install sitemap integration**

```bash
npx astro add sitemap --yes
```

- [ ] **Step 2: Update `astro.config.mjs`**

```js
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://gamingxpo.com',
  integrations: [tailwind(), sitemap()],
});
```

- [ ] **Step 3: Create `public/robots.txt`**

```
User-agent: *
Allow: /
Sitemap: https://gamingxpo.com/sitemap-index.xml
```

- [ ] **Step 4: Build + verify**

```bash
npm run build
```

Expected: `dist/sitemap-index.xml` and `dist/sitemap-0.xml` written, listing every page.

- [ ] **Step 5: Commit**

```bash
git add astro.config.mjs public/robots.txt package.json package-lock.json
git commit -m "feat(phase-5): sitemap + robots"
```

---

### Task 36: 404 page

**Files:**
- Create: `src/pages/404.astro`

- [ ] **Step 1: Implement**

```astro
---
import Base from '../layouts/Base.astro';
---
<Base title="404 — Gamingxpo">
  <main class="min-h-[70vh] flex flex-col items-center justify-center text-center px-6">
    <p class="text-accent text-sm tracking-[0.2em] uppercase">404</p>
    <h1 class="font-display text-display-xl mt-3">This stand wasn't built.</h1>
    <p class="mt-4 max-w-prose text-fg/80">The page you were looking for doesn't exist. Try the <a href="/portfolio" class="text-accent">portfolio</a> or the <a href="/" class="text-accent">home page</a>.</p>
  </main>
</Base>
```

- [ ] **Step 2: Commit**

```bash
git add src/pages/404.astro
git commit -m "feat(phase-5): 404 page"
```

---

### Task 37: Plausible analytics (privacy-friendly)

**Files:**
- Modify: `src/layouts/Base.astro`

- [ ] **Step 1: Add Plausible script**

In `Base.astro` `<head>`:

```astro
{import.meta.env.PROD && (
  <script defer data-domain="gamingxpo.com" src="https://plausible.io/js/script.js"></script>
)}
```

- [ ] **Step 2: Commit**

```bash
git add src/layouts/Base.astro
git commit -m "feat(phase-5): plausible analytics (prod only)"
```

---

### Task 38: Remove `__styleguide` from production build

**Files:**
- Modify: `astro.config.mjs`

- [ ] **Step 1: Block in build**

The simplest way: delete the file before launch, or guard with a flag:

In `src/pages/__styleguide.astro` add at top:

```astro
---
if (import.meta.env.PROD) return Astro.redirect('/');
---
```

- [ ] **Step 2: Commit**

```bash
git add src/pages/__styleguide.astro
git commit -m "chore(phase-5): redirect styleguide in prod"
```

---

### Task 39: Lighthouse audit

- [ ] **Step 1: Production build + preview**

```bash
npm run build
npm run preview
```

- [ ] **Step 2: Run Lighthouse**

```bash
npx lighthouse http://localhost:4321 --output=json --output-path=.tmp/lh-home.json --chrome-flags="--headless"
```

Run for each page (`/services`, `/portfolio`, `/about`, `/contact`). Save reports under `.tmp/lighthouse/`.

- [ ] **Step 3: Confirm targets**

| Page | Perf | A11y | SEO |
|---|---|---|---|
| target | ≥95 | ≥95 | ≥95 |

If any score < 95, identify cause:
- Perf: usually large images — verify AVIF is being served, widths are right
- A11y: missing alt text, low contrast — fix in components
- SEO: missing meta — verify SEO.astro is rendering

Re-run until all green.

- [ ] **Step 4: Commit any fixes**

```bash
git commit -am "perf(phase-5): lighthouse pass"
```

---

### Task 40: Vercel deploy

**Files:** (deploy-only)

- [ ] **Step 1: Install Vercel CLI**

```bash
npm install -g vercel
```

- [ ] **Step 2: Link project**

```bash
vercel link
```

Follow prompts: scope, project name `gamingxpo`.

- [ ] **Step 3: Deploy preview**

```bash
vercel
```

Expected: preview URL printed. Visit and confirm site loads.

- [ ] **Step 4: Set env vars on Vercel**

```bash
vercel env add PUBLIC_SITE_URL production
# enter: https://gamingxpo.com
```

- [ ] **Step 5: Deploy production**

```bash
vercel --prod
```

Expected: production URL prints. Confirm `https://gamingxpo.com` (or vercel.app preview) is live.

- [ ] **Step 6: Commit `.vercel/` config (without secrets)**

```bash
git add .vercel/project.json
git commit -m "chore(phase-5): vercel project linked"
```

---

### Task 41: Phase 5 gate — production sign-off

- [ ] **Step 1: User walks production URL**

Ask user: load `https://gamingxpo.com` on desktop and mobile. Confirm:
- All 5 pages load
- Hero image renders
- Portfolio filters work
- Contact form mockup success state works
- No console errors
- OG preview correct (test with https://www.opengraph.xyz/)

- [ ] **Step 2: On approval, merge**

```bash
git checkout main
git merge phase-5-polish --no-ff -m "merge: phase 5 launch polish"
git tag v1.0.0-mockup
```

---

## Plan complete

After all phase gates pass and `v1.0.0-mockup` is tagged, the project is at its first milestone. Future work (real contact backend, multilingual, blog) lands as new spec → plan → execution cycles.
