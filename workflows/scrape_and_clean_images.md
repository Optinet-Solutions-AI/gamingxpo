# SOP — Scrape and Clean Images

## Inputs
- `https://pavilhao3.com` (public web)
- `https://www.instagram.com/pavilhao_3` (anonymous first; sign-in if rate-limited)

## Steps

1. `py tools/scrape_pavilhao3.py` → writes `.tmp/raw_scrape/pavilhao3/*.jpg` + `pavilhao3.json`
2. `py tools/scrape_instagram.py` → writes `.tmp/raw_scrape/instagram/*.jpg` + `instagram.json`
3. `py tools/classify_logos.py` → writes `.tmp/classified/manifest.json`
4. `py tools/inpaint_watermarks.py` → writes `.tmp/cleaned/*.jpg` + `_diffs/*.png`
5. **User review gate** — open `.tmp/cleaned/_diffs/` and confirm inpaint quality
6. `py tools/optimize_images.py` → writes `public/images/portfolio/<slug>/*.{avif,webp}` and `src/content/portfolio.json`

## Gotchas captured during execution
(Update this section each time we learn something new.)

- Instagram rate-limits anonymous mode at ~50 requests; sign in early if scraping a large account.
- pavilhao3.com's gallery uses lightbox JS; original images may live in `<a href>` not `<img src>` — scraper handles both.
- IOPaint install pulls PyTorch (~2GB); install via `py -m pip install -e .[inpaint]` only when Phase 2 Task 15 starts.
