from __future__ import annotations

"""Compatibility shim for historical imports.

The live Python-side bridge consumed by ``bin/aury.fish`` now lives in
``python/aury/fish_bridge.py``. Keep ``cli.py`` as a thin import-only shim so
older references do not look canonic again by accident.
"""

from .fish_bridge import HELP_TOKENS, VERSION_TOKENS, main

__all__ = ["HELP_TOKENS", "VERSION_TOKENS", "main"]
