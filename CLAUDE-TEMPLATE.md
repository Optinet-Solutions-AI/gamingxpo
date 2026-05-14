# CLAUDE.md — [Project Name]

> Copy this file into any new project as CLAUDE.md and fill in the sections marked [CUSTOMIZE].
> Delete sections that don't apply. The more specific you are, the better Claude performs.

---

## Project Overview

[CUSTOMIZE: 2-4 sentences describing what this project is and what it does.]

- **Frontend:** [e.g. React / Next.js / Vite — deployed on Vercel]
- **Backend / Logic:** [e.g. Node.js API / n8n webhooks / Supabase Edge Functions]
- **Database:** [e.g. Supabase / Airtable / PostgreSQL]
- **AI:** [e.g. OpenAI GPT-4o / Anthropic Claude / Gemini]
- **Repo:** [github.com/your-org/your-repo]
- **Live URL:** [your-app.vercel.app]

---

## How the App Works

[CUSTOMIZE: Describe the main user flow step by step. Example:]

```
1. User does X
   ↓
2. App calls Y (API / webhook / database)
   ↓
3. Result shown to user
```

---

## Architecture

[CUSTOMIZE: Which layer owns what logic.]

```
┌─────────────────────┐
│   Frontend (Dumb)   │  ← Display + user input only. No business logic.
│   React / Next.js   │
└────────┬────────────┘
         │ API calls
         ▼
┌─────────────────────┐
│   Backend (Brain)   │  ← All logic lives here
│   [n8n / API / CF]  │───────► Database
└─────────────────────┘◄──────  [Supabase / Airtable]
```

### Golden Rules
1. **Frontend is DUMB** — display data and fire actions only, no logic
2. **Backend is the BRAIN** — all processing, validation, and AI calls
3. **Database is the MEMORY** — single source of truth
4. **No hardcoded data** — everything loaded dynamically

---

## Key Files & Structure

[CUSTOMIZE: List the files Claude will touch most often.]

```
src/
  components/     ← UI components
  pages/          ← Route pages
  hooks/          ← Custom React hooks
  types/          ← TypeScript types
api/              ← Serverless API routes
```

---

## Environment Variables

