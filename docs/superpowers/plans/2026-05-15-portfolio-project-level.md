# Portfolio Project-Level Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 141-entry photo-level portfolio with a ~15-entry project-level structure — one card and one case study page per client — surfacing all photos for each client in a per-project gallery.

**Architecture:** A new Python scraper (`tools/scrape_project_pages.py`) fetches per-client content from pavilhao3.com and writes `src/data/projects.json` (keyed by slug). The Astro portfolio index and detail pages are rewritten to read from `projects.json` and group `portfolio.json` images by slug match. The homepage featured section is updated to link to `/portfolio/<project-slug>` routes.

**Tech Stack:** Python 3.11 + httpx + selectolax (scraper), Astro 4 + Tailwind CSS (frontend), existing `tools/_common.py` helpers.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `tools/scrape_project_pages.py` | **Create** | Fetch pavilhao3 per-project pages, write `src/data/projects.json` |
| `src/data/projects.json` | **Create (generated)** | Per-client metadata: slug, name, title, description, image_slugs |
| `src/pages/portfolio/[project].astro` | **Create** | Project detail page: hero + story sidebar + full gallery + related |
| `src/pages/portfolio/[slug].astro` | **Delete** | Old photo-level detail page — replaced by `[project].astro` |
| `src/pages/portfolio.astro` | **Replace** | Portfolio index: one card per project, cover + image count |
| `src/pages/index.astro` | **Modify** | Featured section reads from projects.json, links to project slugs |

---

## Known Data Facts (as of 2026-05-15)

Portfolio has 15 named clients across 73 images with a `project` field:

| Client name (portfolio.json) | Count | pavilhao3 slug |
|---|---|---|
| Aliquam Eratac | 4 | aliquam-eratac *(dummy — needs placeholder copy)* |
| Bebuilder 2841 | 12 | bebuilder-2841 *(dummy — needs placeholder copy)* |
| Casfil | 7 | casfil |
| Curabitur Et Ligula | 2 | curabitur-et-ligula *(dummy — needs placeholder copy)* |
| Edp | 2 | edp |
| Fidelidade | 4 | fidelidade |
| Havaianas | 2 | havaianas |
| Iqos | 3 | iqos |
| Oriflame | 3 | oriflame |
| Portugalia | 3 | portugalia |
| Quisque Lorem Tortor | 3 | quisque-lorem-tortor *(dummy — needs placeholder copy)* |
| Rubis Gas | 5 | rubis-gas |
| Solana | 10 | solana |
| Vella Cafe | 4 | vella-cafe |
| Vellila Group | 9 | vellila-group |

The `image_slugs` array for each project is built by matching `portfolio.json[].project` (case-insensitive) to the project name, then collecting the `slug` field.

---

## Task 1: Write `tools/scrape_project_pages.py`

**Files:**
- Create: `tools/scrape_project_pages.py`

The script reads `src/data/portfolio.json`, extracts known `source_page` URLs that match `/blog/portfolio-item/<slug>/`, fetches each one, extracts title + description paragraphs, falls back to placeholder copy for dummies/empty results, groups image slugs per project, and writes `src/data/projects.json`.

**Slug derivation rule:** The pavilhao3 slug comes directly from `source_page` field (regex `r'/blog/portfolio-item/([^/]+)/'`). The Gamingxpo slug is the same string (already lowercase-hyphenated).

**Dummy client rule:** Clients whose `pavilhao3_slug` matches any of `['aliquam-eratac', 'bebuilder-2841', 'curabitur-et-ligula', 'quisque-lorem-tortor']` get placeholder copy instead of scraped content.

