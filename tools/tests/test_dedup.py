from PIL import Image
from pathlib import Path
from tools.dedup import find_duplicates


def _make(path: Path, color):
    Image.new("RGB", (64, 64), color).save(path, "JPEG")


def test_finds_identical_images(tmp_path):
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    c = tmp_path / "c.jpg"
    _make(a, "red")
    _make(b, "red")
    _make(c, "blue")
    dups = find_duplicates([a, b, c])
    assert any({a, b}.issubset(set(group)) for group in dups)
    assert not any(c in group for group in dups)
