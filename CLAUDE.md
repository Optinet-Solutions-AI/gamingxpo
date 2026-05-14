# CLAUDE.md — Gamingxpo.com

> Project brief for any Claude/Codex/Gemini session working in this repo.
> Authoritative spec: [docs/superpowers/specs/2026-05-14-gamingxpo-website-design.md](docs/superpowers/specs/2026-05-14-gamingxpo-website-design.md)

---

## Project Overview

**Gamingxpo.com** is a premium, agency-grade marketing site for a global builder of booths and stands for the iGaming sector (SiGMA, ICE, G2E, BiS, GAT, etc.). It is a new brand built on top of an existing operator (`pavilhao3.com` / `@pavilhao_3` on Instagram), repositioned English-first for worldwide events. **First release is a mockup** — visuals and content complete, no live backend.

- **Frontend:** Astro + Tailwind CSS (static-first, portable to WordPress if/when migrated)
- **Backend / Logic:** None in v1 — contact form is UI-only
- **Asset pipeline:** Python scripts in `tools/` (WAT framework) scrape, classify, inpaint, and optimize images before Astro consumes them
- **AI:** Anthropic Claude Sonnet 4.6 (vision) for watermark classification; IOPaint/LaMa (local) for inpaint
- **Hosting:** Vercel
- **Repo:** local (git init in Phase 0)
- **Live URL:** gamingxpo.com (Phase 5 target)

---

## How the App Works

This is a content site. There is no user journey beyond browsing.

```
Image pipeline (run on demand, not at request time):
  pavilhao3.com + instagram.com/pavilhao_3
        ↓ tools/scrape_*.py
  .tmp/raw_scrape/
        ↓ tools/classify_logos.py (Claude vision)
  .tmp/classified/manifest.json
        ↓ tools/inpaint_watermarks.py (IOPaint)
  .tmp/cleaned/
        ↓ tools/optimize_images.py (sharp → AVIF + WebP)
  public/images/portfolio/<slug>/<width>.{avif,webp}
  src/content/portfolio.json

Site (static, built by Astro):
  visitor → Vercel CDN → static HTML + AVIF/WebP images
```

---

## Architecture

```
┌──────────────────────────────────────────┐
│  Python pipeline (tools/)                │  ← scrape + clean + optimize
│  Run on demand by the agent              │     deterministic, testable
└────────────────┬─────────────────────────┘
                 │ writes
                 ▼
┌──────────────────────────────────────────┐
│  public/images/  +  src/content/*.json   │  ← single source of truth for media
└────────────────┬─────────────────────────┘
                 │ read at build time
                 ▼
┌──────────────────────────────────────────┐
│  Astro static site (src/)                │  ← dumb renderer, no runtime logic
│  Tailwind, content collections           │
└────────────────┬─────────────────────────┘
                 │ vercel deploy
                 ▼
                CDN
```

### Golden Rules
1. **Python prepares, Astro consumes** — no scraping or AI calls at request time
2. **Site is static** — every page renders to HTML at build; zero serverless functions in v1
3. **Images live on disk** — `public/images/` is the source of truth, committed to the repo
4. **WordPress-portable** — keep templates semantic; no Astro-only logic that won't translate to WP page templates
5. **No backend until asked** — contact form is UI-only with a mock success state

---

## Key Files & Structure

```
src/
  pages/            ← /, /services, /portfolio, /about, /contact, /__styleguide
  components/       ← Nav, Footer, Hero, SectionHeader, CaseCard, ServiceTile,
                      MetricStrip, MarqueeBrands, FilterBar, ContactSplit
  layouts/Base.astro
  content/          ← portfolio/ services/ MDX + config.ts schemas
  styles/global.css
public/images/      ← portfolio/<slug>/<width>.{avif,webp}, services/, brand/
tools/              ← Python pipeline (see workflows/scrape_and_clean_images.md)
workflows/          ← SOPs the agent follows step-by-step
.tmp/               ← raw_scrape/, classified/, cleaned/  (regenerable, gitignored)
docs/superpowers/specs/  ← design specs and implementation plans
```

---

## Environment Variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Claude vision calls for logo classification |
| `IG_USERNAME` *(optional)* | Instagram login if anonymous scrape is rate-limited |
| `IG_PASSWORD` *(optional)* | Same — only used when the user opts to sign in |
| `PUBLIC_SITE_URL` | Canonical URL for OG tags, sitemap (`https://gamingxpo.com`) |

`.env` is gitignored. Never commit secrets.

---

## What Should NOT Change

- The WAT layering — Python tools must stay deterministic; Astro must stay dumb
- The static-first model — do not add SSR routes, edge functions, or DB calls without explicit approval
- The brand decision — site is **Gamingxpo.com**, not Pavilhão 3
- The "physical logos stay, watermarks go" rule — a logo on a booth wall / t-shirt / sign is social proof; never inpaint it
- The mockup-first scope — do not wire up Resend, Supabase, CRMs, or analytics beyond Plausible without approval

---

## Known Constraints

- **Instagram scraping is fragile.** IG breaks scrapers frequently. If `instaloader` fails anonymously, pause and ask the user to sign in — they have agreed to handle login on demand.
- **Vision API costs** ≈ $0.003/image with prompt caching. Audit cost before bulk runs > 500 images.
- **IOPaint on CPU** runs ~10s/image. Acceptable for a one-time clean; do not put it in a hot path.
- **Vercel hobby plan** — fine for static. If we ever add serverless, watch the 10s timeout.

---

## Brand