**Placeholder copy map** (use these verbatim):
```python
PLACEHOLDER_COPY = {
    "bebuilder-2841": "A multi-event stand programme delivered across three consecutive trade shows in eighteen months. Brief: a modular system that looked custom-built every time. The result was a reconfigurable architecture that cut on-site assembly by 40% without sacrificing the finish. Fully branded, fully staffed, consistently on time.",
    "aliquam-eratac": "Brand activation stand for an FMCG client entering a new European market. High-contrast graphics, integrated product display, and a demo counter designed for dwell time. Delivered and assembled overnight ahead of a morning keynote. Zero snags on show day.",
    "curabitur-et-ligula": "Compact island stand built for a first-time exhibitor at a regional gaming expo. The brief was maximum presence on a tight footprint — we achieved it with floor-to-ceiling tension fabric, integrated LED headers, and a single hospitality counter. Client returned for the following year.",
    "quisque-lorem-tortor": "Sponsorship activation for a sports and entertainment brand at an outdoor festival. Modular pop-up with branded canopy, product display, and on-site crew. The stand was designed for rapid build and teardown across a touring schedule of four cities in seven days.",
}
```

- [ ] **Step 1: Write the script**

```python
"""Scrape pavilhao3.com per-project pages and write src/data/projects.json."""
from __future__ import annotations
import json
import re
import sys
import time
from pathlib import Path

import httpx
from selectolax.parser import HTMLParser

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_JSON = ROOT / "src" / "data" / "portfolio.json"
PROJECTS_JSON = ROOT / "src" / "data" / "projects.json"

DUMMY_SLUGS = {"aliquam-eratac", "bebuilder-2841", "curabitur-et-ligula", "quisque-lorem-tortor"}

PLACEHOLDER_COPY = {
    "bebuilder-2841": "A multi-event stand programme delivered across three consecutive trade shows in eighteen months. Brief: a modular system that looked custom-built every time. The result was a reconfigurable architecture that cut on-site assembly by 40% without sacrificing the finish. Fully branded, fully staffed, consistently on time.",
    "aliquam-eratac": "Brand activation stand for an FMCG client entering a new European market. High-contrast graphics, integrated product display, and a demo counter designed for dwell time. Delivered and assembled overnight ahead of a morning keynote. Zero snags on show day.",
    "curabitur-et-ligula": "Compact island stand built for a first-time exhibitor at a regional gaming expo. The brief was maximum presence on a tight footprint — we achieved it with floor-to-ceiling tension fabric, integrated LED headers, and a single hospitality counter. Client returned for the following year.",
    "quisque-lorem-tortor": "Sponsorship activation for a sports and entertainment brand at an outdoor festival. Modular pop-up with branded canopy, product display, and on-site crew. The stand was designed for rapid build and teardown across a touring schedule of four cities in seven days.",
}

SLUG_RE = re.compile(r"/blog/portfolio-item/([^/]+)/")


def _extract_slug_from_source_page(source_page: str) -> str | None:
    m = SLUG_RE.search(source_page)
    return m.group(1) if m else None


def _extract_text(html: str) -> str:
    """Return the first 3 meaningful body paragraphs joined as a single string."""
    tree = HTMLParser(html)
    # Remove nav/footer/script/style noise
    for node in tree.css("nav, footer, header, script, style, .site-header, .site-footer, .widget"):
        node.decompose()
    paragraphs = []
    for p in tree.css("p"):
        text = p.text(strip=True)
        # Skip very short lines (captions, labels) and navigation crumbs
        if len(text) > 40 and not text.startswith("©"):
            paragraphs.append(text)
        if len(paragraphs) == 3:
            break
    return " ".join(paragraphs)


def _fetch_project(client: httpx.Client, slug: str) -> dict:
    url = f"https://pavilhao3.com/blog/portfolio-item/{slug}/"
    try:
        r = client.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  [warn] {slug} -> HTTP {r.status_code}")
            return {"title": slug.replace("-", " ").title(), "description": "", "source_url": url}
        tree = HTMLParser(r.text)

        # Title: <title> tag, strip " - Pavilhao 3" or " | Pavilhao 3" suffix
        raw_title = tree.css_first("title")
        title = raw_title.text(strip=True) if raw_title else slug.replace("-", " ").title()
        title = re.sub(r"\s*[-|]\s*Pavilh[aã]o\s*3.*$", "", title, flags=re.IGNORECASE).strip()

        # Meta description
        meta_desc = ""
        meta = tree.css_first('meta[name="description"]')
        if meta:
            meta_desc = meta.attributes.get("content", "").strip()

        # Body paragraphs
        body_text = _extract_text(r.text)
        description = body_text or meta_desc

        return {"title": title, "description": description, "source_url": url}
    except httpx.HTTPError as exc:
        print(f"  [error] {slug}: {exc}")
        return {"title": slug.replace("-", " ").title(), "description": "", "source_url": url}


def build_projects_json() -> None:
    portfolio = json.loads(PORTFOLIO_JSON.read_text(encoding="utf-8"))

    # Group image slugs by pavilhao3_slug (derived from source_page)
    slug_to_images: dict[str, list[str]] = {}
    slug_to_name: dict[str, str] = {}   # pavilhao3_slug -> display name from portfolio.json project field
    seen_source_pages: dict[str, str] = {}  # pavilhao3_slug -> source_page URL

    for entry in portfolio:
        project = entry.get("project")
        if not project:
            continue
        source_page = entry.get("source_page", "")
        pav_slug = _extract_slug_from_source_page(source_page)
        if not pav_slug:
            continue
        if pav_slug not in slug_to_images:
            slug_to_images[pav_slug] = []
            slug_to_name[pav_slug] = project
            seen_source_pages[pav_slug] = source_page
        slug_to_images[pav_slug].append(entry["slug"])

    projects: dict[str, dict] = {}

    with httpx.Client(
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 GamingxpoBot/1.0"},
    ) as client:
        for pav_slug, display_name in sorted(slug_to_name.items()):
            print(f"Processing: {pav_slug} ({display_name})")

            if pav_slug in DUMMY_SLUGS:
                description = PLACEHOLDER_COPY.get(pav_slug, "A premium event stand delivered end-to-end by the Gamingxpo team. Design, build, branding, and on-site crew — one vendor, one accountable lead.")
                projects[pav_slug] = {
                    "slug": pav_slug,
                    "name": display_name,
                    "title": display_name,
                    "description": description,
                    "source_url": seen_source_pages[pav_slug],
                    "year": None,
                    "image_slugs": slug_to_images[pav_slug],
                }
            else:
                scraped = _fetch_project(client, pav_slug)
                description = scraped["description"]
                # Fallback if still empty after scrape
                if not description or len(description) < 30:
                    description = f"Premium booth and stand build for {display_name}, delivered end-to-end by the Gamingxpo team. Full-service scope: concept design, structural build, brand graphics, AV integration, and on-site crew management. One vendor, zero subcontractor chains."
                projects[pav_slug] = {
                    "slug": pav_slug,
                    "name": scraped["title"] or display_name,
                    "title": scraped["title"] or display_name,
                    "description": description,
                    "source_url": scraped["source_url"],
                    "year": None,
                    "image_slugs": slug_to_images[pav_slug],
                }
                time.sleep(0.5)

    PROJECTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_JSON.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(projects)} projects to {PROJECTS_JSON}")
    for slug, p in projects.items():
        print(f"  {slug}: {len(p['image_slugs'])} images")


if __name__ == "__main__":
    build_projects_json()
```

