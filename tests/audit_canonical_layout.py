#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from aury import core_api
from aury.resources import share_root


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


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
    ensure((ROOT / ".git").is_dir(), "a raiz viva precisa continuar sendo um checkout Git de topo")
    ensure((ROOT / "python" / "aury" / "core_api.py").is_file(), "a superfície canônica core_api.py precisa existir na raiz viva")
    ensure(share_root() == ROOT, "o runtime Python precisa resolver a base ativa para a raiz viva")
    ensure(Path(core_api.__file__).resolve() == ROOT / "python" / "aury" / "core_api.py", "core_api precisa vir da árvore canônica")
    ok("raiz Python canônica preservada")

    fish_proc = subprocess.run(
        ["fish", "-c", f"source '{ROOT / 'bin' / 'aury.fish'}'; __aury_share_root"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    ensure(fish_proc.returncode == 0, "não consegui resolver a base ativa do adaptador Fish")
    ensure(Path(fish_proc.stdout.strip()).resolve() == ROOT, "o adaptador Fish precisa resolver a raiz viva do checkout atual")
    ok("raiz Fish canônica preservada")

    gitignore_text = read(".gitignore")
    ensure("/aury/" in gitignore_text, ".gitignore precisa isolar o artefato aninhado da raiz viva")
    ignored = subprocess.run(["git", "check-ignore", "-q", "aury"], cwd=ROOT, check=False)
    ensure(ignored.returncode == 0, "o root Git precisa ignorar ./aury/ como artefato aninhado")
    ok("artefato aninhado isolado do root Git")

    workflow_text = read("docs/WORKFLOW.md")
    workflow_normalized = normalize(workflow_text)
    ensure("raiz canonica" in workflow_normalized, "docs/WORKFLOW.md precisa explicitar a raiz canônica")
    ensure("./aury/" in workflow_text and "artefato historico" in workflow_normalized, "docs/WORKFLOW.md precisa classificar ./aury/ como artefato histórico")
    ensure("preflight_canonico.sh" in workflow_text, "docs/WORKFLOW.md precisa citar o preflight")
    ensure("worktree_gate_minimo.sh" in workflow_text, "docs/WORKFLOW.md precisa citar o gate de worktree")
    ensure("release_gate_minimo.sh" in workflow_text, "docs/WORKFLOW.md precisa citar o gate final")
    ensure("stage" in workflow_normalized and "worktree" in workflow_normalized, "docs/WORKFLOW.md precisa separar worktree e stage pública")
    ok("workflow público mínimo canonizado")

    compatibility_text = read("docs/COMPATIBILITY.md")
    compatibility_normalized = normalize(compatibility_text)
    ensure("pacote do host" in compatibility_normalized, "docs/COMPATIBILITY.md precisa preservar o contrato de pacote do host")
    ensure("suportado agora" in compatibility_normalized, "docs/COMPATIBILITY.md precisa preservar o suporte agora")
    ensure("suportado contido" in compatibility_normalized, "docs/COMPATIBILITY.md precisa preservar o suporte contido")
    ensure("bloqueado por politica" in compatibility_normalized, "docs/COMPATIBILITY.md precisa preservar o bloqueio por política")
    ensure("aurora" in compatibility_normalized and "multiplas origens" in compatibility_normalized, "docs/COMPATIBILITY.md precisa preservar o handoff para a Aurora")
    ok("compatibilidade pública mínima canonizada")

    architecture_text = read("docs/ARCHITECTURE.md")
    architecture_normalized = normalize(architecture_text)
    ensure("raiz canonica" in architecture_normalized, "docs/ARCHITECTURE.md precisa registrar a raiz canônica")
    ensure("adaptador fish" in architecture_normalized, "docs/ARCHITECTURE.md precisa preservar o papel do adaptador Fish")
    ensure("runtime python" in architecture_normalized, "docs/ARCHITECTURE.md precisa preservar o papel do runtime Python")
    ensure("ownership fish / python" in architecture_normalized, "docs/ARCHITECTURE.md precisa explicitar o ownership Fish / Python")
    ensure("hotspot hibrido" in architecture_normalized, "docs/ARCHITECTURE.md precisa explicitar o hotspot híbrido")
    ensure("bin/aury.fish" in architecture_text, "docs/ARCHITECTURE.md precisa citar bin/aury.fish")
    ensure("python/aury/runtime.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/runtime.py")
    ensure("python/aury/host.py" in architecture_text, "docs/ARCHITECTURE.md precisa citar python/aury/host.py")
    ok("ownership arquitetural mínimo canonizado")

    nested_git_dir = ROOT / "aury" / ".git"
    if nested_git_dir.exists():
        ensure(not (ROOT / "aury" / "python" / "aury" / "core_api.py").exists(), "o artefato aninhado não pode carregar a superfície core_api canônica")
        ok("artefato aninhado permanece distinguível da raiz viva")

    print("audit_canonical_layout: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
