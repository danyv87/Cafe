import logging
from typing import List, Tuple, Optional

from utils import receipt_parser

logger = logging.getLogger(__name__)


class InvoiceImporter:
    """Helper class to handle invoice parsing and persistence."""

    def parse(self, path: str, omitidos: Optional[List[str]] = None) -> Tuple[List[dict], List[dict], dict]:
        """Parse the receipt image located at ``path``.

        Returns the list of raw items, the list of items without a matching
        materia prima (``faltantes``) and any additional metadata provided by
        the parser.
        """

        try:
            parsed = receipt_parser.parse_receipt_image(path, omitidos=list(omitidos or []))
            if len(parsed) == 3:
                items, faltantes, meta = parsed
            else:  # backwards compatibility
                items, faltantes = parsed  # type: ignore[misc]
                meta = {}
        except (ConnectionError, TimeoutError) as e:
            raise ValueError(
                "No se pudo procesar la imagen por un problema de conexión."
            ) from e
        except NotImplementedError as e:
            raise ValueError(str(e)) from e
        except FileNotFoundError as e:
            raise ValueError("El comprobante no existe o no es accesible.") from e
        except ValueError as e:
            raise ValueError(str(e)) from e
        except RuntimeError as e:
            raise ValueError(str(e)) from e
        except Exception as e:  # pragma: no cover - unexpected errors
            raise ValueError("No se pudo interpretar la imagen del comprobante.") from e

        if not isinstance(items, list):
            raise ValueError("Formato de datos inválido del comprobante.")

        return items, list(faltantes), dict(meta)

    def validate(self, raw_items: List[dict]) -> List[dict]:
        """Validate and normalize raw items from the parser."""

        items_validados: List[dict] = []
        for item in raw_items:
            try:
                producto_id = item["producto_id"]
                nombre = item["nombre_producto"].strip()
                cantidad = float(item["cantidad"])
                costo_unitario = float(item["costo_unitario"])
                descripcion = item.get("descripcion_adicional", "")
            except Exception as e:
                raise ValueError("Datos de compra inválidos en la imagen.") from e

            if not (
                (isinstance(producto_id, int) and producto_id > 0)
                or (isinstance(producto_id, str) and producto_id.strip())
            ):
                raise ValueError("producto_id vacío o inválido en la imagen.")
            if not isinstance(nombre, str) or not nombre:
                raise ValueError("nombre_producto inválido en la imagen.")
            if cantidad <= 0:
                raise ValueError("cantidad debe ser un número positivo.")
            if costo_unitario <= 0:
                raise ValueError("costo_unitario debe ser un número positivo.")
            if not isinstance(descripcion, str):
                raise ValueError("descripcion_adicional debe ser texto.")

            items_validados.append(
                {
                    "producto_id": producto_id,
                    "nombre_producto": nombre,
                    "cantidad": cantidad,
                    "costo_unitario": costo_unitario,
                    "descripcion_adicional": descripcion,
                }
            )

        return items_validados

    def match(self, items: List[dict]) -> List[dict]:
        """Consolidate items with the same ``producto_id`` and cost."""

        agrupados = {}
        for item in items:
            clave = (item["producto_id"], item["costo_unitario"])
            if clave in agrupados:
                agrupados[clave]["cantidad"] += item["cantidad"]
            else:
                agrupados[clave] = item.copy()
        return list(agrupados.values())

    def persist(self, invoice: dict, destination: Optional[object]) -> Optional[str]:
        """Persist ``invoice`` to ``destination`` if provided."""

        if destination is None:
            return None

        from utils.invoice_utils import save_invoice  # local import to avoid heavy deps

        try:
            invoice_id = save_invoice(invoice, destination)
            logger.info(f"Factura guardada con ID {invoice_id}")
            return invoice_id
        except Exception as exc:  # pragma: no cover - persistence errors
            logger.error(f"No se pudo guardar la factura: {exc}")
            return None
