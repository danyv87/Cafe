import sys
import types

import pytest

from utils import gemini_receipt_parser


def test_parse_receipt_image_unsupported_extension(tmp_path, monkeypatch):
    dummy_path = tmp_path / "receipt.gif"
    dummy_path.touch()

    dummy_google = types.ModuleType("google")
    dummy_genai = types.ModuleType("google.genai")
    dummy_google.genai = dummy_genai
    monkeypatch.setitem(sys.modules, "google", dummy_google)
    monkeypatch.setitem(sys.modules, "google.genai", dummy_genai)

    with pytest.raises(ValueError, match="Unsupported format"):
        gemini_receipt_parser.parse_receipt_image(str(dummy_path))
