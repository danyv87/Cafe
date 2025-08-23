import sys
import types
import pytest

from utils import gemini_receipt_parser


def _setup_dummy_genai(monkeypatch, response):
    """Helper to register a dummy google.genai module returning ``response``."""

    class DummyGenerativeModel:
        def __init__(self, name):
            self.model_name = name

        def generate_content(self, *args, **kwargs):  # pragma: no cover - very small
            return response

    dummy_google = types.ModuleType("google")
    dummy_types = types.SimpleNamespace(
        Part=types.SimpleNamespace(
            from_text=lambda text: {"text": text},
            from_bytes=lambda data, mime_type: {"inline_data": {"data": data, "mime_type": mime_type}},
        ),
        Content=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    class DummyClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.models = types.SimpleNamespace(
                generate_content=lambda **kwargs: response
            )

    dummy_genai = types.SimpleNamespace(
        Client=lambda api_key: DummyClient(api_key),
        types=dummy_types,
    )
    dummy_google.generativeai = dummy_genai
    dummy_google.genai = dummy_genai
    monkeypatch.setitem(sys.modules, "google", dummy_google)
    monkeypatch.setitem(sys.modules, "google.generativeai", dummy_genai)
    monkeypatch.setitem(sys.modules, "google.genai", dummy_genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", dummy_types)
    return DummyGenerativeModel


def test_parse_receipt_image_success(monkeypatch, tmp_path):
    img = tmp_path / "ticket.jpg"
    img.write_bytes(b"fake")
    response = types.SimpleNamespace(
        text='[{"producto": "Pan", "cantidad": 2, "precio": 3.5}]'
    )
    _DummyModel = _setup_dummy_genai(monkeypatch, response)

    called = {}

    def fake_key():
        called["used"] = True
        return "APIKEY"

    monkeypatch.setattr(gemini_receipt_parser, "get_gemini_api_key", fake_key)

    items = gemini_receipt_parser.parse_receipt_image(str(img))

    assert items == [
        {
            "producto": "Pan",
            "cantidad": 2.0,
            "precio": 3.5,
            "unidad_medida": None,
            "costo_unitario": 3.5,
            "stock": 2.0,
        }
    ]
    assert called["used"]


def test_parse_receipt_image_bad_json(monkeypatch, tmp_path):
    img = tmp_path / "ticket.png"
    img.write_bytes(b"fake")
    response = types.SimpleNamespace(text="not json")
    _setup_dummy_genai(monkeypatch, response)
    monkeypatch.setattr(gemini_receipt_parser, "get_gemini_api_key", lambda: "KEY")

    with pytest.raises(ValueError):
        gemini_receipt_parser.parse_receipt_image(str(img))


def test_parse_receipt_image_maps_new_fields(monkeypatch, tmp_path):
    """The parser should map alternative item keys to the expected schema."""

    img = tmp_path / "recibo.png"
    img.write_bytes(b"fake")
    response = types.SimpleNamespace(
        text='[{"descripcion": "Pan", "cantidad": 2, "precio_unitario": null, "subtotal": 7, "extra": "promo"}]'
    )
    _setup_dummy_genai(monkeypatch, response)
    monkeypatch.setattr(gemini_receipt_parser, "get_gemini_api_key", lambda: "KEY")

    items = gemini_receipt_parser.parse_receipt_image(str(img))

    assert items == [
        {
            "producto": "Pan",
            "cantidad": 2.0,
            "precio": 7.0,
            "descripcion_adicional": "extra: promo",
            "unidad_medida": None,
            "costo_unitario": 7.0,
            "stock": 2.0,
        }
    ]


def test_normalize_numbers_scales_all_money_fields():
    inv = gemini_receipt_parser.InvoiceOut(
        items=[
            gemini_receipt_parser.Item(
                cantidad="1",
                precio="1.5",
                precio_unitario="1.5",
                subtotal="1.5",
            ),
            gemini_receipt_parser.Item(
                cantidad="2",
                precio="2.5",
                precio_unitario="2.5",
                subtotal="5",
            ),
        ],
        total="4.0",
        fecha="10/02/2024",
    )

    out = gemini_receipt_parser.normalize_numbers(inv, scale_policy="x1000")

    it0 = out.items[0]
    assert it0.precio == 1500.0
    assert it0.precio_unitario == 1500.0
    assert it0.subtotal == 1500.0
    assert out.total == 4000.0
    assert out.fecha == "2024-02-10"