- **Name:** Gamingxpo.com
- **Positioning:** Premium global builder of iGaming event booths and stands
- **Voice:** English-first, editorial, confident, restrained
- **Palette:** `#0A0A0B` near-black bg • `#F5F4F1` warm off-white text • `#E6FF3D` electric-lime accent (single accent, used sparingly)
- **Type:** Inter Tight 600/700 display, Inter 400 body, 18px / 1.6 / max 65ch
- **Motion:** subtle scroll reveals, slow Ken Burns hero, 200ms hover ease — no parallax stutter, no scroll-jacking
- **Imagery:** 16:9, 1920w minimum, cropped to architecture not crowds

---

# Claude Behavior Rules
## These apply to every session in this project.

---

## 1. Always Use Superpowers

This repo lives inside the WAT framework and follows the `superpowers` skill library. **Use the relevant skill before acting:**

| Situation | Skill |
|---|---|
| Starting any creative work (new feature, page, component) | `superpowers:brainstorming` → design before code |
| You have a spec and need to write the plan | `superpowers:writing-plans` |
| You have a written plan and are about to execute it | `superpowers:executing-plans` |
| Hitting a bug or unexpected behavior | `superpowers:systematic-debugging` |
| About to claim something is "done" / "passing" / "fixed" | `superpowers:verification-before-completion` |
| Implementing a feature or bugfix | `superpowers:test-driven-development` where the code supports tests |
| Building UI / page / component | `frontend-design` (after design is approved) |

Never skip a skill because the task "feels simple." The 1% rule applies.

---

## 2. Auto-Commit Every Change

After every meaningful file edit or creation:

```bash
git add <changed files>
git commit -m "clear, specific description"
git push   # only when on a feature branch with a remote
```

- One commit per logical change — do not batch
- Co-author every commit: `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`
- Branch per phase (`phase-0-scaffold`, `phase-1-scrape`, …) — merge only after the user's gate-pass

---

## 3. Screenshot-Driven Development

For any visible UI change:

1. Start dev server if not running: `npm run dev` (background)
2. Screenshot before — Playwright (`webapp-testing` skill) or `seo-visual` subagent
3. Make the change
4. Screenshot after — confirm it actually looks right
5. Iterate until correct **before** marking the task done
6. The user should never be the visual QA

Dev URL: `http://localhost:4321` (Astro default).

---

## 4. WAT Framework Discipline

This repo inherits the WAT layering from `c:\Users\User\Desktop\CLAUDE.md`:

- **Workflows** (`workflows/*.md`) — SOPs the agent reads before running a tool. Update them when you learn something new (rate limits, quirks, gotchas). Never overwrite without asking.
- **Tools** (`tools/*.py`) — deterministic Python scripts. Look here before building anything new.
- **`.env`** — every secret. Never inline credentials in code.
- **`.tmp/`** — intermediates only. Regenerable. Never commit.

When something breaks: read the error, fix the tool, **verify the fix** (don't just claim it), update the workflow.

---

## 5. State Preservation in UI

When navigating between sections (portfolio filters, tabs):
- Never reset state on navigation — preserve filter selection, scroll position
- Use `localStorage` for active filter / view across reloads
- "Back" must restore the previous state exactly

---

## 6. UI Standards

- **Compact over bloated** — no forced scrolling for basic operations
- **Images fill space** — no hard `maxHeight` cap that clips
- **Buttons never clip** — action bars use `flex-wrap`
- **Responsive by default** — `clamp()` for fluid widths
- **No duplicate UI** — don't repeat info already shown in the side strip / nav

---

## 7. Coding Standards

### Do
- Small, focused changes — one feature per commit
- Loading + error states for every async operation (when we get to a contact backend in a later milestone)
- Components < ~400 lines — split if larger
- Self-host fonts (`Inter`, `Inter Tight`) — no Google Fonts runtime call

### Don't
- Don't add features beyond what was asked
- Don't refactor surrounding code while fixing a bug
- Don't add error handling for impossible scenarios
- Don't create abstractions for one-time patterns
- Don't leave `console.log` in production code
- Don't hardcode content that belongs in `src/content/`
- Don't call third-party services directly from the browser

---

## 8. Mockup-First Discipline

Until the user explicitly approves a backend:
- Contact form submits to a static "thanks" state
- No newsletter signups, no CRMs, no analytics events firing to remote servers
- `mailto:` fallbacks are acceptable

When the user lifts the mockup constraint, the contact backend (Resend or Supabase) becomes its own brainstorming → spec → plan cycle.

---

## Token-Saving

`.claudeignore` (project root):
```
node_modules/
dist/
.astro/
.next/
build/
out/
package-lock.json
bun.lockb
yarn.lock
pnpm-lock.yaml
*.min.js
*.min.css
*.map
.tmp/
public/images/
*.log
```

Use `Grep` / `Glob` directly. No need for a separate `find-relevant.js` script — Astro projects are small enough.

---

## Quick Reference

| Task | Command |
|---|---|
| Start dev server | `npm run dev` |
| Build for prod | `npm run build` |
| Preview prod build | `npm run preview` |
| Run scrape | `python tools/scrape_pavilhao3.py && python tools/scrape_instagram.py` |
| Classify logos | `python tools/classify_logos.py` |
| Inpaint watermarks | `python tools/inpaint_watermarks.py` |
| Optimize images | `python tools/optimize_images.py` |
| Deploy | `git push` (Vercel auto-deploys main) |

---

## Summary

**What this project is:** Premium agency-grade marketing site for Gamingxpo.com, a global iGaming booth/stand builder.
**Main rule:** Python prepares assets, Astro renders static HTML, nothing else runs at request time.
**Never break:** WAT layering, mockup-first scope, "physical logos stay, watermarks go" rule.
**Always do:** invoke superpowers skills first, auto-commit per change, screenshot every UI change, verify before claiming done.
