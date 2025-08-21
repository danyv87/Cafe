import json
import sys
import types
from pathlib import Path

import pytest

from utils import gemini_receipt_parser


class _DummyResponses:
    """Helper to mock ``Client.responses``."""

    def __init__(self, payload: str):
        self._payload = payload

    def generate(self, **_: object):  # pragma: no cover - trivial
        return type("Resp", (), {"output_text": self._payload})()


class _DummyClient:
    def __init__(self, payload: str):
        self.responses = _DummyResponses(payload)


def _patch_client(monkeypatch, payload: str) -> None:
    """Patch ``google.genai.Client`` to return ``payload`` as the response."""

    dummy = types.SimpleNamespace(Client=lambda api_key: _DummyClient(payload))
    monkeypatch.setitem(sys.modules, "google", types.SimpleNamespace(genai=dummy))
    monkeypatch.setitem(sys.modules, "google.genai", dummy)


def _fake_image(tmp_path: Path) -> Path:
    path = tmp_path / "receipt.png"
    path.write_bytes(b"fake")
    return path


def test_parse_receipt_image_transforms(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "utils.gemini_receipt_parser.get_gemini_api_key", lambda: "demo"
    )

    data = [
        {"description": "Cafe", "quantity": 1, "price": 2.0},
        {"description": "Leche", "quantity": 2, "price": 3.0},
    ]
    payload = json.dumps(data)
    _patch_client(monkeypatch, payload)

    img = _fake_image(tmp_path)
    items = gemini_receipt_parser.parse_receipt_image(str(img))

    assert items == [
        {
            "nombre_producto": "Cafe",
            "cantidad": 1.0,
            "costo_unitario": 2.0,
            "descripcion_adicional": "",
        },
        {
            "nombre_producto": "Leche",
            "cantidad": 2.0,
            "costo_unitario": 3.0,
            "descripcion_adicional": "",
        },
    ]


def test_parse_receipt_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        gemini_receipt_parser.parse_receipt_image("missing.png")


def test_parse_receipt_image_invalid_response(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "utils.gemini_receipt_parser.get_gemini_api_key", lambda: "demo"
    )
    _patch_client(monkeypatch, "no-json")

    img = _fake_image(tmp_path)
    with pytest.raises(ValueError):
        gemini_receipt_parser.parse_receipt_image(str(img))

