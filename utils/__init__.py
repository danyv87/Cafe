"""Utility package for the Cafe application.

The module exposes the most commonly used helper submodules to make imports
within the project concise.  Submodules are intentionally not imported eagerly
in order to avoid importing heavy optional dependencies on module import.  The
``__all__`` definition allows ``from utils import <mod>`` style imports without
side effects.
"""

__all__ = [
    "history_utils",
    "invoice_utils",
    "json_utils",
    "ocr_utils",
    "preview_utils",
    "receipt_parser",
]
