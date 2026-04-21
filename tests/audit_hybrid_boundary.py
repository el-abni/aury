#!/usr/bin/env python3
from __future__ import annotations

import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return " ".join(text.lower().split())


def main() -> int:
    fish_bridge_text = read("python/aury/fish_bridge.py")
    ensure("def main(" in fish_bridge_text, "python/aury/fish_bridge.py precisa expor o entrypoint Python da fronteira Fish")
    ensure("render_dev_report" in fish_bridge_text, "python/aury/fish_bridge.py precisa continuar roteando 'dev'")
    ensure("execute(" in fish_bridge_text, "python/aury/fish_bridge.py precisa continuar delegando a execução normal ao runtime")

    cli_text = read("python/aury/cli.py")
    cli_normalized = normalize(cli_text)
    ensure("from .fish_bridge import help_tokens, version_tokens, main" in cli_normalized, "python/aury/cli.py precisa delegar para python/aury/fish_bridge.py")
    ensure("compatibility shim" in cli_normalized, "python/aury/cli.py precisa se declarar shim de compatibilidade")

    main_text = read("python/aury/__main__.py")
    ensure("from .fish_bridge import main" in main_text, "python/aury/__main__.py precisa apontar para o bridge Python vivo")

    fish_text = read("bin/aury.fish")
    ensure("__aury_fish_bridge_invoke" in fish_text, "bin/aury.fish precisa nomear explicitamente a chamada da fronteira híbrida")
    ensure("__aury_fish_bridge_show_shared_help" in fish_text, "bin/aury.fish precisa nomear explicitamente o fallback de ajuda da fronteira híbrida")
    ensure("__aury_fish_bridge_show_shared_version" in fish_text, "bin/aury.fish precisa nomear explicitamente o fallback de versão da fronteira híbrida")
    ensure("__aury_fish_bridge_invoke $intent sistema" in fish_text, "bin/aury.fish precisa consultar o bridge Python antes do guard local de manutenção do host")

    architecture_text = read("docs/ARCHITECTURE.md")
    architecture_normalized = normalize(architecture_text)
    ensure("python/aury/fish_bridge.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/fish_bridge.py")
    ensure("python/aury/cli.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/cli.py")
    ensure("shim" in architecture_normalized and "compat" in architecture_normalized, "docs/ARCHITECTURE.md precisa classificar python/aury/cli.py como shim de compatibilidade")
    ensure("python/aury/runtime.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/runtime.py")
    ensure("python/aury/host.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/host.py")
    ensure("python/aury/resources.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/resources.py")

    workflow_text = read("docs/WORKFLOW.md")
    workflow_normalized = normalize(workflow_text)
    ensure("python/aury/fish_bridge.py" in workflow_text, "docs/WORKFLOW.md precisa citar python/aury/fish_bridge.py")
    ensure("python/aury/cli.py" in workflow_text, "docs/WORKFLOW.md precisa citar python/aury/cli.py")
    ensure("shim" in workflow_normalized and "compat" in workflow_normalized, "docs/WORKFLOW.md precisa classificar python/aury/cli.py como shim de compatibilidade")

    print("audit_hybrid_boundary: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
