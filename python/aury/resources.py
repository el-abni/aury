from __future__ import annotations

import os
from pathlib import Path

_FALLBACK_VERSION = "versão-indisponível"
_FALLBACK_HELP = """💜 Aury {version}

❌ não encontrei resources/help.txt na base ativa.
Use: aury ajuda a partir de uma instalação íntegra ou do checkout canônico.
"""


def share_root() -> Path:
    override = os.environ.get("AURY_SHARE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def read_version() -> str:
    version_file = share_root() / "VERSION"
    if not version_file.is_file():
        return _FALLBACK_VERSION
    version = version_file.read_text(encoding="utf-8").strip()
    return version or _FALLBACK_VERSION


def render_help() -> str:
    help_file = share_root() / "resources" / "help.txt"
    if not help_file.is_file():
        return _FALLBACK_HELP.format(version=read_version())
    template = help_file.read_text(encoding="utf-8")
    return template.replace("{version}", read_version())