- [ ] **Step 2: Run the script**

```
cd c:\Users\User\Desktop\Gamingxpo.com
.venv\Scripts\python tools/scrape_project_pages.py
```

Expected output: `Wrote 15 projects to ...src/data/projects.json` followed by per-project image counts. Total images across all projects should be 73.

- [ ] **Step 3: Inspect output**

```
.venv\Scripts\python -c "
import json
data = json.load(open('src/data/projects.json'))
total = sum(len(v['image_slugs']) for v in data.values())
print(f'{len(data)} projects, {total} total images')
for slug, p in data.items():
    print(f'  {slug}: {len(p[\"image_slugs\"])} imgs | desc[:60]={repr(p[\"description\"][:60])}')
"
```

Expected: 15 projects, 73 total images, each has a non-empty description.

- [ ] **Step 4: Commit**

```bash
git add tools/scrape_project_pages.py src/data/projects.json
git commit -m "feat(data): scrape per-project content, write projects.json

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Create `src/pages/portfolio/[project].astro`

**Files:**
- Create: `src/pages/portfolio/[project].astro`

This is the new project detail page. It replaces `[slug].astro` (which is deleted in Task 3). It reads `projects.json` for metadata and `portfolio.json` for all images whose `project` field slug-matches the route param.

**Slug matching rule:** `(img.project ?? '').toLowerCase().replace(/\s+/g, '-') === project.slug`

- [ ] **Step 1: Create the file**

Create `src/pages/portfolio/[project].astro`:

```astro
---
import Base from '../../layouts/Base.astro';
import SectionHeader from '../../components/SectionHeader.astro';
import ContactSplit from '../../components/ContactSplit.astro';
import projects from '../../data/projects.json';
import portfolio from '../../data/portfolio.json';

