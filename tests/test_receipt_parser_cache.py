from unittest.mock import patch

from models.materia_prima import MateriaPrima
from utils import receipt_parser


def _fake_mps():
    return [
        MateriaPrima("Cafe", "kg", 10, id="1"),
        MateriaPrima("Leche", "l", 2, id="2"),
    ]


def test_buscar_materia_prima_cache_and_clear():
    """First lookup populates cache; clearing forces reload."""

    with patch(
        "controllers.materia_prima_controller.listar_materias_primas",
        side_effect=_fake_mps,
    ) as mock_listar:
        receipt_parser.clear_cache()
        mp1 = receipt_parser._buscar_materia_prima("Cafe")
        mp2 = receipt_parser._buscar_materia_prima("Cafe")
        assert mp1 is mp2
        assert mock_listar.call_count == 1

        receipt_parser.clear_cache()
        receipt_parser._buscar_materia_prima("Cafe")
        assert mock_listar.call_count == 2


def test_normalizar_items_uses_buscar_materia_prima_once_per_name():
    raw_items = [
        {"nombre_producto": "Cafe", "cantidad": 1, "precio": 1},
        {"nombre_producto": "Cafe", "cantidad": 2, "precio": 1},
        {"nombre_producto": "Leche", "cantidad": 1, "precio": 1},
    ]

    with patch("utils.receipt_parser._buscar_materia_prima") as mock_buscar:
        mock_buscar.side_effect = _fake_mps()
        receipt_parser._normalizar_items(raw_items)
        # Only two unique names, so the expensive lookup should run twice.
        assert mock_buscar.call_count == 2


def test_normalizar_items_accepts_alternative_keys():
    raw_items = [
        {
            "descripcion": "Cafe",
            "cantidad": 1,
            "precio_unitario": 3,
            "extra": "promo",
            "unidad_medida": "kg",
            "stock": 7,
        },
        {"descripcion": "Leche", "cantidad": 2, "precio_unitario": None, "subtotal": 4},
    ]

    with patch("utils.receipt_parser._buscar_materia_prima") as mock_buscar:
        mock_buscar.side_effect = _fake_mps()
        items, faltantes = receipt_parser._normalizar_items(raw_items)

    assert faltantes == []
    assert items[0]["costo_unitario"] == 3.0
    assert items[0]["descripcion_adicional"] == "extra: promo"
    assert items[0]["unidad_medida"] == "kg"
    assert items[0]["stock"] == 7.0
    assert items[1]["costo_unitario"] == 4.0

