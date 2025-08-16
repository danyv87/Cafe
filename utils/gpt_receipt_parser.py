import json
try:
    import openai  # type: ignore
except Exception:  # pragma: no cover - handled in tests
    openai = None


def parse_receipt(image_path: str):
    """Parse a receipt image using OpenAI and return list of item dicts.

    The function expects the OpenAI completion to return a JSON string with
    a top level key ``items`` containing item data. Each item should define
    ``producto_id``, ``nombre_producto``, ``cantidad`` and ``costo_unitario``.
    """
    if openai is None:
        raise RuntimeError("OpenAI SDK is not installed")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Parse receipt: {image_path}"}],
    )
    content = response["choices"][0]["message"]["content"]
    data = json.loads(content)
    return data["items"]
