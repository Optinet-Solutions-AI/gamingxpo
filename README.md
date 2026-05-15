# Gamingxpo.com

Premium marketing site for **Gamingxpo**, a global builder of booths and stands for the iGaming sector (SiGMA, ICE, G2E, BiS, SBC, GAT). First release is a visual mockup. No live backend in v1.

- **Frontend:** Astro 4 + Tailwind CSS (static, ships from `dist/`)
- **Asset pipeline:** Python tools that scrape, AI-classify, inpaint, and optimize images before Astro consumes them
- **Hosting target:** Vercel (also WordPress-portable, templates stay semantic)

---

## Live structure

| Route | Purpose |
|---|---|
| `/` | Hero, metrics, featured client projects, services teaser, testimonials, team |
| `/services` | 5 service blocks with photo + numbered marks |
| `/portfolio` | 15 client case studies (project grid) |
| `/portfolio/<slug>` | Per-client case study with full multi-angle gallery |
| `/about` | Origin story, metrics, team |
| `/contact` | Mockup contact form |

---

## Development

```bash
npm install
npm run dev          # http://localhost:4321
npm run build        # static output → dist/
npm run preview      # serve dist/
```

Python pipeline (one-off, only when scraping new images):

```bash
.venv\Scripts\python.exe tools/scrape_pavilhao3_deep.py    # crawl pavilhao3.com
.venv\Scripts\python.exe tools/build_raw_manifest.py       # dedup
.venv\Scripts\python.exe tools/classify_logos.py           # Gemini vision tags
.venv\Scripts\python.exe tools/inpaint_watermarks.py       # cv2 watermark removal
.venv\Scripts\python.exe tools/optimize_images.py          # sharp -> AVIF + WebP
.venv\Scripts\python.exe tools/augment_portfolio_metadata.py
.venv\Scripts\python.exe tools/sync_team_data.py
```

---

## Repo layout

```
src/
  pages/            # Astro pages
  components/       # Nav, Hero, CaseCard, Testimonials, Team, ...
  layouts/Base.astro
  content/services/ # MD source for /services
  data/             # portfolio.json, projects.json, team.json
  styles/global.css
public/
  images/portfolio/ # AVIF + WebP at 4 widths per image (committed)
  images/brand/     # OG image, logo assets
  fonts/            # self-hosted Inter + Inter Tight
tools/              # Python scraping + classification + optimization pipeline
workflows/          # SOPs the agent reads before running tools
docs/superpowers/   # spec + implementation plan
```

---

## Tech notes

- **Light editorial palette** — cream `#F7F4EF` background, espresso ink `#14110D`, amber accent `#F5C84B`, electric-lime pop `#E6FF3D`
- **Self-hosted typography** — Inter Tight (display) + Inter (body) variable WOFF2 in `public/fonts/`
- **No tracking** — no analytics, no third-party scripts, mockup-first
- **CMS-portable** — Astro components map cleanly to WordPress templates if/when migrated

---

## Environment

A `.env` (gitignored) needs:

```
GEMINI_API_KEY=     # only for re-running the vision classifier
IG_USERNAME=        # optional: Instagram scrape login
IG_PASSWORD=
PUBLIC_SITE_URL=https://gamingxpo.com
```

---

## License

Proprietary. © Gamingxpo. All rights reserved.
