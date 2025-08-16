import json
import os
from typing import List, Dict

from openai import OpenAI

client = OpenAI()


def parse_receipt_image(path: str) -> List[Dict]:
    """Parse a receipt image and extract purchased items.

    The function sends the image to an OpenAI multimodal model and expects a
    JSON array with ``producto``, ``cantidad`` and ``precio`` fields for each
    item found in the receipt.

    To authenticate requests the environment variable ``OPENAI_API_KEY`` must
    be defined before calling this function.

    Parameters
    ----------
    path:
        Path to an image (``.jpeg``, ``.jpg`` or ``.png``) containing the receipt.

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
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    if not path.lower().endswith((".jpeg", ".jpg", ".png")):
        raise ValueError(
            "Unsupported format: only .jpeg, .jpg or .png images are allowed"
        )

    with open(path, "rb") as f:
        image_bytes = f.read()

    prompt = (
        "Devuelve un arreglo JSON de objetos con las claves 'producto', "
        "'cantidad' y 'precio' presentes en este recibo."
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image": image_bytes},
                ],
            }
        ],
        response_format={"type": "json_object"},
    )

    try:
        content = response.output[0].content[0].text
    except Exception:  # pragma: no cover - fallback for older SDKs
        content = response.choices[0].message["content"]

    data = json.loads(content)
    if isinstance(data, dict):
        # Allow returning an object with key 'items'
        data = data.get("items", [])
    return data
