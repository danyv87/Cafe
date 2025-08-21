import os
import json
from pathlib import Path
from typing import Any, Union
import sqlite3
import dataclasses
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


def save_invoice(inv: Any, destination: Union[str, os.PathLike, sqlite3.Connection]) -> None:
    """Persist *inv* to ``destination``.

    ``destination`` can be a directory path where a JSON representation of the
    invoice will be stored, or a ``sqlite3.Connection`` instance in which case
    the data is inserted into a table named ``invoices``.  ``inv`` is expected to
    be an instance of ``InvoiceOut`` (or compatible) that can be converted to a
    dictionary via ``model_dump()``, ``dict()`` or ``dataclasses.asdict``.
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
        return

    # treat destination as path
    dest_path = Path(destination)
    dest_path.mkdir(parents=True, exist_ok=True)
    file_path = dest_path / f"{invoice_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

__all__ = ["save_invoice"]
