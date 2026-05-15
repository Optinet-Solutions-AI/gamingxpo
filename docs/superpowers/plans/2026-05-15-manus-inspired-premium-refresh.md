# Manus-Inspired Premium Refresh — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Graft the dark hero + dark stats + dark CTA-band rhythm of the Manus reference onto the existing Gamingxpo home, keeping cream mid-sections (selected work, services, testimonials, team, brands) unchanged.

**Architecture:** Pure presentation change. Tailwind tokens + four Astro components + one new component + one page swap. Python pipeline, content collections, routing, and `public/images/` are untouched. Per CLAUDE.md, validation is screenshot-driven (no unit test runner in this Astro project).

**Tech Stack:** Astro 4, Tailwind 3, Playwright (for screenshot validation), `npm run dev` / `npm run build`.

**Spec:** [docs/superpowers/specs/2026-05-15-manus-inspired-premium-refresh.md](../specs/2026-05-15-manus-inspired-premium-refresh.md)

**Reference screenshots (baseline):**
- `.tmp/compare/manus_home_full.png` — Manus reference
- `.tmp/compare/ours_home_full.png` — current Gamingxpo home
- `.tmp/compare/manus_home_hero.png` — Manus hero crop
- `.tmp/compare/ours_home_hero.png` — current hero crop

---

## Task 1: Migrate color tokens

**Why first:** Every later task references `bg-ink` and `bg-accent` at their NEW values. Migrating first keeps every later screenshot honest.

**Files:**
- Modify: `tailwind.config.cjs` (whole `colors` block)
- Modify: `src/styles/global.css` lines 24-33 (`:root` block)
- Modify: `src/components/Footer.astro` line 5
- Modify: `src/components/CaseCard.astro` line 14
- Modify: `src/pages/portfolio.astro` line 53
- Modify: `src/pages/portfolio/[project].astro` line 130

- [ ] **Step 1: Update Tailwind color tokens**

Open `tailwind.config.cjs`. Replace the `colors` object with:

```js
colors: {
  bg: '#F7F4EF',
  'bg-alt': '#FFFFFF',
  fg: '#14110D',
  muted: '#6E665A',
  line: '#E5E0D7',
  ink: '#0A0A0B',
  accent: '#F59E0B',
  'accent-dim': '#B45309',
},
```

Removed: `bg-deep`, `pop`, `coral`. Shifted: `ink` (`#1A1A1A` → `#0A0A0B`), `accent` (`#F5C84B` → `#F59E0B`).

- [ ] **Step 2: Update CSS custom properties**

Open `src/styles/global.css`. Replace the `:root` block (lines 24-33) with:

```css
:root {
  --bg: #F7F4EF;
  --bg-alt: #FFFFFF;
  --fg: #14110D;
  --accent: #F59E0B;
  --accent-dim: #B45309;
  --ink: #0A0A0B;
}
```

- [ ] **Step 3: Migrate Footer to `bg-ink`**

In `src/components/Footer.astro` line 5, change:

```diff
- <footer class="bg-bg-deep text-bg mt-section">
+ <footer class="bg-ink text-bg mt-section">
```

- [ ] **Step 4: Migrate CaseCard hover color**

In `src/components/CaseCard.astro` line 14:

```diff
- <div class="text-display-md font-display mt-1 text-ink group-hover:text-coral transition-colors">{title ?? alt}</div>
+ <div class="text-display-md font-display mt-1 text-ink group-hover:text-accent-dim transition-colors">{title ?? alt}</div>
```

- [ ] **Step 5: Migrate portfolio index hover color**

In `src/pages/portfolio.astro` line 53:

```diff
- <div class="text-display-md font-display mt-1 text-ink group-hover:text-coral transition-colors">{p.name}</div>
+ <div class="text-display-md font-display mt-1 text-ink group-hover:text-accent-dim transition-colors">{p.name}</div>
```

- [ ] **Step 6: Migrate project detail hover color**

