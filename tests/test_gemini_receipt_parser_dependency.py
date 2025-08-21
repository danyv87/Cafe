import builtins
from pathlib import Path

import pytest

from utils import gemini_receipt_parser


def test_missing_google_genai(monkeypatch, tmp_path):
    dummy = tmp_path / "dummy.png"
    dummy.touch()

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "google.genai" or name.startswith("google.genai"):
            raise ImportError("No module named 'google.genai'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ImportError, match="pip install google-genai"):
        gemini_receipt_parser.parse_receipt_image(str(dummy))
