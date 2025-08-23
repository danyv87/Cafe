import json
import sqlite3
from utils.invoice_utils import save_invoice, load_invoice


def _sample_invoice():
    return {
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


def test_load_invoice_from_directory(tmp_path):
    inv = _sample_invoice()
    save_invoice(inv, tmp_path)
    file_path = next(tmp_path.glob("*.json"))

    loaded = load_invoice(file_path)
    assert loaded["proveedor"] == "Proveedor"
    assert loaded["items"][0]["nombre_producto"] == "Cafe"
    assert loaded["items"][0]["descripcion_adicional"] == "tostado"


def test_load_invoice_from_db(tmp_path):
    inv = _sample_invoice()
    conn = sqlite3.connect(tmp_path / "inv.db")
    save_invoice(inv, conn)
    invoice_id = conn.execute("SELECT id FROM invoices").fetchone()[0]

    loaded = load_invoice(conn, invoice_id)
    assert loaded["proveedor_id"] == 1
    assert loaded["items"][0]["costo_unitario"] == 5
    conn.close()
