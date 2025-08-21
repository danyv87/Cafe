"""Lightweight stub of the :mod:`pytesseract` module for tests.

The real ``pytesseract`` dependency is quite heavy and not available in the
execution environment.  Tests monkeypatch :func:`image_to_string` to provide
deterministic outputs so the implementation below merely satisfies the import
and provides a minimal default behaviour.
"""

from __future__ import annotations

from typing import Any


def image_to_string(_image: Any, lang: str | None = None) -> str:  # pragma: no cover - trivial
    """Dummy replacement for the real OCR function.

    The function returns an empty string but is normally patched in unit tests
    to return specific contents.
    """

    return ""

