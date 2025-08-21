"""Utilities for handling the Gemini API key.

The module avoids embedding API keys in the source code. The key is retrieved
from the ``GEMINI_API_KEY`` environment variable. As a fallback an encrypted
configuration file can be used by specifying its path in ``GEMINI_CONFIG_PATH``
and the decryption secret in ``GEMINI_CONFIG_SECRET``.  The file must contain a
base64 encoded string obtained by XOR-ing the API key with the secret.
"""

from __future__ import annotations

import base64
import os

from dotenv import load_dotenv


def get_gemini_api_key() -> str:
    """Return the Gemini API key from a safe location.

    The search order is:

    1. The ``GEMINI_API_KEY`` environment variable.
    2. An encrypted file specified by ``GEMINI_CONFIG_PATH`` and decrypted using
       ``GEMINI_CONFIG_SECRET``.

    Raises
    ------
    RuntimeError
        If the API key cannot be found or decrypted.
    """

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    path = os.getenv("GEMINI_CONFIG_PATH")
    if path:
        secret = os.getenv("GEMINI_CONFIG_SECRET")
        if not secret:
            raise RuntimeError(
                "GEMINI_CONFIG_SECRET no está definido para descifrar el archivo de configuración."
            )
        try:
            with open(path, "rb") as fh:
                encoded = fh.read()
            decoded = base64.b64decode(encoded)
            secret_bytes = secret.encode()
            key_bytes = bytes(
                b ^ secret_bytes[i % len(secret_bytes)] for i, b in enumerate(decoded)
            )
            api_key = key_bytes.decode()
            if api_key:
                return api_key
        except FileNotFoundError as exc:  # pragma: no cover - path may be bad
            raise RuntimeError(
                "No se encontró el archivo de configuración cifrado."
            ) from exc
        except Exception as exc:  # pragma: no cover - decoding errors
            raise RuntimeError("No se pudo descifrar la clave de la API.") from exc

    raise RuntimeError(
        "Falta la clave GEMINI_API_KEY. Define la variable de entorno o proporciona un archivo de configuración cifrado."
    )