export function getStaticPaths() {
  return Object.values(projects).map((proj: any) => ({
    params: { project: proj.slug },
    props: { project: proj },
  }));
}

const { project } = Astro.props;
const images = (portfolio as any[]).filter((p: any) =>
  (p.project ?? '').toLowerCase().replace(/\s+/g, '-') === project.slug
  && p.quality !== 'reject'
);
const cover = images.find((p: any) => p.subject === 'booth_exterior') ?? images[0];
const otherProjects = Object.values(projects)
  .filter((p: any) => p.slug !== project.slug)
  .slice(0, 3) as any[];
---
<Base
  title={`${project.name} — Gamingxpo Portfolio`}
  description={project.description.slice(0, 160)}
  ogImage={cover ? `${cover.src_base}/1920.webp` : undefined}
>

  <!-- Hero block -->
  <section class="max-w-layout mx-auto px-6 pt-12 pb-12">
    <div class="grid md:grid-cols-12 gap-8 items-end mb-8">
      <div class="md:col-span-8">
        <p class="inline-flex items-center gap-2 text-xs tracking-[0.25em] uppercase font-medium text-fg/70">
          <span class="w-6 h-px bg-accent"></span>
          Case study · Client {project.name}
        </p>
        <h1 class="font-display text-display-xl mt-4 max-w-[14ch] text-ink">{project.name}</h1>
      </div>
      <div class="md:col-span-4 text-sm text-muted">
        <p>{project.description.split(/\.\s+/)[0]}.</p>
      </div>
    </div>
    {cover && (
      <div class="relative rounded-2xl overflow-hidden bg-line aspect-[21/9]">
        <picture>
          <source type="image/avif" srcset={`${cover.src_base}/1920.avif`} />
          <img src={`${cover.src_base}/1920.webp`} alt={cover.alt} class="w-full h-full object-cover" />
        </picture>
      </div>
    )}
  </section>

  <!-- Story + sidebar -->
  <article class="max-w-layout mx-auto px-6 py-section grid md:grid-cols-12 gap-8 lg:gap-16">
    <aside class="md:col-span-4 space-y-6">
      <div class="border-l border-line pl-4">
        <div class="text-fg/70 text-xs uppercase tracking-widest">Client</div>
        <div class="text-ink font-medium mt-1">{project.name}</div>
      </div>
      <div class="border-l border-line pl-4">
        <div class="text-fg/70 text-xs uppercase tracking-widest">Photos in gallery</div>
        <div class="text-ink font-medium mt-1">{images.length}</div>
      </div>
      <div class="border-l border-line pl-4">
        <div class="text-fg/70 text-xs uppercase tracking-widest">Scope</div>
        <div class="text-ink font-medium mt-1">Design · Build · Branding · On-site</div>
      </div>
    </aside>
    <div class="md:col-span-8 max-w-prose space-y-6 text-fg/80 text-body">
      <h2 class="font-display text-display-md text-ink">About the project</h2>
      <p>{project.description}</p>
    </div>
  </article>

  <!-- Image gallery — all angles -->
  <section class="bg-bg-alt border-t border-line">
    <div class="max-w-layout mx-auto px-6 py-section">
      <header class="mb-8">
        <p class="inline-flex items-center gap-2 text-xs tracking-[0.25em] uppercase font-medium text-fg/70">
          <span class="w-6 h-px bg-accent"></span>
          Gallery
        </p>
        <h2 class="font-display text-display-lg mt-4 text-ink">Every angle.</h2>
      </header>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {images.map((img: any) => (
          <div class="aspect-[4/3] overflow-hidden rounded-xl bg-line">
            <picture>
              <source
                type="image/avif"
                srcset={`${img.src_base}/640.avif 640w, ${img.src_base}/960.avif 960w, ${img.src_base}/1440.avif 1440w`}
                sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
              />
              <img
                src={`${img.src_base}/960.webp`}
                alt={img.alt}
                class="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                loading="lazy"
              />
            </picture>
          </div>
        ))}
      </div>
    </div>
  </section>

  <!-- More projects -->
  {otherProjects.length > 0 && (
    <section>
      <SectionHeader eyebrow="More work" title="Other clients." />
      <div class="max-w-layout mx-auto px-6 grid md:grid-cols-3 gap-8 pb-section">
        {otherProjects.map((p: any) => {
          const c = (portfolio as any[]).find(
            (x: any) => (x.project ?? '').toLowerCase().replace(/\s+/g, '-') === p.slug
          );
          return (
            <a href={`/portfolio/${p.slug}`} class="group block">
              <div class="aspect-[4/3] overflow-hidden rounded-xl bg-line">
                {c && (
                  <img
                    src={`${c.src_base}/960.webp`}
                    alt={c.alt}
                    class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                    loading="lazy"
                  />
                )}
              </div>
              <div class="pt-3 font-display text-ink group-hover:text-coral transition-colors">{p.name}</div>
            </a>
          );
        })}
      </div>
    </section>
  )}

  <ContactSplit />
