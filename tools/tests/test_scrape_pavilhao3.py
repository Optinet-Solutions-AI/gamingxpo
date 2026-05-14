from pathlib import Path
from tools.scrape_pavilhao3 import extract_image_urls

FIXTURE = Path(__file__).parent / "fixtures" / "pavilhao3_home.html"


def test_extract_image_urls_returns_absolute_urls():
    html = FIXTURE.read_text(encoding="utf-8")
    urls = extract_image_urls(html, base_url="https://pavilhao3.com/")
    assert len(urls) > 0
    for u in urls:
        assert u.startswith("https://"), f"not absolute: {u}"
        assert u.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
