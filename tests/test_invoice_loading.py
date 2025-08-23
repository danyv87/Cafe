from __future__ import annotations

import sqlite3
from utils.invoice_utils import save_invoice, load_invoice, list_invoices


def _sample_invoice(invoice_id: str | None = None):
    inv = {
        "proveedor_id": 1,
        "proveedor": "Proveedor",
        "items": [
            {
                "producto_id": 1,
                "nombre_producto": "Cafe",
                "cantidad": 2,
                "costo_unitario": 5,
                "descripcion_adicional": "tostado",
            }
        ],
        "pendientes": [],
    }
    if invoice_id:
        inv["id"] = invoice_id
    return inv


def test_load_invoice_from_directory(tmp_path):
    inv = _sample_invoice()
    invoice_id = save_invoice(inv, tmp_path)
    assert (tmp_path / f"{invoice_id}.json").exists()
    loaded = load_invoice(tmp_path, invoice_id)
    assert loaded["proveedor"] == "Proveedor"
    assert loaded["items"][0]["nombre_producto"] == "Cafe"
    assert loaded["items"][0]["descripcion_adicional"] == "tostado"


def test_load_invoice_from_db(tmp_path):
    inv = _sample_invoice()
    conn = sqlite3.connect(tmp_path / "inv.db")
    invoice_id = save_invoice(inv, conn)
    assert conn.execute("SELECT id FROM invoices").fetchone()[0] == invoice_id
    loaded = load_invoice(conn, invoice_id)
    assert loaded["proveedor_id"] == 1
    assert loaded["items"][0]["costo_unitario"] == 5
    conn.close()


def test_list_invoices_directory(tmp_path):
    save_invoice(_sample_invoice("inv1"), tmp_path)
    save_invoice(_sample_invoice("inv2"), tmp_path)
    ids = list_invoices(tmp_path)
    assert set(ids) == {"inv1", "inv2"}


def test_list_invoices_db(tmp_path):
    conn = sqlite3.connect(tmp_path / "inv.db")
    save_invoice(_sample_invoice("inv1"), conn)
    save_invoice(_sample_invoice("inv2"), conn)
    ids = list_invoices(conn)
    assert set(ids) == {"inv1", "inv2"}
    conn.close()


def test_default_load_single_invoice_directory(tmp_path):
    save_invoice(_sample_invoice("only1"), tmp_path)
    loaded = load_invoice(tmp_path)
    assert loaded["id"] == "only1"
    assert loaded["proveedor"] == "Proveedor"


def test_default_load_single_invoice_db(tmp_path):
    conn = sqlite3.connect(tmp_path / "inv.db")
    save_invoice(_sample_invoice("only1"), conn)
    loaded = load_invoice(conn)
    assert loaded["id"] == "only1"
    assert loaded["items"][0]["producto_id"] == 1
    conn.close()
