import os
import json
import dataclasses
import sqlite3
from pathlib import Path
from typing import Any, Union
from uuid import uuid4


def _invoice_to_dict(inv: Any) -> dict:
    """Return *inv* as a plain dictionary.

    Supports objects from dataclasses, Pydantic ``BaseModel`` (v1/v2) and
    plain dictionaries.  Raises ``TypeError`` for unsupported objects.
    """

    if inv is None:
        raise TypeError("inv cannot be None")

    # Pydantic v2
    if hasattr(inv, "model_dump"):
        return inv.model_dump()
    # Pydantic v1
    if hasattr(inv, "dict"):
        return inv.dict()
    # dataclasses
    if dataclasses.is_dataclass(inv):
        return dataclasses.asdict(inv)
    # already a mapping
    if isinstance(inv, dict):
        return dict(inv)

    raise TypeError("Unsupported invoice object type")


def save_invoice(
    inv: Any, destination: Union[str, os.PathLike, sqlite3.Connection]
) -> str:
    """Persist *inv* to ``destination`` and return its identifier.

    ``destination`` can be a directory path where a JSON representation of the
    invoice will be stored, or a ``sqlite3.Connection`` instance in which case
    the data is inserted into a table named ``invoices``.  ``inv`` is expected to
    be an instance of ``InvoiceOut`` (or compatible) that can be converted to a
    dictionary via ``model_dump()``, ``dict()`` or ``dataclasses.asdict``.

    Returns
    -------
    str
        The identifier of the saved invoice.  If ``inv`` does not include one,
        a new UUID4-based identifier is generated.
    """

    data = _invoice_to_dict(inv)
    invoice_id = data.get("id") or data.get("invoice_id") or uuid4().hex

    if isinstance(destination, sqlite3.Connection):
        cur = destination.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, data TEXT)"
        )
        cur.execute(
            "INSERT OR REPLACE INTO invoices (id, data) VALUES (?, ?)",
            (invoice_id, json.dumps(data)),
        )
        destination.commit()
        return invoice_id

    # treat destination as path
    dest_path = Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)
    file_path = dest_path / f"{invoice_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return invoice_id


def list_invoices(source: Union[str, os.PathLike, sqlite3.Connection]) -> list[str]:
    """Return all invoice identifiers stored in ``source``.

    ``source`` can be a directory path containing JSON files or a
    ``sqlite3.Connection`` from which invoice identifiers will be queried.
    """

    if isinstance(source, sqlite3.Connection):
        cur = source.cursor()
        try:
            cur.execute("SELECT id FROM invoices")
        except sqlite3.OperationalError:
            return []
        return [row[0] for row in cur.fetchall()]

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(str(source))
    if not path.is_dir():
        raise ValueError("source debe ser un directorio o conexión SQLite")
    return sorted(p.stem for p in path.glob("*.json"))

def load_invoice(
    source: Union[str, os.PathLike, sqlite3.Connection],
    invoice_id: str | None = None,
) -> dict:
    """Load a previously saved invoice from ``source``.

    Parameters
    ----------
    source:
        Directory path, JSON file path or ``sqlite3.Connection`` from which the
        invoice will be read.
    invoice_id:
        Identifier of the invoice.  Required when ``source`` is a directory or a
        database connection.  Ignored when ``source`` points directly to a JSON
        file.

    Returns
    -------
    dict
        A dictionary with all invoice fields, including the associated item
        fields.
    """

    # Source is an SQLite database connection
    if isinstance(source, sqlite3.Connection):
        if not invoice_id:
            ids = list_invoices(source)
            if len(ids) == 1:
                invoice_id = ids[0]
            else:
                if not ids:
                    raise FileNotFoundError("No hay facturas en la base de datos")
                raise ValueError(
                    "invoice_id es requerido para cargar desde la base de datos; "
                    f"opciones disponibles: {', '.join(ids)}"
                )
        cur = source.cursor()
        cur.execute("SELECT data FROM invoices WHERE id=?", (invoice_id,))
        row = cur.fetchone()
        if row is None:
            raise FileNotFoundError(f"Factura {invoice_id} no encontrada en la base de datos")
        return json.loads(row[0])

    # Treat source as path
    path = Path(source)
    if path.is_dir():
        if not invoice_id:
            ids = list_invoices(path)
            if len(ids) == 1:
                invoice_id = ids[0]
            else:
                if not ids:
                    raise FileNotFoundError("No hay facturas en el directorio")
                raise ValueError(
                    "invoice_id es requerido para cargar desde un directorio; "
                    f"opciones disponibles: {', '.join(ids)}"
                )
        path = path / f"{invoice_id}.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = ["save_invoice", "load_invoice", "list_invoices"]
