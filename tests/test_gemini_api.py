import base64

import pytest

from utils.gemini_api import get_gemini_api_key


def _encode_key(key: str, secret: str) -> bytes:
    secret_bytes = secret.encode()
    key_bytes = key.encode()
    encoded = bytes(
        b ^ secret_bytes[i % len(secret_bytes)] for i, b in enumerate(key_bytes)
    )
    return base64.b64encode(encoded)


def test_env_var(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "demo")
    assert get_gemini_api_key() == "demo"


def test_encrypted_file(monkeypatch, tmp_path):
    secret = "clave"
    key = "oculta"
    enc = _encode_key(key, secret)
    path = tmp_path / "key.enc"
    path.write_bytes(enc)

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_CONFIG_PATH", str(path))
    monkeypatch.setenv("GEMINI_CONFIG_SECRET", secret)

    assert get_gemini_api_key() == key


def test_missing_key(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_CONFIG_PATH", raising=False)
    monkeypatch.delenv("GEMINI_CONFIG_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="Falta la clave GEMINI_API_KEY"):
        get_gemini_api_key()
