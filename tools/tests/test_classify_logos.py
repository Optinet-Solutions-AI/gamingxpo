import json
from pathlib import Path
from tools.classify_logos import ClassificationResult, parse_response

FIXTURE = Path(__file__).parent / "fixtures" / "sample_response.json"


def test_parse_response_returns_result():
    raw = FIXTURE.read_text(encoding="utf-8")
    result = parse_response(raw)
    assert isinstance(result, ClassificationResult)
    assert result.has_watermark is True
    assert len(result.watermark_boxes) == 1
    assert result.watermark_boxes[0].x == 0.85
    assert result.quality == "portfolio_grade"
    assert result.subject == "booth_exterior"


def test_parse_response_strips_markdown_fences():
    raw = '```json\n' + FIXTURE.read_text(encoding="utf-8") + '\n```'
    result = parse_response(raw)
    assert result.has_watermark is True
