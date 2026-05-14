# Gamingxpo.com — Website Design Spec

**Date:** 2026-05-14
**Status:** Draft — awaiting user review
**Owner:** john@optinetsolutions.com

---

## 1. Goal

Build a premium, agency-grade marketing website for **Gamingxpo.com**, a new brand positioned as a global builder of booths and stands for the iGaming sector. The site replaces the impression created by https://pavilhao3.com (which is the same operator but undermarketed) and showcases the existing portfolio in an editorial, English-first format suitable for international iGaming events (SiGMA, ICE, G2E, BiS, GAT, etc.).

The first release is a **mockup** — visual and content complete, no live backend integrations.

---

## 2. Decisions (locked)

| Area | Decision |
|---|---|
| Framework | Astro + Tailwind |
| Hosting | Vercel (with WordPress portability in mind — keep templates HTML-clean) |
| Brand | New brand "Gamingxpo.com"; Pavilhão 3 is a reference only |
| Visual tier | Premium / agency-grade (editorial dark, single accent, restrained motion) |
| Image storage | `public/images/` committed to repo |
| Logo handling | AI-classify + auto-inpaint watermark-style overlays; keep all logos on physical objects (booth walls, t-shirts, signage) |
| Site map | Home + Services + Portfolio + About + Contact |
| Contact backend | **Deferred** — mockup-only form, no backend in v1 |
| Image sources | https://pavilhao3.com and https://www.instagram.com/pavilhao_3 |

---

## 3. Architecture

```
Gamingxpo.com/
├── CLAUDE.md                    # Project brief (rewritten from template)
├── astro.config.mjs
├── tailwind.config.cjs
├── package.json
├── src/
│   ├── pages/
│   │   ├── index.astro          # Home
│   │   ├── services.astro
│   │   ├── portfolio.astro
│   │   ├── about.astro
│   │   ├── contact.astro
│   │   └── __styleguide.astro   # internal, removed before launch
│   ├── components/
│   │   ├── Nav.astro
│   │   ├── Footer.astro
│   │   ├── Hero.astro
│   │   ├── SectionHeader.astro
│   │   ├── CaseCard.astro
│   │   ├── ServiceTile.astro
│   │   ├── MetricStrip.astro
│   │   ├── MarqueeBrands.astro
│   │   ├── FilterBar.astro
│   │   └── ContactSplit.astro
│   ├── layouts/Base.astro
│   ├── content/
│   │   ├── portfolio/           # MDX per case study
│   │   ├── services/            # MDX per service
│   │   └── config.ts            # Astro content collections schemas
│   └── styles/global.css
├── public/
│   └── images/
│       ├── portfolio/<slug>/<width>.{avif,webp}
│       ├── services/
│       └── brand/
├── tools/                       # WAT framework — Python pipeline
│   ├── scrape_pavilhao3.py
│   ├── scrape_instagram.py
│   ├── classify_logos.py
│   ├── inpaint_watermarks.py
│   └── optimize_images.py
├── workflows/                   # WAT framework — SOPs
│   ├── scrape_and_clean_images.md
│   ├── design_system.md
│   └── publish_portfolio.md
├── .tmp/
│   ├── raw_scrape/
│   ├── classified/
│   └── cleaned/
├── docs/superpowers/specs/
├── .env                         # secrets (Anthropic key, optional IG session)
├── .claudeignore
└── .gitignore
```

**Layer separation (WAT framework):** Python tools prepare assets deterministically; Astro consumes the cleaned `public/images/` and `src/content/`. The site has no Python runtime dependency.

---

## 4. Image pipeline

### 4.1 Scrape
- **`tools/scrape_pavilhao3.py`** — `httpx + selectolax`. Crawl homepage and gallery/portfolio pages. Collect every `<img src>`, `<source srcset>` (pick the largest), and CSS `background-image`. Output `.tmp/raw_scrape/pavilhao3/` + `pavilhao3.json` manifest (source URL, alt text, parent page).
- **`tools/scrape_instagram.py`** — `instaloader`, anonymous mode first. Pull all posts from `@pavilhao_3` (images + carousel slides). Output `.tmp/raw_scrape/instagram/` + `instagram.json` (caption, post URL, timestamp). If anonymous mode is rate-limited, fall back to a throwaway IG session credential from `.env`.
- **Dedup:** `imagehash.phash` across the union of both sets.

### 4.2 Classify (vision)
- **`tools/classify_logos.py`** — Iterate raw images, call Claude Sonnet 4.6 vision with this output contract:

  ```json
  {
    "has_watermark": true,
    "watermark_boxes": [
      {"x": 0.85, "y": 0.92, "w": 0.13, "h": 0.06, "label": "@pavilhao_3 corner watermark"}
    ],
    "physical_logos": [
      {"label": "client logo on booth wall — KEEP"}
    ],
    "quality": "portfolio_grade | social_only | reject",
    "subject": "booth_exterior | booth_interior | crowd | team | detail | other"
  }
  ```

- Coordinates are normalized 0–1. Use prompt caching to keep cost ≈ $0.003/image.
- Output `.tmp/classified/manifest.json`. Drop anything with `quality: reject` (blur, screenshots, memes, off-topic).

### 4.3 Inpaint
- **`tools/inpaint_watermarks.py`** — For each image with `has_watermark: true`, build a binary mask from `watermark_boxes` (with ~6px feather) and run **IOPaint** (LaMa model, local). Output `.tmp/cleaned/<filename>.jpg`.
- **`physical_logos` are never touched** — they are social proof.
- Save side-by-side `before|after` PNGs to `.tmp/cleaned/_diffs/` for user audit before commit.

