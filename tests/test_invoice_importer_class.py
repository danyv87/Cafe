import sqlite3
from unittest.mock import patch

import pytest

from controllers.invoice_importer import InvoiceImporter


@patch("controllers.invoice_importer.receipt_parser.parse_receipt_image")
def test_invoice_importer_flow_success(mock_parse, tmp_path):
    mock_parse.return_value = (
        [
            {
                "producto_id": "1",
                "nombre_producto": "Cafe",
                "cantidad": 1,
                "costo_unitario": 10,
            },
            {
                "producto_id": "1",
                "nombre_producto": "Cafe",
                "cantidad": 2,
                "costo_unitario": 10,
            },
        ],
        [],
        {"total": 30},
    )
    importer = InvoiceImporter()
    items, faltantes, meta = importer.parse("img.jpg", [])
    assert meta["total"] == 30
    assert faltantes == []
    validados = importer.validate(items)
    agrupados = importer.match(validados)
    assert len(agrupados) == 1
    assert agrupados[0]["cantidad"] == 3
    factura = {
        "proveedor_id": "p",
        "proveedor": "Prov",
        "items": agrupados,
        "pendientes": [],
    }
    invoice_id = importer.persist(factura, tmp_path)
    assert (tmp_path / f"{invoice_id}.json").exists()


def test_invoice_importer_validate_error():
    importer = InvoiceImporter()
    with pytest.raises(ValueError, match="cantidad debe ser un número positivo"):
        importer.validate(
            [
                {
                    "producto_id": "1",
                    "nombre_producto": "Cafe",
                    "cantidad": 0,
                    "costo_unitario": 10,
                }
            ]
        )


def test_invoice_importer_persist_sqlite():
    importer = InvoiceImporter()
    conn = sqlite3.connect(":memory:")
    factura = {
        "proveedor_id": "p",
        "proveedor": "Prov",
        "items": [],
        "pendientes": [],
    }
    invoice_id = importer.persist(factura, conn)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoices WHERE id=?", (invoice_id,))
    assert cur.fetchone()[0] == 1
