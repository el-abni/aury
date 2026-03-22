from __future__ import annotations

import os
from pathlib import Path


def share_root() -> Path:
    override = os.environ.get("AURY_SHARE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def read_version() -> str:
    version = (share_root() / "VERSION").read_text(encoding="utf-8").strip()
    return version or "v1.6.3"


def render_help() -> str:
    template = (share_root() / "resources" / "help.txt").read_text(encoding="utf-8")
    return template.replace("{version}", read_version())
