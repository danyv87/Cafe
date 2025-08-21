"""Receipt parser powered by Gemini.

This module exposes :func:`parse_receipt_image` which sends a receipt image to
Google's Gemini generative AI models to obtain a textual transcription. Lines
containing product information are then matched with regular expressions to
extract ``producto``, ``cantidad`` and ``precio`` fields.

The Gemini API key is retrieved via :func:`utils.gemini_api.get_gemini_api_key`.
Ensure the key is available and the ``google-generativeai`` package is
installed.
"""

from __future__ import annotations

import os
import re
from typing import List, Dict

import google.generativeai as genai

from .gemini_api import get_gemini_api_key

# Palabras típicas de totales que queremos omitir al extraer ítems
_SUMMARY_KEYWORDS = {"total", "subtotal", "iva", "impuesto", "descuento"}


def _normalise_number(value: str) -> float:
    """Convierte textos numéricos en float asumiendo formato es-ES:
    - Punto como separador de miles.
    - Coma como separador decimal.

    Reglas:
      "23.900"   -> 23900
      "1.234,56" -> 1234.56
      "23,9"     -> 23.9
      "23900"    -> 23900.0
    """
    s = value.strip()
    # Quitar símbolos comunes
    s = s.replace("$", "").replace("Gs", "").replace("Gs.", "").replace("₲", "")
    # Dejar solo dígitos, signos, coma y punto
    s = re.sub(r"[^0-9,.\-]", "", s)

    if "," in s:
        # Caso es-ES: quitar puntos de miles y usar coma como decimal
        s = s.replace(".", "")
        s = s.replace(",", ".")
    else:
        # No hay coma: mantener posible decimal ".", pero quitar comas residuales
        s = s.replace(",", "")

    return float(s)


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image and extract purchased items.

    The function loads the image from ``path`` and sends it to Gemini to obtain
    the text. Each line is analysed with a regular expression expecting the
    structure ``producto cantidad precio`` where the numeric values may contain
    decimal points or commas. Matching lines are converted to dictionaries with
    the keys ``producto``, ``cantidad`` and ``precio``. If a line does not match
    this pattern, a heuristic fallback is applied that extracts the last two
    numeric values as quantity and price respectively. Lines containing keywords
    such as ``Total`` or ``IVA`` are ignored to reduce false positives from
    summary sections.

    Parameters
    ----------
    path: str
        Path to an image (``.jpeg``, ``.jpg`` or ``.png``) containing the
        receipt.

    Returns
    -------
    list of dict
        A list of dictionaries describing the items.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the path does not end with ``.jpeg``, ``.jpg`` or ``.png``.
    RuntimeError
        If the Gemini API request fails or returns no text.
    """
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError(
            "Unsupported format: only .jpeg, .jpg or .png images are allowed"
        )

    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    mime_type = "image/jpeg" if path.lower().endswith((".jpeg", ".jpg")) else "image/png"
    with open(path, "rb") as fh:
        image_bytes = fh.read()

    response = model.generate_content(
        [
            {"mime_type": mime_type, "data": image_bytes},
            # Pedimos sólo el texto crudo para luego parsearlo con regex
            "Transcribe el texto del recibo en español. Devuelve solo el texto.",
        ]
    )
    text = getattr(response, "text", "") or ""
    if not text.strip():
        raise RuntimeError("No se pudo obtener texto del recibo usando Gemini")

    # Regla principal: producto (texto), cantidad (número), precio (número)
    pattern = re.compile(
        r"^(?P<producto>.+?)\s+(?P<cantidad>\d{1,3}(?:[.,]?\d{3})*(?:[.,]\d+)?)\s+(?P<precio>\d{1,3}(?:[.,]?\d{3})*(?:[.,]\d+)?)(?:\s+\w+)?$"
    )

    items: List[Dict] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Omitir líneas de totales/subtotales/impuestos
        low = line.lower()
        if any(k in low for k in _SUMMARY_KEYWORDS):
            continue

        match = pattern.match(line)
        if match:
            producto = match.group("producto").strip()
            cantidad_txt = match.group("cantidad")
            precio_txt = match.group("precio")
        else:
            # Heurística: tomar los dos últimos números de la línea como (cantidad, precio)
            cleaned = line.replace("$", "").replace("₲", "")
            numbers = re.findall(r"\d{1,3}(?:[.,]?\d{3})*(?:[.,]\d+)?", cleaned)
            if len(numbers) < 2:
                continue
            precio_txt = numbers[-1]
            cantidad_txt = numbers[-2]
            # El producto es lo que queda antes de la cantidad
            try:
                idx_cantidad = cleaned.rfind(cantidad_txt)
                producto = cleaned[:idx_cantidad].strip(" :.-\t")
            except Exception:
                producto = ""
            if not producto:
                continue

        try:
            cantidad = _normalise_number(cantidad_txt)
            precio = _normalise_number(precio_txt)
        except ValueError:
            # Si no se puede convertir, saltar esta línea
            continue

        items.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "precio": precio,
            }
        )

    return items

  