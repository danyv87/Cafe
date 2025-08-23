import sys
import types

from utils import gemini_receipt_parser


def test_image_to_part_falls_back_to_raw_bytes(monkeypatch, tmp_path):
    bad = tmp_path / "corrupt.jpg"
    raw = b"not an image"
    bad.write_bytes(raw)

    dummy_types = types.ModuleType("google.genai.types")
    dummy_types.Part = types.SimpleNamespace(
        from_bytes=lambda data, mime_type: {"data": data, "mime_type": mime_type}
    )

    dummy_genai = types.ModuleType("google.genai")
    dummy_genai.types = dummy_types

    dummy_google = types.ModuleType("google")
    dummy_google.genai = dummy_genai

    monkeypatch.setitem(sys.modules, "google", dummy_google)
    monkeypatch.setitem(sys.modules, "google.genai", dummy_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", dummy_types)

    part = gemini_receipt_parser.image_to_part(str(bad))

    assert part["data"] == raw
    assert part["mime_type"] == "image/jpeg"

