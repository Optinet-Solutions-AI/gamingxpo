# Manus-Inspired Premium Refresh

**Date:** 2026-05-15
**Status:** approved
**Author:** Claude + John (Gamingxpo)
**Scope:** Home page visual refresh only. Other pages untouched this round.

## Context

The current Gamingxpo.com home renders cream-throughout with a 4-image collage hero. A reference build by Manus (https://pavilhao3-bb7clvrf.manus.space/) reads as more premium because of three things:

1. Dark, near-black hero with a single large booth photograph.
2. A dark, full-bleed stats strip immediately below the hero, with no visible seam.
3. A dark CTA band above the footer.

Manus's mid-sections (services, selected work) are weaker than ours — their "Selected Work" is tinted text boxes with no real images, no testimonials, no team-on-home, no brand marquee.

This refresh grafts Manus's dark hero / stats / CTA rhythm onto our richer content layer. Cream sections in between stay as they are.

## Goals

- Hero reads premium and iGaming-appropriate at first paint.
- Social proof (200+ booths, 14 countries) hits before the user scrolls.
- Brand color system collapses to one accent (amber-orange), retiring `coral` and demoting `pop` (lime).
- No regression to existing pages, content, or pipeline.

## Non-goals

- No restyling of `/portfolio`, `/portfolio/[project]`, `/services`, `/about`, `/contact` this round.
- No backend wiring on the contact form (still mockup per CLAUDE.md).
- No logo redesign. No font swap.
- No new content collections, no scrape re-runs.

## Architecture impact

None to the WAT layers. This is purely a presentation change:

- Tailwind tokens (`tailwind.config.cjs`)
- Three Astro components touched, one new component
- One page (`src/pages/index.astro`)
- No changes to Python pipeline, content schema, routing, or `public/images/`.

## Design decisions (locked from brainstorming)

| Decision | Choice | Reason |
|---|---|---|
| Theme rhythm | Dark hero + dark stats + cream middle + dark CTA | Mirrors Manus, keeps content sections legible |
| Hero image | Single large booth photo, Ken-Burns | Cleaner than the 4-image collage; matches reference |
| Accent color | Amber-orange (`#F59E0B`) | Closer to Manus; warmer than current `#F5C84B`; retires lime + coral as primary accents |
| Headline copy | Keep ours ("Stand out at every iGaming event in the world.") | More iGaming-specific than Manus's generic "Built Like a Product, Not a Pop-up" |
| ContactSplit on home | Drop it | New `CtaBand` replaces it on home; `/contact` page still owns the full form |

## Color tokens (target state in `tailwind.config.cjs`)

```js
colors: {
  bg:       '#F7F4EF',  // unchanged — cream
  'bg-alt': '#FFFFFF',  // unchanged — white card
  fg:       '#14110D',  // unchanged — espresso ink
  muted:    '#6E665A',  // unchanged
  line:     '#E5E0D7',  // unchanged
  ink:      '#0A0A0B',  // SHIFT from #1A1A1A → spec value (true near-black, matches Manus dark)
  accent:   '#F59E0B',  // SHIFT from #F5C84B → warmer amber-orange (Manus parity)
  'accent-dim': '#B45309', // NEW — amber that survives WCAG AA on cream (#F7F4EF)
  // RETIRE: pop, coral, bg-deep — no longer referenced
}
```

`bg-deep` (`#1F1A14`) is replaced by `ink` for dark surfaces. `pop` and `coral` are removed; any remaining references must be migrated to `accent` or deleted.

## Component-by-component changes

### 1. `src/components/Hero.astro` — rebuild

**Outgoing:** cream bg, 4-image grid (6-col x 6-row), three decorative shapes (amber dot, ink square, coral bar), eyebrow + headline + sub + CTA pair + avatar pile.

**Incoming:**
- `<section>` becomes `bg-ink text-bg` with `relative` positioning and a subtle grain overlay (existing `bg-grain` token, opacity ~15%).
- Two-column grid, `lg:grid-cols-12`, text spans 6, image spans 6.
- Left column:
  - Eyebrow: `text-accent` uppercase, tracking 0.25em.
  - Headline: `font-display text-display-xl text-bg max-w-[14ch]`.
  - Sub: `text-bg/70 text-body max-w-prose`.
  - CTA pair: primary `bg-accent text-ink` pill, secondary `border border-bg/30 text-bg` ghost.
  - Social proof row: avatar pile (3 thumb circles) + "200+ booths shipped across 14 countries" in `text-bg/60 text-xs`.
- Right column:
  - Single `<picture>` element, full height (`h-[520px] lg:h-[640px]`), `rounded-2xl overflow-hidden`.
  - Image source: `cover` from current selection logic (first `portfolio_grade` + `booth_exterior`, excluding `DUMMY_PROJECTS`).
  - Ken Burns animation kept (`motion-safe:animate-[kenburns_24s_ease-out_infinite_alternate]`).
  - AVIF + WebP source set at 1920w.
- Decorative shapes (amber dot, ink square, coral bar) removed.
- Bottom of section uses `pb-0` so the dark continues seamlessly into MetricStrip.

### 2. `src/components/MetricStrip.astro` — restyle dark

**Outgoing:** white card on cream with thin amber left-bar accent on each metric.

**Incoming:**
- Section background `bg-ink text-bg`, no top border, no bottom border.
- `pt-0` so it sits flush against the hero (looks like one continuous dark surface).
- Metric values: `font-display text-display-md text-bg`.
- Labels: `text-bg/60 text-xs uppercase tracking-wider`.
- Left amber accent bar kept (`bg-accent`), now reads as a hairline on dark.
- Bottom of strip has a thicker bottom padding so it transitions cleanly to the next cream section.

### 3. `src/components/Nav.astro` — scroll-aware variant

**Outgoing:** always-on `bg-bg/80 backdrop-blur-md border-b border-line` sticky nav.

**Incoming:**
- Initial state when at top of page on dark hero: `bg-transparent text-bg`, link text `text-bg/70 hover:text-bg`, CTA pill `bg-accent text-ink`.
- After scrolling past hero (use `IntersectionObserver` on a sentinel `<div>` placed at the bottom of the Hero section, or a simple `scrollY > heroHeight` listener — pick the IntersectionObserver, no scroll polling): nav transitions to current cream style (`bg-bg/80 backdrop-blur-md text-ink`).
- Transition is a 200ms ease on `background-color, border-color, color`.
- On pages without a dark hero (`/services`, `/portfolio`, `/about`, `/contact`), Nav stays in the existing cream state from first paint. This is handled by a prop (`darkHeroSentinel?: boolean`) or by detecting absence of the sentinel — pick the sentinel approach so the Nav component does not need to know which page it's on.

### 4. `src/components/CtaBand.astro` — new

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│      Ready to build the booth that gets the room?      │
│      One vendor. One accountable lead. Built in Lisbon,│
│      shipped worldwide.                                │
│                                                        │
│      [ Start your booth → ]                            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

- Section: `bg-ink text-bg`, full-bleed, `py-section`.
- Inner container: `max-w-layout mx-auto px-6 text-center`.
- Headline: `font-display text-display-lg max-w-[20ch] mx-auto`.
- Sub: `text-bg/70 text-body max-w-prose mx-auto mt-4`.
- CTA: amber pill identical to hero primary, links `/contact`.
- Props: `headline`, `sub`, `cta` (label + href). Default content baked in.

### 5. `src/pages/index.astro` — page composition

Current order:
```
Hero → MetricStrip → Selected work → What we do → Testimonials → Team → MarqueeBrands → ContactSplit
```

New order:
```
Hero → MetricStrip → Selected work → What we do → Testimonials → Team → MarqueeBrands → CtaBand
```

`ContactSplit` import + render removed from `index.astro` only. The component file stays (still used on `/contact` if applicable — verify during implementation).

## Files touched (canonical list)

Core changes:
1. `tailwind.config.cjs` — color token shifts (`ink`, `accent`, add `accent-dim`, retire `pop`/`coral`/`bg-deep`)
2. `src/components/Hero.astro` — rebuild
3. `src/components/MetricStrip.astro` — restyle dark
4. `src/components/Nav.astro` — add scroll-aware variant via sentinel
5. `src/components/CtaBand.astro` — new file
6. `src/pages/index.astro` — swap ContactSplit → CtaBand

Token migration sweep (results of pre-spec grep, all real):
7. `src/styles/global.css` lines 27, 31, 32 — delete `--bg-deep`, `--pop`, `--coral` CSS custom properties
8. `src/components/Footer.astro` line 5 — `bg-bg-deep` → `bg-ink`
9. `src/components/CaseCard.astro` line 14 — `group-hover:text-coral` → `group-hover:text-accent-dim` (WCAG: amber `#F59E0B` on cream is 2.3:1, fails AA for large text. `accent-dim` `#B45309` is ~5.1:1, passes AA)
10. `src/pages/portfolio.astro` line 53 — `group-hover:text-coral` → `group-hover:text-accent-dim`
11. `src/pages/portfolio/[project].astro` line 130 — `group-hover:text-coral` → `group-hover:text-accent-dim`

Verified non-issues (do NOT touch):
- `src/data/projects.json` line 148, 196 — contain the English word "pop-up" in project descriptions, not the token name
- `src/pages/about.astro` line 55 — "Built like a product, not a pop-up." English copy, not the token
- `src/components/Hero.astro` line 30 `bg-coral` — being deleted by the Hero rebuild (item 2)
- `ContactSplit.astro` is referenced by `services.astro`, `[project].astro`, `contact.astro`, `about.astro`, `styleguide.astro` and stays in the codebase. Only the `index.astro` import is removed.

## Validation

Screenshot-driven, per CLAUDE.md section 3:

1. Baseline screenshots already captured at `.tmp/compare/ours_home_full.png` and `.tmp/compare/manus_home_full.png`.
2. After implementation, capture `.tmp/compare/ours_home_full_after.png` at 1440x900.
3. Confirm visually:
   - Hero is dark, single image, amber CTA.
   - Stats strip is flush against hero (no seam).
   - Mid sections (Selected work, services, testimonials, team, brands) unchanged.
   - CtaBand sits above Footer, is dark, has amber CTA.
   - Nav is transparent on hero, cream after scroll.
4. Mobile viewport at 390x844 — verify hero stack reflows, image sits below text, all CTAs still touchable.
5. Lighthouse pass on `npm run build && npm run preview` — Performance / SEO / Accessibility ≥ 95 each, per CLAUDE.md "Quality bar".

## Risks / open questions

- **Mobile hero height**: at 390w, a 640px tall image dominates the fold. Implementation should clamp hero image height to `clamp(280px, 60vh, 640px)` on mobile.
- **Amber-on-cream contrast**: WCAG AA requires ≥ 4.5:1 for body text. `#F59E0B` on cream `#F7F4EF` is ~2.3:1 — fine for large CTA copy, NOT fine for eyebrow text on cream sections. Use `accent-dim` (`#B45309`, ratio ~5.1:1) anywhere amber-on-cream appears as small text.
- **Color migration sweep**: must grep for `pop`, `coral`, `bg-deep` before commit and migrate any stragglers. Skip the `pop` reference in the Logo if intentional brand mark (check during implementation, decide then).
- **Nav sentinel approach**: if IntersectionObserver complicates the Astro hydration story, fall back to a single passive scroll listener with `requestAnimationFrame` throttling. Both are fine for this case.

## Out of scope (explicit)

- Portfolio listing page
- Project detail pages
- Services page
- About page
- Contact page
- Mobile nav drawer
- Dark mode toggle
- Per-page hero variants
- Analytics
- Contact backend

These remain on the cream design system. A second spec will cover propagating the dark / amber accent into them if needed.

## Definition of done

- All 7 file changes merged on a single branch.
- Before/after screenshots committed to `.tmp/compare/`.
- One commit per logical change, co-authored per CLAUDE.md.
- `npm run build` produces zero warnings.
- Lighthouse home ≥ 95 on Performance / SEO / Accessibility.
- No references to `pop`, `coral`, `bg-deep` remain in `src/`.
