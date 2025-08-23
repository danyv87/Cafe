import types
import sys

import pytest

from gui.materia_prima_dialogs import solicitar_datos_materia_prima_masivo
from controllers.materia_prima_controller import ALLOWED_UNIDADES


def _setup_fake_tk(monkeypatch):
    created = {
        "comboboxes": [],
        "entries": [],
        "button": None,
        "showerror": [],
        "top": None,
        "root": None,
    }
    mainloop_cb = {"func": None}

    class _Widget:
        def __init__(self, *args, **kwargs):
            pass

        def pack(self, *args, **kwargs):
            pass

        def grid(self, *args, **kwargs):
            pass

        def bind(self, *args, **kwargs):
            pass

        def config(self, **kwargs):
            pass

    class Root:
        def __init__(self):
            created["root"] = self
            self.quit_called = False

        def withdraw(self):
            pass

        def mainloop(self):
            if mainloop_cb["func"]:
                mainloop_cb["func"]()

        def quit(self):
            self.quit_called = True

        def destroy(self):
            pass

    class Toplevel(_Widget):
        def __init__(self, root):
            created["top"] = self
            self.destroyed = False

        def title(self, *args, **kwargs):
            pass

        def geometry(self, *args, **kwargs):
            pass

        def resizable(self, *args, **kwargs):
            pass

        def destroy(self):
            self.destroyed = True

    class Canvas(_Widget):
        def create_window(self, *args, **kwargs):
            pass

        def configure(self, *args, **kwargs):
            pass

        def yview(self, *args, **kwargs):
            pass

    class Frame(_Widget):
        pass

    class Scrollbar(_Widget):
        def __init__(self, *args, command=None, **kwargs):
            self.command = command

        def set(self, *args, **kwargs):
            pass

    class Label(_Widget):
        pass

    class Checkbutton(_Widget):
        def __init__(self, *args, variable=None, text="", **kwargs):
            self.variable = variable
            self.text = text
            self.command = None

        def config(self, **kwargs):
            if "command" in kwargs:
                self.command = kwargs["command"]
            if "text" in kwargs:
                self.text = kwargs["text"]

    class Combobox(_Widget):
        def __init__(self, *args, values=None, width=None, **kwargs):
            self.values = values or []
            self.value = ""
            created["comboboxes"].append(self)

        def get(self):
            return self.value

    class Entry(_Widget):
        def __init__(self, *args, width=None, **kwargs):
            self.value = ""
            created["entries"].append(self)

        def get(self):
            return self.value

    class Button(_Widget):
        def __init__(self, *args, text="", command=None, **kwargs):
            created["button"] = command

    class BooleanVar:
        def __init__(self, value=False):
            self._value = value

        def get(self):
            return self._value

        def set(self, value):
            self._value = value

    dummy_ttk = types.SimpleNamespace(
        Frame=Frame,
        Scrollbar=Scrollbar,
        Label=Label,
        Checkbutton=Checkbutton,
        Combobox=Combobox,
        Entry=Entry,
        Button=Button,
    )

    dummy_messagebox = types.SimpleNamespace(
        showerror=lambda title, msg, parent=None: created["showerror"].append(
            (title, msg)
        )
    )

    dummy_tk = types.SimpleNamespace(
        Tk=Root,
        Toplevel=Toplevel,
        Canvas=Canvas,
        BooleanVar=BooleanVar,
        BOTH="both",
        NORMAL="normal",
        DISABLED="disabled",
        ttk=dummy_ttk,
        messagebox=dummy_messagebox,
    )

    monkeypatch.setitem(sys.modules, "tkinter", dummy_tk)
    monkeypatch.setitem(sys.modules, "tkinter.ttk", dummy_ttk)
    monkeypatch.setitem(sys.modules, "tkinter.messagebox", dummy_messagebox)

    return created, mainloop_cb


def test_masivo_gui_rejects_invalid_unit(monkeypatch):
    created, mainloop_cb = _setup_fake_tk(monkeypatch)

    def handler():
        created["comboboxes"][0].value = "invalid"
        created["entries"][0].value = "10"
        created["entries"][1].value = "5"
        created["button"]()

    mainloop_cb["func"] = handler

    res = solicitar_datos_materia_prima_masivo([
        {"nombre_producto": "harina"}
    ])

    assert res == {}
    assert created["showerror"]
    assert not created["top"].destroyed
    assert not created["root"].quit_called


def test_masivo_gui_accepts_valid_unit(monkeypatch):
    created, mainloop_cb = _setup_fake_tk(monkeypatch)

    def handler():
        created["comboboxes"][0].value = ALLOWED_UNIDADES[0]
        created["entries"][0].value = "10"
        created["entries"][1].value = "5"
        created["button"]()

    mainloop_cb["func"] = handler

    res = solicitar_datos_materia_prima_masivo([
        {"nombre_producto": "azucar"}
    ])

    assert res == {"azucar": (ALLOWED_UNIDADES[0], 10.0, 5.0)}
    assert created["showerror"] == []
    assert created["top"].destroyed
    assert created["root"].quit_called

