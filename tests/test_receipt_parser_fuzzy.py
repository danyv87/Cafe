from unittest.mock import patch

from models.materia_prima import MateriaPrima
from utils import receipt_parser


def _fake_mps():
    return [
        MateriaPrima("Cafe", "kg", 10, id="1"),
        MateriaPrima("Leche", "l", 2, id="2"),
    ]


def test_buscar_materia_prima_fuzzy_success():
    with patch(
        "controllers.materia_prima_controller.listar_materias_primas",
        side_effect=_fake_mps,
    ):
        receipt_parser.clear_cache()
        mp = receipt_parser._buscar_materia_prima("Cafee")
        assert mp is not None
        assert mp.nombre == "Cafe"


def test_buscar_materia_prima_fuzzy_below_threshold():
    with patch(
        "controllers.materia_prima_controller.listar_materias_primas",
        side_effect=_fake_mps,
    ):
        receipt_parser.clear_cache()
        mp = receipt_parser._buscar_materia_prima("Lecha")
        assert mp is None
