from __future__ import annotations

import base64
import json
import os
from typing import Dict, List

from openai import OpenAI

# =========================================================
# Cliente OpenAI
# =========================================================
def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key)

# =========================================================
# Catálogo de materias primas (cache + lookup)
# =========================================================
_MATERIAS_PRIMAS_CACHE: Dict[str, "MateriaPrima"] | None = None

def clear_cache() -> None:
    """Limpia la caché de materias primas."""
    global _MATERIAS_PRIMAS_CACHE
    _MATERIAS_PRIMAS_CACHE = None

def _buscar_materia_prima(nombre: str):
    """
    Devuelve la MateriaPrima cuyo nombre coincide (case-insensitive),
    o None si no se encuentra. Usa cache para evitar recargas.
    """
    global _MATERIAS_PRIMAS_CACHE
    try:
        from controllers.materia_prima_controller import listar_materias_primas
    except Exception:
        return None

    nombre_normalizado = nombre.strip().lower()

    if _MATERIAS_PRIMAS_CACHE is None:
        _MATERIAS_PRIMAS_CACHE = {
            mp.nombre.strip().lower(): mp for mp in listar_materias_primas()  # type: ignore
        }
    return _MATERIAS_PRIMAS_CACHE.get(nombre_normalizado)

# =========================================================
# Utilidades de normalización
# =========================================================
def _to_num(x):
    """Convierte strings con moneda y separadores a float; deja pasar si ya es numérico."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        # Limpia símbolos de moneda/espacios
        for sym in ("₲", "Gs.", "Gs", "Gs:", "Gs-", "G$", "$", "PYG"):
            s = s.replace(sym, "")
        s = s.replace(" ", "")
        # Convierte formato 1.234,56 -> 1234.56
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except Exception:
            pass
    return x

def _normalizar_items(raw_items: List[Dict]) -> List[Dict]:
    """
    Espera items con claves: producto/nombre_producto, cantidad, precio/costo_unitario.
    Mapea a tu esquema con producto_id, nombre_producto, cantidad, costo_unitario.
    """
    items: List[Dict] = []
    encontrados: Dict[str, "MateriaPrima"] = {}

    for raw in raw_items:
        nombre = raw.get("nombre_producto") or raw.get("producto")
        if not nombre:
            raise ValueError("Falta el nombre del producto en el comprobante")

        key = nombre.strip().lower()
        mp = encontrados.get(key)
        if mp is None:
            mp = _buscar_materia_prima(nombre)
            encontrados[key] = mp
        if not mp:
            raise ValueError(f"Materia prima '{nombre}' no encontrada")

        try:
            cantidad = _to_num(raw.get("cantidad", 0))
            precio = _to_num(raw.get("costo_unitario", raw.get("precio", 0)))
            cantidad = float(cantidad)
            precio = float(precio)
        except Exception as exc:
            raise ValueError("Cantidad o precio inválidos en el comprobante") from exc

        items.append({
            "producto_id": mp.id,
            "nombre_producto": mp.nombre,
            "cantidad": cantidad,
            "costo_unitario": precio,
            "descripcion_adicional": raw.get("descripcion_adicional", ""),
        })
    return items

# =========================================================
# Parser principal (ÚNICA definición)
# =========================================================
def parse_receipt_image(path: str) -> List[Dict]:
    """
    Si 'path' termina en .json -> carga lista de items (fallback offline).
    Si es imagen (.jpeg/.jpg/.png) -> usa OpenAI Responses API (gpt-4o-mini).
    Devuelve lista normalizada para tu app.
    """
    if not path:
        raise ValueError("path no puede estar vacío")

    # Fallback JSON (útil en pruebas u offline)
    if path.lower().endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as exc:
            raise ValueError("Archivo JSON de recibo no encontrado") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("JSON de recibo inválido") from exc
        if not isinstance(data, list):
            raise ValueError("El archivo JSON debe contener una lista de items")
        return _normalizar_items(data)

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    if ext not in (".jpeg", ".jpg", ".png"):
        raise ValueError("Unsupported format: only .jpeg, .jpg or .png images are allowed")

    # Prepara data URL (formato aceptado por Responses API para visión)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "png" if ext == ".png" else "jpeg"
    data_url = f"data:image/{mime};base64,{b64}"

    prompt = (
        "Devuelve un ARREGLO JSON con objetos {producto, cantidad, precio}. "
        "Usa números (punto decimal) en 'cantidad' y 'precio'. Sin texto extra."
    )

    inputs = [{
        "role": "user",
        "content": [
            {"type": "input_text", "text": prompt},
            {"type": "input_image", "image_url": data_url},
        ],
    }]

    client = _get_client()

    # Structured Outputs (json_schema). Si el entorno no acepta response_format, cae al except.
    schema = {
        "name": "items_recibo",
        "schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["producto", "cantidad", "precio"],
                "properties": {
                    "producto": {"type": "string"},
                    "cantidad": {"type": "number"},
                    "precio":   {"type": "number"},
                },
                "additionalProperties": False,
            },
        },
        "strict": True,
    }

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=inputs,
            response_format={"type": "json_schema", "json_schema": schema},
        )
        try:
            content = resp.output_text
        except Exception:
            content = resp.output[0].content[0].text
    except TypeError:
        # Entorno donde responses.create no acepta response_format
        resp = client.responses.create(model="gpt-4o-mini", input=inputs)
        try:
            content = resp.output_text
        except Exception:
            content = resp.output[0].content[0].text

    data = json.loads(content)
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        raise ValueError("La respuesta del modelo no es un arreglo JSON")

    return _normalizar_items(data)