</Base>
```

- [ ] **Step 2: Verify it compiles (quick type check via build)**

```
cd c:\Users\User\Desktop\Gamingxpo.com
npm run build 2>&1 | head -40
```

Do not proceed if there are TypeScript or Astro errors. Fix any compilation issues before continuing.

- [ ] **Step 3: Commit**

```bash
git add src/pages/portfolio/[project].astro
git commit -m "feat(portfolio): add project-level detail page [project].astro

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Delete old `[slug].astro` and replace `portfolio.astro`

**Files:**
- Delete: `src/pages/portfolio/[slug].astro`
- Replace: `src/pages/portfolio.astro`

Deleting `[slug].astro` removes the 130+ individual photo routes. Replacing `portfolio.astro` switches the index from photo-grid to project-grid.

- [ ] **Step 1: Delete the old detail page**

```bash
git rm src/pages/portfolio/[slug].astro
```

- [ ] **Step 2: Replace portfolio.astro**

Overwrite `src/pages/portfolio.astro` with:

```astro
---
import Base from '../layouts/Base.astro';
import SectionHeader from '../components/SectionHeader.astro';
import projects from '../data/projects.json';
import portfolio from '../data/portfolio.json';

const projectList = (Object.values(projects) as any[]).map((p: any) => {
  const images = (portfolio as any[]).filter((img: any) =>
    (img.project ?? '').toLowerCase().replace(/\s+/g, '-') === p.slug
    && img.quality !== 'reject'
  );
  const cover = images.find((img: any) => img.subject === 'booth_exterior') ?? images[0];
  return { ...p, cover, imageCount: images.length };
}).filter((p: any) => p.cover);

projectList.sort((a: any, b: any) => b.imageCount - a.imageCount);
const totalPhotos = projectList.reduce((s: number, p: any) => s + p.imageCount, 0);
---
<Base
  title="Portfolio — Gamingxpo"
  description="Selected booth builds for iGaming clients. Click any project for the full multi-angle gallery."
>
  <SectionHeader
    eyebrow="Portfolio"
    title={`${projectList.length} clients. ${totalPhotos}+ photos.`}
    kicker="Every project below was designed, built, freighted, and assembled on-site by the in-house Gamingxpo team. Click any card for the full gallery."
  />

  <div class="max-w-layout mx-auto px-6 grid md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-14 pb-section">
    {projectList.map((p: any) => (
      <a href={`/portfolio/${p.slug}`} class="group block">
        <div class="aspect-[4/3] overflow-hidden rounded-xl bg-line relative">
          <picture>
            <source
              type="image/avif"
              srcset={`${p.cover.src_base}/640.avif 640w, ${p.cover.src_base}/960.avif 960w, ${p.cover.src_base}/1440.avif 1440w`}
              sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
            />
            <img
              src={`${p.cover.src_base}/960.webp`}
              alt={p.cover.alt}
              class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
              loading="lazy"
            />
          </picture>
          <div class="absolute top-3 left-3 bg-bg-alt/90 backdrop-blur px-2.5 py-1 rounded-full text-xs text-ink font-medium">
            {p.imageCount} photos
          </div>
        </div>
        <div class="pt-4 flex items-start justify-between gap-4">
          <div>
            <div class="text-xs text-muted uppercase tracking-widest">Case study</div>
            <div class="text-display-md font-display mt-1 text-ink group-hover:text-coral transition-colors">{p.name}</div>
          </div>
          <span class="shrink-0 inline-flex items-center justify-center w-9 h-9 rounded-full border border-line group-hover:bg-ink group-hover:border-ink group-hover:text-bg transition-colors text-ink">
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M3 8h10m0 0L9 4m4 4l-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </span>
        </div>
      </a>
    ))}
  </div>
</Base>
```