### 4.4 Optimize
- **`tools/optimize_images.py`** — Use `sharp` via `npx` to emit AVIF + WebP at widths `[640, 960, 1440, 1920]`. Place final variants at `public/images/portfolio/<slug>/<width>.<ext>`.
- Emit `src/content/portfolio.json` (slug, title, subject, English alt text, source URL) for Astro content collections to consume.

### 4.5 Cost & honest constraints
- ~$1.50 per 500 images for vision classification.
- IOPaint: CPU ≈ 10s/image, GPU < 1s/image. Free either way.
- Instagram scrapers break periodically; if blocked we fall back to manual download.

---

## 5. Site map & content model

### 5.1 Pages
| Route | Purpose | Above-the-fold hook |
|---|---|---|
| `/` | 8-second decision | Full-bleed hero booth photo + "Stand out at every iGaming event in the world." + CTA |
| `/services` | What we build | 5-tile grid (Design • Build • Branding • AV/Tech • On-site) |
| `/portfolio` | Proof | Filterable gallery (by event, year, m²) → case-study pages |
| `/about` | Trust | Founder story, team, partner brand strip |
| `/contact` | Lead capture (mockup) | Form UI only; submit shows static success state |

### 5.2 Content collections (`src/content/config.ts`)
```ts
portfolio: {
  slug, title, client, event, year, city, size_m2,
  scope: ('design'|'build'|'av'|'branding'|'on_site')[],
  cover: ImageSet, gallery: ImageSet[],
  body: MDX  // story / challenge / solution / result
}
services: { slug, title, intro, deliverables[], featured_portfolio_slugs[] }
testimonials: { client, person, role, quote, portfolio_slug }
```

### 5.3 Filtering
Portfolio page filters by `event`, `year`, `scope`. Implemented client-side with vanilla JS over a hydration-free Astro grid (no React needed).

---

## 6. Visual direction

| Element | Decision |
|---|---|
| Mode | Dark-first |
| Background | `#0A0A0B` |
| Text | `#F5F4F1` warm off-white |
| Accent | `#E6FF3D` electric-lime (single accent, used sparingly) |
| Display type | Inter Tight 600/700 (self-hosted) — fallback to system stack |
| Body type | Inter 400, 18px / line-height 1.6 / max-width 65ch |
| Grid | 12-col with 96px vertical rhythm desktop / 48px mobile |
| Motion | View-timeline scroll reveals, slow Ken Burns on hero, 200ms hover ease. No scroll-jacking, no parallax stutter. |
| Imagery | 16:9 minimum, 1920w minimum, cropped to architecture (not crowds) |

### Upgrades over pavilhao3.com
- Full-bleed hero replaces thumbnail mosaic
- English-first copy (Portuguese `/pt` namespace deferred)
- Real case studies with story per project (not flat gallery)
- Hero metric strip ("200+ booths • 14 countries • 9 years")
- Editorial dark with single accent replaces casino-blue gradients

---

## 7. Implementation phases

| # | Phase | Output | Gate |
|---|---|---|---|
| 0 | Repo + CLAUDE.md | Astro+Tailwind scaffold, tools/workflows skeleton, rewritten CLAUDE.md, Vercel project linked, initial commit | `npm run dev` serves blank Astro at `localhost:4321` |
| 1 | Pipeline — scrape | `scrape_pavilhao3.py` + `scrape_instagram.py` populate `.tmp/raw_scrape/` with dedup manifest | User confirms raw image count is sufficient |
| 2 | Pipeline — clean | `classify_logos.py` + `inpaint_watermarks.py` + `optimize_images.py` populate `public/images/portfolio/` and `src/content/portfolio.json` | User audits `.tmp/cleaned/_diffs/` |
| 3 | Design system | `Base.astro`, tokens, type scale, all components rendered on `/__styleguide` | User approves styleguide |
| 4 | Page assembly | 5 pages built, portfolio filtering works, contact form UI-only with mock success state | User walks preview |
| 5 | Launch polish | Lighthouse ≥95 perf/seo/a11y, OG images, sitemap.xml, robots.txt, 404, Plausible analytics | Production live on gamingxpo.com |

### Phase ground rules
- Each phase = its own git branch + PR, merged only after user gate-pass
- Screenshot-driven verification per `superpowers:verification-before-completion`
- Each phase ends with a `workflows/<phase>.md` SOP committed
- WAT layering preserved: Python in `tools/`, SOPs in `workflows/`, secrets in `.env`, intermediates in `.tmp/`

---

## 8. Open items (non-blocking)

- **Instagram sign-in** — anonymous mode tried first; if rate-limited, the pipeline halts and prompts the user to sign in interactively (user confirmed they will handle login on demand). The IG session is then cached locally by `instaloader` for the remainder of the run.
- **Contact backend** — out of scope for v1. Revisit when mockup is approved (Resend for email-only, Supabase if leads should be stored).
- **Portuguese localization** — deferred. English-first launch.
- **Real client logos for partner strip** — need user-supplied list or we extract from scraped images.

---

## 9. Out of scope (v1)

- Backend services (form submission, lead capture, CRM)
- CMS authoring UI
- E-commerce / quoting
- Multi-language
- Blog / news section
- Reels / video embeds from Instagram
- Authentication / admin area
