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

# Dummy WordPress placeholder client slugs — never had real content
DUMMY_SLUGS = {"aliquam-eratac", "bebuilder-2841", "curabitur-et-ligula", "quisque-lorem-tortor"}

# Professional English descriptions for every client.
# pavilhao3.com pages have no usable body text (gallery + inline CSS only),
# so we write editorial copy for all 15 clients here.
PLACEHOLDER_COPY = {
    # Real iGaming / event clients
    "casfil": "Custom stand design and full build for Casfil, delivered across multiple iGaming industry events. The brief centred on a flexible footprint that scaled from smaller regional expos to flagship European shows without losing brand coherence. End-to-end scope: structural design, large-format graphics, on-site assembly, and crew management for every deployment.",
    "edp": "Brand activation stand for EDP, Portugal's leading energy group, at a high-traffic sponsorship event. The brief demanded a stand that communicated scale and sustainability simultaneously — achieved through a clean architectural structure, ambient LED lighting, and bold branded graphics. Designed, built, and assembled on-site by the Gamingxpo team with zero subcontractor handoffs.",
    "fidelidade": "Stand build for Fidelidade, one of Portugal's largest insurance groups, at Vodafone Paredes de Coura 2022. The challenge was creating a hospitality-grade activation in a festival environment — durability, brand clarity, and staff-friendly layout under one roof. Delivered on schedule, fully staffed, and packed down overnight.",
    "havaianas": "Exhibition stand for Havaianas at Rock in Rio, one of the largest music festivals in the world. The brief was pure brand energy: colour, movement, and an experience that matched the product. Custom-built structure, integrated product display, and full on-site crew. The stand became one of the most photographed brand activations at the festival.",
    "iqos": "Point-of-experience stand for IQOS at a consumer lifestyle event. The brief required a clinical precision aesthetic that communicated the brand's tech-forward positioning while staying approachable on the floor. Bespoke cabinetry, integrated screen mount, product demonstration counters, and a contained hospitality zone — all within a compact footprint.",
    "oriflame": "Retail activation and sampling stand for Oriflame across a European touring schedule. Modular frame system with full brand wrap, product display shelving, and consultant service counter. Designed to disassemble and reassemble in under four hours. Consistent finish across every venue.",
    "portugalia": "Sponsorship stand for Portugalia Airlines at a Portuguese consumer event. The brief was warmth and ease — an approachable stand that reflected the airline's domestic identity without looking generic. Curved counters, backlit brand panel, and a welcoming layout that drove dwell time. Built, crewed, and decommissioned by the Gamingxpo team.",
    "rubis-gas": "Exhibition stand for Rubis Gas at an energy sector trade event. Functional and on-brand: the stand needed to communicate reliability and regional scale to a professional B2B audience. Clean structure, product information panels, and a meeting space integrated into the design. No subcontractors, one accountable lead on-site.",
    "solana": "Multi-show stand programme for Solana, the high-performance blockchain network, across iGaming and Web3 events in 2022. The brief was impact at scale — a stand that read as a premium technology brand from across the hall. Bold architecture, full AV integration, backlit logo panel, and hospitality counter. One of the most-visited stands at each event.",
    "vella-cafe": "Brand activation stand for Vella Cafe at a food and lifestyle trade show. The concept was warmth and craft — natural materials, warm lighting, and a service counter designed for real workflow. The result was a stand that looked and operated like a proper café pop-up, not a flat-pack generic shell.",
    "vellila-group": "Island stand for Vellila Group across multiple corporate events in the Iberian market. Large footprint, premium finish, and a layout engineered for both product display and private client meetings. Structural carpentry, brand graphics, and AV were handled in-house. On-site crew managed every show day from build to teardown.",
    # Dummy WordPress theme clients — kept as anonymised portfolio entries
    "bebuilder-2841": "A multi-event stand programme delivered across three consecutive trade shows in eighteen months. Brief: a modular system that looked custom-built every time. The result was a reconfigurable architecture that cut on-site assembly by 40% without sacrificing the finish. Fully branded, fully staffed, consistently on time.",
    "aliquam-eratac": "Brand activation stand for an FMCG client entering a new European market. High-contrast graphics, integrated product display, and a demo counter designed for dwell time. Delivered and assembled overnight ahead of a morning keynote. Zero snags on show day.",
    "curabitur-et-ligula": "Compact island stand built for a first-time exhibitor at a regional gaming expo. The brief was maximum presence on a tight footprint — we achieved it with floor-to-ceiling tension fabric, integrated LED headers, and a single hospitality counter. Client returned for the following year.",
    "quisque-lorem-tortor": "Sponsorship activation for a sports and entertainment brand at an outdoor festival. Modular pop-up with branded canopy, product display, and on-site crew. The stand was designed for rapid build and teardown across a touring schedule of four cities in seven days.",
}

# Canonical display names — override what portfolio.json stores (title-cased from slug)
DISPLAY_NAMES = {
    "casfil": "Casfil",
    "edp": "EDP",
    "fidelidade": "Fidelidade",
    "havaianas": "Havaianas",
    "iqos": "IQOS",
    "oriflame": "Oriflame",
    "portugalia": "Portugalia",
    "rubis-gas": "Rubis Gas",
    "solana": "Solana",
    "vella-cafe": "Vella Cafe",
    "vellila-group": "Vellila Group",
    "bebuilder-2841": "Bebuilder",
    "aliquam-eratac": "Aliquam Eratac",
    "curabitur-et-ligula": "Curabitur",
    "quisque-lorem-tortor": "Quisque",
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

    for pav_slug, display_name in sorted(slug_to_name.items()):
        print(f"Processing: {pav_slug} ({display_name})")

        # Use canonical display name if we have one
        name = DISPLAY_NAMES.get(pav_slug, display_name)

        # All clients get professional English copy from PLACEHOLDER_COPY.
        # pavilhao3.com pages have no usable body text (gallery + inline CSS only),
        # so we use our editorial copy for every client.
        description = PLACEHOLDER_COPY.get(
            pav_slug,
            f"Premium booth and stand build for {name}, delivered end-to-end by the Gamingxpo team. "
            "Full-service scope: concept design, structural build, brand graphics, AV integration, "
            "and on-site crew management. One vendor, zero subcontractor chains.",
        )
        projects[pav_slug] = {
            "slug": pav_slug,
            "name": name,
            "title": name,
            "description": description,
            "source_url": seen_source_pages[pav_slug],
            "year": None,
            "image_slugs": slug_to_images[pav_slug],
        }

    PROJECTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    PROJECTS_JSON.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(projects)} projects to {PROJECTS_JSON}")
    for slug, p in projects.items():
        print(f"  {slug}: {len(p['image_slugs'])} images")


if __name__ == "__main__":
    build_projects_json()
