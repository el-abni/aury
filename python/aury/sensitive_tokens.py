from __future__ import annotations

import re

from .contracts import ProtectedToken

_PATH_RE = re.compile(r"^(~/|/|\./|\.\./)")
_PATH_TRAILING_SLASH_RE = re.compile(r".+/$")
_PATH_CONTAINS_SLASH_RE = re.compile(r".+/.+")
_COMPOUND_ARCHIVE_RE = re.compile(r"\.(tar\.gz|tgz|tar\.bz2|tar\.xz)$", re.IGNORECASE)
_FILE_RE = re.compile(r"(^\.[^/]+$|^[^\s/]+\.[A-Za-z0-9][A-Za-z0-9._-]*$)")
_HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*\.[A-Za-z]{2,}$")
_NON_HOST_FILE_EXTENSIONS = {
    "tar.gz",
    "tgz",
    "tar.bz2",
    "tar.xz",
    "zip",
    "7z",
    "tar",
    "gz",
    "bz2",
    "xz",
    "txt",
    "log",
    "md",
    "markdown",
    "fish",
    "sh",
    "bash",
    "zsh",
    "json",
    "yaml",
    "yml",
    "toml",
    "ini",
    "conf",
    "cfg",
    "service",
    "desktop",
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "tsv",
    "xml",
    "html",
    "htm",
    "css",
    "js",
    "ts",
    "jsx",
    "tsx",
    "py",
    "rs",
    "c",
    "cpp",
    "h",
    "hpp",
    "java",
    "kt",
    "swift",
    "go",
    "rb",
    "php",
    "lua",
    "pl",
}


def _is_probably_path(token: str) -> bool:
    return bool(_PATH_RE.match(token) or _PATH_TRAILING_SLASH_RE.match(token) or _PATH_CONTAINS_SLASH_RE.match(token))


def _is_probably_file(token: str) -> bool:
    return bool(_is_probably_path(token) or _COMPOUND_ARCHIVE_RE.search(token) or _FILE_RE.match(token))


def _host_extension(token: str) -> str:
    lower = token.lower()
    for extension in ("tar.gz", "tar.bz2", "tar.xz"):
        if lower.endswith(f".{extension}"):
            return extension
    parts = lower.rsplit(".", 1)
    if len(parts) != 2:
        return ""
    return parts[1]


def _is_probably_host(token: str) -> bool:
    if _is_probably_path(token):
        return False
    if _host_extension(token) in _NON_HOST_FILE_EXTENSIONS:
        return False
    return bool(_HOST_RE.match(token))


def token_sensitive_type(token: str) -> str | None:
    if not token:
        return None
    stripped = token.strip()
    if _is_probably_path(stripped):
        return "path"
    if _is_probably_host(stripped):
        return "host"
    if _is_probably_file(stripped):
        return "file"
    return None


def protect_sensitive_tokens(tokens: list[str]) -> tuple[list[str], list[ProtectedToken]]:
    protected: list[str] = []
    mapping: list[ProtectedToken] = []
    for token in tokens:
        token_type = token_sensitive_type(token)
        if token_type is None:
            protected.append(token)
            continue
        placeholder = f"__AURY_{token_type.upper()}_{len(mapping)+1}__"
        mapping.append(ProtectedToken(placeholder=placeholder, value=token, token_type=token_type))
        protected.append(placeholder)
    return protected, mapping


def restore_sensitive_tokens(tokens: list[str], protected_tokens: list[ProtectedToken]) -> list[str]:
    restored = list(tokens)
    for item in protected_tokens:
        restored = [item.value if token == item.placeholder else token for token in restored]
    return restored