In `src/pages/portfolio/[project].astro` line 130:

```diff
- <div class="pt-3 font-display text-ink group-hover:text-coral transition-colors">{p.name}</div>
+ <div class="pt-3 font-display text-ink group-hover:text-accent-dim transition-colors">{p.name}</div>
```

- [ ] **Step 7: Verify no retired tokens remain in component/page code**

Run:
```bash
git grep -n -E "\b(bg-deep|bg-bg-deep|text-coral|bg-coral|border-coral|text-pop|bg-pop)\b" -- "src/**/*.astro" "src/**/*.ts" "src/**/*.tsx" "src/**/*.css"
```

Expected output: exactly one match — `src/components/Hero.astro` line 30 `bg-coral` (the decorative bar, will be deleted in Task 3). If any other match appears, migrate it to `accent` or `accent-dim` (small text → `accent-dim`; pills / large surfaces → `accent`) and re-run.

- [ ] **Step 8: Confirm build still works**

Run: `npm run build`
Expected: exits cleanly, "Complete!" or equivalent success message, zero warnings.

- [ ] **Step 9: Commit**

```bash
git add tailwind.config.cjs src/styles/global.css src/components/Footer.astro src/components/CaseCard.astro src/pages/portfolio.astro src/pages/portfolio/[project].astro
git commit -m "$(cat <<'EOF'
refactor(tokens): retire pop/coral/bg-deep, shift accent to amber-orange

- accent: #F5C84B -> #F59E0B  (warmer, matches Manus reference)
- ink:    #1A1A1A -> #0A0A0B  (true near-black per brand spec)
- new:    accent-dim #B45309  (passes WCAG AA for amber on cream)
- retire: pop, coral, bg-deep (unused after migration)

Hover states (CaseCard, portfolio, [project]) migrated to accent-dim.
Footer migrated from bg-bg-deep to bg-ink.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Build CtaBand component

**Files:**
- Create: `src/components/CtaBand.astro`

- [ ] **Step 1: Create the component**

Write `src/components/CtaBand.astro`:

```astro
---
const {
  eyebrow = 'Ready when you are',
  headline = 'Ready to build the booth that gets the room?',
  sub = 'One vendor. One accountable lead. Built in Lisbon, shipped worldwide.',
  cta = { href: '/contact', label: 'Start your booth' },
} = Astro.props;
---
<section class="bg-ink text-bg">
  <div class="max-w-layout mx-auto px-6 py-section text-center">
    <p class="text-accent text-xs tracking-[0.25em] uppercase font-medium">{eyebrow}</p>
    <h2 class="font-display text-display-lg mt-4 max-w-[20ch] mx-auto">{headline}</h2>
    <p class="mt-5 text-bg/70 text-body max-w-prose mx-auto">{sub}</p>
    <a
      href={cta.href}
      class="mt-9 inline-flex items-center gap-2 bg-accent text-ink font-medium px-7 py-3.5 rounded-full hover:bg-accent-dim hover:text-bg transition-colors"
    >
      {cta.label}
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M3 8h10m0 0L9 4m4 4l-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </a>
  </div>
</section>
```

- [ ] **Step 2: Smoke test via temporary import**

Temporarily add a render at the bottom of `src/pages/styleguide.astro` so we can visually verify before wiring it into the home. After the last existing element on that page, insert:

```astro
<CtaBand />
```

…with `import CtaBand from '../components/CtaBand.astro';` at the top of the frontmatter.

- [ ] **Step 3: Visual verification**

If `npm run dev` is not running, start it: `npm run dev` (background).
Wait until log shows `Local http://localhost:4321/`.

Run this Playwright snippet (save as `.tmp/screenshot_ctaband.py`):

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
OUT = Path(__file__).parent / "compare"
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.goto("http://localhost:4321/styleguide", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1000)
    page.screenshot(path=str(OUT / "ctaband_check.png"), full_page=True)
    b.close()
