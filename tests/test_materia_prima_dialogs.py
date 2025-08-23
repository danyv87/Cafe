import types
import sys

from gui.materia_prima_dialogs import solicitar_datos_materia_prima_masivo
from controllers.materia_prima_controller import ALLOWED_UNIDADES


def _force_cli(monkeypatch):
    dummy_tk = types.SimpleNamespace(
        Tk=lambda: (_ for _ in ()).throw(RuntimeError("no gui")),
        ttk=object(),
        messagebox=object(),
    )
    monkeypatch.setitem(sys.modules, "tkinter", dummy_tk)


def test_masivo_cli_uses_allowed_units(monkeypatch):
    _force_cli(monkeypatch)
    inputs = iter(["crear", "1", "10", "5"])  # crear, unidad, costo, stock
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    res = solicitar_datos_materia_prima_masivo([
        {"nombre_producto": "azucar"}
    ])

    assert res == {"azucar": (ALLOWED_UNIDADES[0], 10.0, 5.0)}


def test_masivo_cli_rejects_invalid_unit(monkeypatch):
    _force_cli(monkeypatch)
    inputs = iter(["crear", "99"])  # invalid option
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    res = solicitar_datos_materia_prima_masivo([
        {"nombre_producto": "harina"}
    ])

    assert res == {}

