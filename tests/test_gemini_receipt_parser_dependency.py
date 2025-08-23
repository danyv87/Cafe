import builtins

import pytest

from utils import gemini_receipt_parser


def test_missing_google_genai(monkeypatch, tmp_path):
    dummy = tmp_path / "dummy.png"
    dummy.touch()

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if (
            name in {"google.generativeai", "google.genai"}
            or name.startswith("google.generativeai")
            or name.startswith("google.genai")
        ):
            raise ImportError("No module named 'google-generativeai'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setenv("GEMINI_API_KEY", "dummy")
    monkeypatch.setattr(
        gemini_receipt_parser,
        "image_to_part",
        lambda path: {"inline_data": {"data": b"fake", "mime_type": "image/png"}},
    )

    with pytest.raises(ImportError, match="pip install google-generativeai"):
        gemini_receipt_parser.parse_receipt_image(str(dummy))