```

Run: `py -3 .tmp/screenshot_ctaband.py`
Open `.tmp/compare/ctaband_check.png` and confirm: dark band, white headline, amber CTA pill, eyebrow in amber.

- [ ] **Step 4: Remove smoke-test wiring**

Revert the temporary changes to `src/pages/styleguide.astro` (remove the import and the `<CtaBand />` line). The component stays on disk, untouched.

- [ ] **Step 5: Commit**

```bash
git add src/components/CtaBand.astro
git commit -m "$(cat <<'EOF'
feat(component): CtaBand - dark full-bleed CTA strip

New component for the dark CTA band that sits above the footer. Props:
eyebrow, headline, sub, cta. Defaults baked in for home-page use.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Rebuild Hero (dark + single image)

**Files:**
- Modify: `src/components/Hero.astro` (full rewrite)

- [ ] **Step 1: Replace the entire file**

Write `src/components/Hero.astro`:

```astro
---
import portfolio from '../data/portfolio.json';

const DUMMY_PROJECTS = new Set([
  'Bebuilder 2841', 'Quisque Lorem Tortor', 'Aliquam Eratac', 'Curabitur Et Ligula',
]);

const grade = portfolio.filter((p: any) =>
  p.quality === 'portfolio_grade'
  && (p.subject === 'booth_exterior' || p.subject === 'booth_interior')
  && !DUMMY_PROJECTS.has(p.project ?? '')
);
const cover = grade.find((p: any) => p.subject === 'booth_exterior') ?? grade[0];
const avatars = grade.slice(0, 3);

const {
  eyebrow = 'Booths & Stands · iGaming',
  headline = 'Stand out at every iGaming event in the world.',
  sub = 'We design, build, and ship booths for SiGMA, ICE, G2E, BiS. Wherever your brand needs to win the room.',
  cta = { href: '/contact', label: 'Start your booth' },
  secondary = { href: '/portfolio', label: 'See portfolio' }
} = Astro.props;
---
<section class="relative bg-ink text-bg overflow-hidden">
  <div class="absolute inset-0 bg-grain opacity-[0.06] pointer-events-none" aria-hidden="true"></div>

  <div class="relative max-w-layout mx-auto px-6 pt-24 pb-24 lg:pt-28 lg:pb-32 grid lg:grid-cols-12 gap-12 items-center">
    <div class="lg:col-span-6">
      <p class="text-accent text-xs tracking-[0.25em] uppercase font-medium">{eyebrow}</p>
      <h1 class="font-display text-display-xl text-bg mt-5 max-w-[14ch]">{headline}</h1>
      <p class="mt-6 max-w-prose text-bg/70 text-body">{sub}</p>
      <div class="mt-9 flex flex-wrap gap-3">
        <a href={cta.href} class="inline-flex items-center gap-2 bg-accent text-ink font-medium px-7 py-3.5 rounded-full hover:bg-accent-dim hover:text-bg transition-colors">
          {cta.label}
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10m0 0L9 4m4 4l-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </a>
        <a href={secondary.href} class="inline-flex items-center gap-2 border border-bg/25 text-bg px-7 py-3.5 rounded-full hover:bg-bg/10 hover:border-bg/40 transition-colors">
          {secondary.label}
        </a>
      </div>
      <div class="mt-12 flex items-center gap-5 text-xs text-bg/55">
        <div class="flex -space-x-2">
          {avatars.map(p => (
            <img src={`${p.src_base}/640.webp`} alt="" class="w-8 h-8 rounded-full border-2 border-ink object-cover" loading="lazy" />
          ))}
        </div>
        <span class="tracking-wide">200+ booths shipped across 14 countries</span>
      </div>
    </div>

    <div class="lg:col-span-6">
      {cover && (
        <picture>
          <source
            type="image/avif"
            srcset={`${cover.src_base}/960.avif 960w, ${cover.src_base}/1440.avif 1440w, ${cover.src_base}/1920.avif 1920w`}
            sizes="(min-width: 1024px) 50vw, 100vw"
          />
          <img
            src={`${cover.src_base}/1440.webp`}
            alt={cover.alt}
            class="w-full rounded-2xl object-cover bg-fg/40 motion-safe:animate-[kenburns_24s_ease-out_infinite_alternate]"
            style="height: clamp(280px, 60vh, 640px);"
            loading="eager"
            fetchpriority="high"
          />
        </picture>
      )}
    </div>
  </div>

  <div data-hero-sentinel aria-hidden="true" class="absolute bottom-0 left-0 right-0 h-px pointer-events-none"></div>
</section>

<style>
  @keyframes kenburns {
    from { transform: scale(1.0); }
    to   { transform: scale(1.06) translate(-0.8%, -0.8%); }
  }
</style>
```