- [ ] **Step 3: Verify build succeeds**

```
npm run build 2>&1 | tail -20
```

Expected: Build succeeds. No routes matching `/portfolio/[slug]` for photo slugs. New routes present for project slugs (havaianas, edp, solana, etc.).

- [ ] **Step 4: Commit**

```bash
git add src/pages/portfolio.astro
git commit -m "refactor(portfolio): replace photo-grid with project-grid index

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Update homepage featured section

**Files:**
- Modify: `src/pages/index.astro` (lines 17–35 — the `featured` block)

Currently `index.astro` picks one image per named project and links to photo slugs (`/portfolio/<image-slug>`). We need it to link to project slugs (`/portfolio/<project-slug>`) and read from `projects.json` for the cover.

- [ ] **Step 1: Modify index.astro**

Replace the import and `featured` computation block. The existing file has:

```ts
import portfolio from '../data/portfolio.json';

const DUMMY_PROJECTS = new Set([
  'Bebuilder 2841', 'Quisque Lorem Tortor', 'Aliquam Eratac', 'Curabitur Et Ligula',
]);

// One feature card per real named client (first portfolio_grade booth photo we have)
const seenProjects = new Set<string>();
const featured = portfolio
  .filter((p: any) =>
    p.quality === 'portfolio_grade'
    && (p.subject === 'booth_exterior' || p.subject === 'booth_interior')
    && p.project
    && !DUMMY_PROJECTS.has(p.project)
  )
  .filter((p: any) => {
    if (seenProjects.has(p.project)) return false;
    seenProjects.add(p.project);
    return true;
  })
  .slice(0, 6);

const titleCase = (s: string) => s.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
```

Replace it with:

```ts
import portfolio from '../data/portfolio.json';
import projectsData from '../data/projects.json';

const projectsList = (Object.values(projectsData) as any[]).map((p: any) => {
  const images = (portfolio as any[]).filter((img: any) =>
    (img.project ?? '').toLowerCase().replace(/\s+/g, '-') === p.slug
    && img.quality !== 'reject'
  );
  const cover = images.find((img: any) => img.subject === 'booth_exterior') ?? images[0];
  return { ...p, cover };
}).filter((p: any) => p.cover);

