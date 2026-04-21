from __future__ import annotations

import os
from pathlib import Path

from .public_voice import failure, info

_FALLBACK_VERSION = "versão-indisponível"
_FALLBACK_HELP = """💜 Aury {version}

{missing}
{hint}
"""


def _is_live_share_root(path: Path) -> bool:
    return (
        (path / "VERSION").is_file()
        and (path / "resources" / "help.txt").is_file()
        and (path / "python" / "aury" / "core_api.py").is_file()
    )


def share_root() -> Path:
    override = os.environ.get("AURY_SHARE_DIR")
    if override:
        candidate = Path(override).expanduser().resolve()
        if _is_live_share_root(candidate):
            return candidate

    module_root = Path(__file__).resolve().parents[2]
    if _is_live_share_root(module_root):
        return module_root

    installed_root = Path.home().expanduser() / ".local" / "share" / "aury"
    if _is_live_share_root(installed_root):
        return installed_root.resolve()

    return module_root


def read_version() -> str:
    version_file = share_root() / "VERSION"
    if not version_file.is_file():
        return _FALLBACK_VERSION
    version = version_file.read_text(encoding="utf-8").strip()
    return version or _FALLBACK_VERSION


def render_help() -> str:
    help_file = share_root() / "resources" / "help.txt"
    if not help_file.is_file():
        return _FALLBACK_HELP.format(
            version=read_version(),
            missing=failure("Não encontrei resources/help.txt na base ativa."),
            hint=info("Use a Aury a partir de uma instalação íntegra ou do checkout canônico."),
        )
    template = help_file.read_text(encoding="utf-8")
    return template.replace("{version}", read_version())