Key changes from the previous Hero:
- `bg-ink text-bg` replaces cream
- Single `<picture>` instead of 4-image grid
- Hero image clamped: `clamp(280px, 60vh, 640px)` — addresses the mobile-too-tall risk from the spec
- All three decorative shapes (amber dot, ink square, coral bar) removed
- Avatar pile uses `border-ink` so it reads correctly on dark
- Added `data-hero-sentinel` div at the bottom — Task 5 uses this for scroll-aware Nav
- `1920w` AVIF source included for retina

- [ ] **Step 2: Verify the AVIF/WebP sources exist**

The new srcset references 1920.avif. Check it's actually generated:

```bash
ls public/images/portfolio/$(node -e "const p=require('./src/data/portfolio.json').find(x=>x.quality==='portfolio_grade'&&x.subject==='booth_exterior');console.log(p.src_base.split('/').pop())") | head
```

Expected: see `1920.avif`, `1440.avif`, `960.avif`, `640.avif`, plus webp twins. If `1920.avif` is missing, drop it from the `srcset` and use `1440.avif` as the largest — do not fail the task, log the omission in the commit message.

- [ ] **Step 3: Visual verification**

If `npm run dev` is not running, start it: `npm run dev` (background). Wait until log shows `Local http://localhost:4321/`.

Run:
```bash
py -3 .tmp/screenshot_compare.py
```

(That script from earlier already captures `ours_home_hero.png` and `ours_home_full.png`.)

Open `.tmp/compare/ours_home_hero.png`. Confirm:
- Background is near-black, not cream
- Single large booth photo on the right (not a 4-image grid)
- Headline in white, eyebrow in amber
- Amber pill CTA + ghost CTA below it
- Avatar pile with 3 thumbs + "200+ booths..." line under CTAs
- No amber dot, no ink square, no coral bar

- [ ] **Step 4: Commit**

```bash
git add src/components/Hero.astro
git commit -m "$(cat <<'EOF'
feat(hero): dark hero with single full-bleed booth shot

Replaces the cream 4-image collage with a dark near-black hero and one
large Ken-Burns booth photo. Matches the Manus reference rhythm.

- bg-ink + text-bg, subtle grain overlay
- Single <picture> with AVIF/WebP up to 1920w
- Image height clamped 280-640px for mobile/desktop
- Decorative shapes removed
- Adds data-hero-sentinel for the scroll-aware Nav (Task 5)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Restyle MetricStrip dark + flush

**Files:**
- Modify: `src/components/MetricStrip.astro` (whole file)

- [ ] **Step 1: Replace the file contents**

Write `src/components/MetricStrip.astro`:

```astro
---
const { items = [
  { value: '200+', label: 'booths built' },
  { value: '14', label: 'countries' },
  { value: '9', label: 'years' },
  { value: '40+', label: 'iGaming clients' },
] } = Astro.props;
---
<section class="bg-ink text-bg">
  <div class="max-w-layout mx-auto px-6 pt-0 pb-16 grid grid-cols-2 md:grid-cols-4 gap-8">
    {items.map((i: { value: string; label: string }) => (
      <div class="relative pl-4">
        <span class="absolute left-0 top-1 bottom-1 w-px bg-accent"></span>
        <div class="font-display text-display-md text-bg">{i.value}</div>
        <div class="text-bg/55 text-xs mt-2 tracking-widest uppercase">{i.label}</div>
      </div>
    ))}
  </div>
