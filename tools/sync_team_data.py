"""Sync src/data/team.json with the real team portrait slugs from portfolio.json.

Match by filename pattern — only `<FirstName>-<LastName>-scaled-e<digits>-1630x860` is a portrait.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools._common import ROOT

# Real team from pavilhao3.com /we/ page
TEAM_DEFS = [
    {
        "match": "andre-maricato-silva",
        "name": "André Silva",
        "role": "CEO",
        "bio": "Leads the company and the iGaming strategy. Put Gamingxpo on the SiGMA, ICE, and G2E floors.",
    },
    {
        "match": "fatima-nunes",
        "name": "Fátima Nunes",
        "role": "Finance & HR",
        "bio": "Runs operations, finance, and the people side of the business. Every invoice and every team member passes through her desk.",
    },
    {
        "match": "alexandre-machado",
        "name": "Alexandre Machado",
        "role": "Account Manager",
        "bio": "Senior account lead. Single point of contact for some of our largest iGaming clients across Europe and LATAM.",
    },
    {
        "match": "carla-trapola",
        "name": "Carla Trapola",
        "role": "Account Manager",
        "bio": "Event-cycle specialist — the operators that show at three or four iGaming expos a year. Calendar planning is her game.",
    },
    {
        "match": "francisco-leitao",
        "name": "Francisco Leitão",
        "role": "Account Manager",
        "bio": "Brings deep production knowledge to the client-facing side. Ask 'can we build that?' and he answers honestly.",
    },
    {
        "match": "vanda-nave",
        "name": "Vanda Nave",
        "role": "Production",
        "bio": "Production lead. Translates renders into joinery, hardware, and logistics. Knows every supplier and every shortcut.",
    },
    {
        "match": "eliana-rodrigues",
        "name": "Eliana Rodrigues",
        "role": "Production",
        "bio": "Workshop production. Drives the build calendar from first cut to crating. Nothing ships late on her watch.",
    },
    {
        "match": "isabel-vargas",
        "name": "Isabel Vargas",
        "role": "Designer",
        "bio": "Designer focused on space + material storytelling. The booth that feels coherent up close is usually her layout call.",
    },
    {
        "match": "vasco-branco",
        "name": "Vasco Branco",
        "role": "Designer",
        "bio": "Lead designer. Renders the booth that closes the deal. Specialises in iGaming brand-system translations to physical environments.",
    },
    {
        "match": "giovanna-laurito",
        "name": "Giovanna Laurito",
        "role": "Designer",
        "bio": "Designer with a strong typography and signage focus. The 30-metre brand-read on every booth is mostly her doing.",
    },
]


def main():
    portfolio = json.loads((ROOT / "src" / "data" / "portfolio.json").read_text(encoding="utf-8"))

    out = []
    for member in TEAM_DEFS:
        # Find the slug that starts with this match string
        slug = None
        for p in portfolio:
            if p["slug"].startswith(member["match"]):
                slug = p["slug"]
                break
        if not slug:
            print(f"WARN: no portrait found for {member['name']} (match='{member['match']}')")
            continue
        out.append({
            "name": member["name"],
            "role": member["role"],
            "bio": member["bio"],
            "src_base": f"/images/portfolio/{slug}",
        })

    team_path = ROOT / "src" / "data" / "team.json"
    team_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out)} team members → src/data/team.json")
    for m in out:
        print(f"  {m['name']} — {m['role']}")


if __name__ == "__main__":
    main()