const featuredProjects = projectsList.slice(0, 6);

const titleCase = (s: string) => s.replace(/[_-]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
```

- [ ] **Step 2: Update the JSX render block**

In the same file, the existing featured map is:

```astro
{featured.map((p: any) => <CaseCard {...p} title={p.project ?? titleCase(p.subject)} event="iGaming event" year={2025} />)}
```

Replace it with:

```astro
{featuredProjects.map((p: any) => (
  <CaseCard
    slug={p.slug}
    src_base={p.cover.src_base}
    alt={p.cover.alt}
    title={p.name}
    event="iGaming event"
    year={2025}
  />
))}
```

- [ ] **Step 3: Verify build**

```
npm run build 2>&1 | tail -20
```

Expected: Build succeeds. Homepage renders 6 project cards linking to `/portfolio/<project-slug>`.

- [ ] **Step 4: Commit**

```bash
git add src/pages/index.astro
git commit -m "feat(home): featured cards now link to project-level portfolio pages

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Final build verification and summary commit

- [ ] **Step 1: Clean build**

```
npm run build 2>&1
```

Confirm all of the following:
- Exit code 0 (no errors)
- Routes include `/portfolio/havaianas`, `/portfolio/edp`, `/portfolio/solana`, `/portfolio/vellila-group`, etc. (15 project routes)
- Routes do NOT include `/portfolio/havaianas-rock-in-rio-2018-...` or similar photo-slug routes
- Total generated routes are roughly 20–25 (home, services, about, contact, styleguide, 404, portfolio index, 15 project pages)

- [ ] **Step 2: Count routes**

```
npm run build 2>&1 | grep "portfolio/"
```

Expected: Only project-slug routes show (havaianas, edp, iqos, etc.), not photo slugs.

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
feat(portfolio): project-level structure (one case study per client)

- src/data/projects.json: per-client metadata scraped from
  pavilhao3.com/blog/portfolio-item/<slug>/ pages, with image grouping
- src/pages/portfolio/[project].astro: new project detail page with hero,
  story, and full multi-angle gallery (all photos for that client)
- src/pages/portfolio.astro: now lists projects (not photos), showing
  cover photo + image count per card
- src/pages/index.astro: featured cards now link to /portfolio/<project-slug>
- tools/scrape_project_pages.py: scraper for per-project content

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review Against Spec

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| `tools/scrape_project_pages.py` fetches per-project pages | Task 1 |
| Extracts title, description paragraphs, meta description | Task 1 Step 1 (`_fetch_project`) |
| 0.5s polite delay between requests | Task 1 Step 1 (`time.sleep(0.5)`) |
| Writes `src/data/projects.json` with slug, name, title, description, source_url, year, image_slugs | Task 1 Step 1 |
| DUMMY clients get professional placeholder copy | Task 1 Step 1 (`PLACEHOLDER_COPY` + fallback) |
| `image_slugs` from portfolio.json project match (not new downloads) | Task 1 Step 1 (reads portfolio.json, groups by pav_slug) |
| `[project].astro` replaces `[slug].astro` | Tasks 2, 3 |
| Hero + story sidebar + full gallery + related projects | Task 2 |
| `portfolio.astro` project grid with cover + image count badge | Task 3 |
| Homepage featured links to `/portfolio/<project-slug>` | Task 4 |
| Old per-photo routes removed | Task 3 Step 1 (`git rm [slug].astro`) |
| Total routes ~25 not ~148 | Task 5 Step 2 |
| No existing images deleted | Never touches `public/images/` or `portfolio.json` entries |
| No broken services/about/contact pages | Build check in each task |
| Single final commit with canonical message | Task 5 Step 3 |

**Placeholder scan:** No TBDs, no "TODO", no "Lorem ipsum", no "similar to Task N", all code blocks present.

**Type consistency:** `project.slug`, `project.name`, `project.description`, `p.cover`, `p.cover.src_base`, `p.cover.alt` — used consistently across Tasks 2, 3, 4 and all match the structure written in Task 1.