</section>
```

Changes from the previous version:
- `bg-bg-alt border-y border-line` → `bg-ink text-bg`
- `py-12` → `pt-0 pb-16` (the strip butts directly against the hero with no visible seam; hero already has `pb-24` so the negative space comes from there)
- Value color `text-ink` → `text-bg`
- Label color `text-muted text-sm` → `text-bg/55 text-xs uppercase tracking-widest`
- Amber left bar (`bg-accent`) kept

- [ ] **Step 2: Visual verification**

Run: `py -3 .tmp/screenshot_compare.py`
Open `.tmp/compare/ours_home_full.png`. Confirm:
- Hero dark area continues seamlessly into stats strip — no visible white/cream seam between them
- Stats values in big white type, labels in faded white uppercase
- The amber hairline on the left of each metric is visible

- [ ] **Step 3: Commit**

```bash
git add src/components/MetricStrip.astro
git commit -m "$(cat <<'EOF'
style(metrics): dark, full-bleed, flush against hero

Strip continues the dark hero surface so the two sections read as one
slab of social proof. Values white display-md, labels faded uppercase.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Scroll-aware Nav

**Files:**
- Modify: `src/components/Nav.astro` (whole file)

- [ ] **Step 1: Replace the file contents**

Write `src/components/Nav.astro`:

```astro
---
import Logo from './Logo.astro';

const links = [
  { href: '/', label: 'Home' },
  { href: '/services', label: 'Services' },
  { href: '/portfolio', label: 'Portfolio' },
  { href: '/about', label: 'About' },
  { href: '/contact', label: 'Contact' },
];
const current = Astro.url.pathname;
---
<nav
  data-nav
  data-state="cream"
  class="sticky top-0 z-50 transition-colors duration-200 bg-bg/80 backdrop-blur-md border-b border-line data-[state=dark]:bg-transparent data-[state=dark]:backdrop-blur-none data-[state=dark]:border-transparent"
>
  <div class="max-w-layout mx-auto flex items-center justify-between px-6 py-4">
    <Logo size={30} />
    <ul class="hidden md:flex gap-7 text-sm">
      {links.map(l => (
        <li>
          <a
            href={l.href}
            data-navlink
            class={`relative py-1 transition-colors ${current === l.href ? 'text-ink font-medium' : 'text-fg/70 hover:text-ink'} group-data-[state=dark]/nav:text-bg/70 group-data-[state=dark]/nav:hover:text-bg`}
          >
            {l.label}
            {current === l.href && <span class="absolute -bottom-0.5 left-0 right-0 h-px bg-ink group-data-[state=dark]/nav:bg-bg"></span>}
          </a>
        </li>
      ))}
    </ul>
    <a
      href="/contact"
      class="hidden md:inline-flex items-center gap-2 bg-ink text-bg font-medium px-4 py-2 rounded-full text-sm hover:bg-fg transition-colors group-data-[state=dark]/nav:bg-accent group-data-[state=dark]/nav:text-ink group-data-[state=dark]/nav:hover:bg-accent-dim group-data-[state=dark]/nav:hover:text-bg"
    >
      Start a project →
    </a>
  </div>
</nav>

<script>
  // Toggle nav between 'cream' and 'dark' based on whether the hero sentinel is in view.
  // If no sentinel exists on the page (every page except home), stay in cream.
  const nav = document.querySelector('[data-nav]') as HTMLElement | null;
  const sentinel = document.querySelector('[data-hero-sentinel]');

  if (nav && sentinel) {
    nav.dataset.state = 'dark';
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          nav.dataset.state = e.isIntersecting ? 'dark' : 'cream';
        }
      },
      { rootMargin: '-64px 0px 0px 0px', threshold: 0 }
    );
    io.observe(sentinel);
  }
</script>
```