[CUSTOMIZE: List every env var the project uses and what it's for.]

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Base URL for API calls |
| `OPENAI_API_KEY` | OpenAI image/text generation |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase server-side key (never expose to client) |

---

## What Should NOT Change

[CUSTOMIZE: List things Claude must never touch or break.]

- [ ] The existing authentication flow
- [ ] The database schema (unless explicitly asked)
- [ ] Existing API contract / response shapes
- [ ] The overall UI layout and brand colors
- [ ] Any currently-working feature

---

## Known Constraints

[CUSTOMIZE: Technical limits Claude should be aware of.]

- Vercel hobby plan: 10-second function timeout (use `maxDuration: 300` for long AI calls)
- Supabase free: 500MB storage, 50k rows
- Rate limits: [list any API rate limits]
- [Any other hard limits]

---

## Brands / Tenants / Config

[CUSTOMIZE: If your app supports multiple brands, clients, or configurations, list them here.]

Example:
- Brand A — primary color #FF5500
- Brand B — primary color #0055FF

---

# Claude Behavior Rules
## These apply to every session in this project.

---

## 1. Auto-Commit Every Change

**After every file edit or creation, immediately:**
```bash
git add <changed files>
git commit -m "clear description of what changed"
git push
```

- Do not wait for the user to ask
- Do not batch multiple changes into one commit — commit as you go
- Use clear, specific commit messages (not "update files")
- Always co-author: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

---

## 2. Screenshot-Driven Development

**For any UI change:**
1. Start the dev server if not running: `npm run dev` (background)
2. Take a screenshot of the relevant page/component
3. Make the change
4. Take another screenshot to verify it looks correct
5. If it looks wrong — iterate until it looks right before moving on
6. Never rely on the user to spot visual bugs

**Dev server URL:** `http://localhost:[PORT]` — check package.json for the port.

**Screenshot tool:** Use the `seo-visual` subagent or Playwright.

---

## 3. Token-Saving: Read Only Relevant Files

**Before reading files, run:**
```bash
node scripts/find-relevant.js "<keyword>" --show-lines
```

This returns only the files that actually contain the relevant code.
Read those files. Do not scan the whole codebase.

**Examples:**
```bash
node scripts/find-relevant.js "ImageModal"
node scripts/find-relevant.js "supabase auth" --type ts
node scripts/find-relevant.js "webhook" --show-lines
```

**If `scripts/find-relevant.js` doesn't exist yet, create it** (see the Token-Saving Setup section below).

---

## 4. State Preservation When Switching Views

When the user navigates between sections (tabs, panels, library views):
- **Never reset state** on navigation — preserve form data, generated results, scroll position
- Use `localStorage` to persist the active tab/view across reloads
- Mount all tab content and hide/show with CSS rather than unmounting
- When a "Back" button is needed, it should restore exactly where the user was

Pattern:
```tsx
const [activeTab, setActiveTab] = useState(() => {
  try { return localStorage.getItem('app_activeTab') || 'default'; }
  catch { return 'default'; }
});
const handleTabChange = (tab) => {
  try { localStorage.setItem('app_activeTab', tab); } catch {}
  setActiveTab(tab);
};
```

---

## 5. UI Standards

- **Compact over bloated** — panels and modals should not force scrolling for basic operations
- **Images fill available space** — never add a hard `maxHeight` cap that clips images
- **Buttons never clip** — action bars use `flex-wrap` so they reflow on small screens
- **Responsive by default** — use `clamp()` for widths that need to scale with viewport
- **No duplicate UI** — if something is shown in the side strip, don't repeat it in the panel
- **Tooltips over labels** — for compact UI, use `title` attributes instead of visible text descriptions

---

## 6. Coding Standards

### Do
- Make small, focused changes — one feature or fix per commit
- Add loading and error states for every async operation
- Use environment variables for all URLs and keys
- Keep components under ~400 lines — split if larger
- Explain decisions briefly in comments when logic isn't obvious

### Don't
- Don't add features beyond what was asked
- Don't refactor surrounding code when fixing a bug
- Don't add error handling for impossible scenarios
- Don't create abstractions for one-time patterns (3 similar lines > premature abstraction)
- Don't leave `console.log` statements in production code
- Don't hardcode data that should come from a database or config
- Don't call external services (Airtable, Supabase, etc.) directly from the frontend

---

## 7. Error Handling Pattern

Every fetch call should follow this pattern:
```tsx
const [data,    setData]    = useState(null);
const [loading, setLoading] = useState(false);
const [error,   setError]   = useState<string | null>(null);

const load = async () => {
  setLoading(true);
  setError(null);
  try {
    const res = await fetch('/api/...');
    if (!res.ok) throw new Error(`Failed (${res.status})`);
    setData(await res.json());
  } catch (e) {
    setError(e instanceof Error ? e.message : 'Something went wrong');
  } finally {
    setLoading(false);
  }
};
```

---

## Token-Saving Setup

If this is a new project, create these two files once:

### `.claudeignore` (project root)
```
node_modules/
dist/
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
screenshots/
*.log
```

### `scripts/find-relevant.js`
```js
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const args      = process.argv.slice(2);
const keyword   = args.find(a => !a.startsWith('--'));
const showLines = args.includes('--show-lines');
const typeFlag  = args.indexOf('--type');
const extFilter = typeFlag !== -1 ? `.${args[typeFlag + 1]}` : null;

if (!keyword) {
  console.error('Usage: node scripts/find-relevant.js <keyword> [--show-lines] [--type ts|tsx|js]');
  process.exit(1);
}

const SKIP_DIRS  = new Set(['node_modules','dist','.next','build','out','.git','coverage','screenshots']);
const SEARCH_EXTS = new Set(['.ts','.tsx','.js','.jsx','.mjs','.json','.md','.env']);
const results = [];

function walk(dir) {
  let entries;
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
  for (const entry of entries) {
    if (entry.name.startsWith('.') && entry.name !== '.env') continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) { if (!SKIP_DIRS.has(entry.name)) walk(full); continue; }
    const ext = path.extname(entry.name).toLowerCase();
    if (extFilter && ext !== extFilter) continue;
    if (!SEARCH_EXTS.has(ext)) continue;
    try { if (fs.statSync(full).size > 300_000) continue; } catch { continue; }
    let content;
    try { content = fs.readFileSync(full, 'utf8'); } catch { continue; }
    const re = new RegExp(keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i');
    if (!re.test(content)) continue;
    const matchLines = [];
    content.split('\n').forEach((line, i) => { if (re.test(line)) matchLines.push({ n: i+1, text: line.trim() }); });
    results.push({ file: path.relative(process.cwd(), full), lines: matchLines });
  }
}

walk(process.cwd());
if (results.length === 0) { console.log(`No files found containing "${keyword}"`); process.exit(0); }
results.sort((a, b) => b.lines.length - a.lines.length);
console.log(`\nFiles relevant to "${keyword}" (${results.length} found):\n`);
for (const r of results) {
  console.log(`  ${r.file}  (${r.lines.length} match${r.lines.length !== 1 ? 'es' : ''})`);
  if (showLines) {
    for (const l of r.lines.slice(0, 5)) console.log(`    L${l.n}: ${l.text.slice(0, 120)}`);
    if (r.lines.length > 5) console.log(`    … and ${r.lines.length - 5} more`);
  }
}
console.log('\nTip: Read only these files to save tokens.');
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start dev server | `npm run dev` |
| Find relevant files | `node scripts/find-relevant.js "keyword" --show-lines` |
| Build for production | `npm run build` |
| Deploy | `git push` (auto-deploys via Vercel/Netlify) |
| [CUSTOMIZE: add more] | |

---

## Summary

**What this project is:** [one sentence]
**Main rule:** [one sentence — e.g. "Frontend is dumb, n8n is the brain"]
**Never break:** [comma-separated list of sacred features]
**Always do:** auto-commit + push, screenshot UI changes, use find-relevant.js first