Important wrinkles:
- The script picks up the sentinel from Task 3. If absent (any page that's not the home), nav stays in the default cream state.
- The sentinel is at the BOTTOM of the hero (Task 3 step 1). `rootMargin: '-64px'` accounts for the sticky nav height so the swap happens when the user has scrolled the nav past the hero, not when the sentinel first enters the viewport top.
- The `group-data-[state=dark]/nav:` selector requires Tailwind to treat the nav as a group. To make that work cleanly with arbitrary values, add `group/nav` to the `<nav>` class list.

- [ ] **Step 2: Fix the group class**

The version in Step 1 references `group/nav` in the `group-data-[state=dark]/nav:` selectors but the nav element doesn't actually carry `group/nav` yet. Edit the `<nav>` opening tag class list to ADD `group/nav` at the start:

```diff
- class="sticky top-0 z-50 transition-colors duration-200 bg-bg/80 backdrop-blur-md border-b border-line data-[state=dark]:bg-transparent data-[state=dark]:backdrop-blur-none data-[state=dark]:border-transparent"
+ class="group/nav sticky top-0 z-50 transition-colors duration-200 bg-bg/80 backdrop-blur-md border-b border-line data-[state=dark]:bg-transparent data-[state=dark]:backdrop-blur-none data-[state=dark]:border-transparent"
```

- [ ] **Step 3: Visual verification — home (dark hero)**

Run: `py -3 .tmp/screenshot_compare.py`
Open `.tmp/compare/ours_home_hero.png`. The cropped 1440x900 hero shot is taken at scrollY=0 so nav should be in DARK state. Confirm:
- Nav background transparent, no border line
- Link text white/faded white
- Logo readable on dark
- "Start a project" CTA pill is AMBER bg with dark text

- [ ] **Step 4: Visual verification — scroll past hero**

Add a second script `.tmp/screenshot_nav_scrolled.py`:

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
OUT = Path(__file__).parent / "compare"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.goto("http://localhost:4321/", wait_until="networkidle", timeout=30000)
    page.evaluate("window.scrollTo(0, 1200)")  # well past hero
    page.wait_for_timeout(600)  # let IO fire + transition settle
    page.screenshot(path=str(OUT / "ours_nav_scrolled.png"), full_page=False, clip={"x":0,"y":0,"width":1440,"height":120})
    b.close()
```

Run: `py -3 .tmp/screenshot_nav_scrolled.py`
Open `.tmp/compare/ours_nav_scrolled.png`. Confirm:
- Nav background is cream with backdrop blur (not transparent)
- Link text dark
- "Start a project" CTA pill is DARK bg (ink) with cream text — same as the pre-refresh look on other pages

- [ ] **Step 5: Visual verification — non-home page**

Add `.tmp/screenshot_nav_about.py`:

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
OUT = Path(__file__).parent / "compare"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
    page.goto("http://localhost:4321/about", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(400)
    page.screenshot(path=str(OUT / "ours_nav_about.png"), full_page=False, clip={"x":0,"y":0,"width":1440,"height":120})
    b.close()
```

Run: `py -3 .tmp/screenshot_nav_about.py`
Open `.tmp/compare/ours_nav_about.png`. Confirm nav is in CREAM state at scroll 0 because `/about` has no `data-hero-sentinel`.

- [ ] **Step 6: Commit**

```bash
git add src/components/Nav.astro
git commit -m "$(cat <<'EOF'
feat(nav): scroll-aware variant - transparent on dark hero, cream after

IntersectionObserver watches the [data-hero-sentinel] element from the
Hero component. While the sentinel is in view (i.e. hero is still on
screen), nav is transparent with white text + amber CTA. After scrolling
past it, nav transitions to the standard cream state.

Pages without a hero sentinel (services, portfolio, about, contact,
project detail) stay in cream from first paint.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Swap ContactSplit → CtaBand on home

**Files:**
- Modify: `src/pages/index.astro` (imports + JSX)

- [ ] **Step 1: Swap the import**

In `src/pages/index.astro` line 10, replace:

```diff
- import ContactSplit from '../components/ContactSplit.astro';
+ import CtaBand from '../components/CtaBand.astro';
```

- [ ] **Step 2: Swap the JSX**

In the same file, find the JSX line `<ContactSplit />` (it's the last element before `</Base>` — currently line 92 per the spec). Replace it with:

```astro
<CtaBand />
```

Do NOT add any props — the CtaBand defaults match the spec's intended copy.

- [ ] **Step 3: Verify ContactSplit is still imported elsewhere**

```bash
git grep -l "import ContactSplit" -- "src/**/*.astro"
```

Expected: `src/pages/services.astro`, `src/pages/about.astro`, `src/pages/contact.astro`, `src/pages/portfolio/[project].astro`, `src/pages/styleguide.astro` — exactly five matches. If `src/pages/index.astro` is in the list, Step 1 failed; redo it. If any expected page is missing, leave it — those pages weren't touched in this refresh.

- [ ] **Step 4: Visual verification of full home page**

Run: `py -3 .tmp/screenshot_compare.py`
Open `.tmp/compare/ours_home_full.png`. Confirm bottom of the home page (just above Footer) shows the dark CtaBand with amber CTA, NOT the two-column ContactSplit layout.

- [ ] **Step 5: Commit**

```bash
git add src/pages/index.astro
git commit -m "$(cat <<'EOF'
feat(home): swap ContactSplit for CtaBand

Home now ends with the dark CTA band before the footer, matching the
Manus reference rhythm. ContactSplit component file untouched; still
used on services / about / contact / project detail / styleguide.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Final validation

**Files:** none modified. Validation only.

- [ ] **Step 1: Build with zero warnings**

Run: `npm run build`
Expected: no warnings, completes successfully. If warnings appear (other than `LF will be replaced by CRLF` from git), fix the cause before continuing.

- [ ] **Step 2: Full-page comparison screenshots**

If dev server isn't running, start it: `npm run dev` (background). Wait for `Local http://localhost:4321/`.

Run: `py -3 .tmp/screenshot_compare.py`

This captures `.tmp/compare/ours_home_full.png` and `.tmp/compare/ours_home_hero.png` at 1440x900.

- [ ] **Step 3: Mobile viewport check**

Create `.tmp/screenshot_mobile.py`:

```python
from playwright.sync_api import sync_playwright
from pathlib import Path
OUT = Path(__file__).parent / "compare"
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_context(viewport={"width": 390, "height": 844}).new_page()
    page.goto("http://localhost:4321/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / "ours_home_mobile.png"), full_page=True)
    b.close()
```

Run: `py -3 .tmp/screenshot_mobile.py`
Open `.tmp/compare/ours_home_mobile.png`. Confirm:
- Hero text stacks above the image (single column)
- Hero image visible and not absurdly tall (target: < 60vh, ~500px)
- CTAs full-width or wrapping gracefully — no clipping
- Avatar pile + social proof line readable
- Stats strip stacks 2x2 on mobile
- CtaBand legible at the bottom

- [ ] **Step 4: Lighthouse check**

Run: `npx -y lighthouse http://localhost:4321/ --only-categories=performance,accessibility,seo --form-factor=desktop --preset=desktop --output=json --output-path=.tmp/lighthouse.json --chrome-flags="--headless" --quiet`

Then read the result:
```bash
node -e "const r=require('./.tmp/lighthouse.json');for(const k of ['performance','accessibility','seo']) console.log(k, Math.round(r.categories[k].score*100))"
```

Expected: each score ≥ 95. If any score < 95, capture the failing audits with:
```bash
node -e "const r=require('./.tmp/lighthouse.json');for(const k of Object.keys(r.audits)) if(r.audits[k].score!==null && r.audits[k].score<0.9) console.log(k, r.audits[k].score, '-', r.audits[k].title)"
```

…and address the top offenders before closing out. Common culprits at this stage:
- Hero image dimensions missing — add explicit `width`/`height` attrs
- Color contrast — verify all amber-on-cream uses `accent-dim`
- Preload key request — if hero image is `fetchpriority="high"` already, add `<link rel="preload" as="image" ...>` to `Base.astro` for the hero src (use 1440.webp for broadest support)

- [ ] **Step 5: Commit screenshots + lighthouse report**

```bash
git add .tmp/compare/ours_home_full.png .tmp/compare/ours_home_hero.png .tmp/compare/ours_home_mobile.png .tmp/compare/ours_nav_scrolled.png .tmp/compare/ours_nav_about.png .tmp/lighthouse.json
git commit -m "$(cat <<'EOF'
chore(validation): after-screenshots + lighthouse report for refresh

Captures the post-refresh state at 1440x900 desktop and 390x844 mobile,
plus the scroll-aware Nav states (dark over hero, cream after scroll,
cream on /about). Lighthouse scores attached.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Note: `.tmp/` is gitignored per CLAUDE.md. If the commit fails because the files are ignored, that's expected — open the screenshots locally to verify, then skip this commit step (no commit needed for ignored artifacts).

- [ ] **Step 6: Final grep — no retired tokens anywhere**

```bash
git grep -n -E "\b(bg-deep|bg-bg-deep|text-coral|bg-coral|border-coral|text-pop|bg-pop|--bg-deep|--pop|--coral)\b" -- src
```

Expected: NO matches. If any appear, migrate (small text → `accent-dim`, surfaces → `accent` or `ink`).

---

## Self-review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| Color tokens shifted (ink, accent, accent-dim) | Task 1 step 1 |
| `pop`, `coral`, `bg-deep` retired from `global.css` | Task 1 step 2 |
| Footer `bg-bg-deep` → `bg-ink` | Task 1 step 3 |
| CaseCard hover migration | Task 1 step 4 |
| portfolio.astro hover migration | Task 1 step 5 |
| [project].astro hover migration | Task 1 step 6 |
| Hero rebuilt — dark, single image, Ken Burns | Task 3 |
| Hero decorative shapes removed | Task 3 step 1 (explicit) |
| Mobile hero height clamped 280-640px | Task 3 step 1 (`clamp(280px, 60vh, 640px)`) |
| MetricStrip dark + flush against hero | Task 4 |
| Nav scroll-aware via sentinel | Task 5 |
| Sentinel placed in Hero | Task 3 step 1 (`<div data-hero-sentinel>`) |
| Nav stays cream on non-home pages | Task 5 step 5 verification |
| CtaBand component created | Task 2 |
| Home swap ContactSplit → CtaBand | Task 6 |
| ContactSplit untouched on other pages | Task 6 step 3 verification |
| Build with zero warnings | Task 7 step 1 |
| Lighthouse ≥ 95 on home | Task 7 step 4 |
| Mobile viewport verification | Task 7 step 3 |
| Final no-retired-tokens grep | Task 7 step 6 |

All spec requirements have tasks.

**Type / name consistency check:**
- `data-hero-sentinel` introduced in Task 3 step 1, consumed in Task 5 step 1 — same string ✓
- `accent-dim` introduced in Task 1 step 1, used in Task 1 steps 4/5/6, Task 2 step 1, Task 3 step 1, Task 5 step 1 — consistent ✓
- `group/nav` referenced in Task 5 step 1 selectors and added to the nav class list in Task 5 step 2 — matches ✓
- Hero `cover` variable referenced in `<picture>` — defined in same frontmatter ✓

**Placeholder scan:** none found.
