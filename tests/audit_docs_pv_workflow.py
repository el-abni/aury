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
    readme = read("README.md")
    readme_n = normalize(readme)
    ensure("docs/architecture.md" in readme_n, "README.md precisa apontar para docs/ARCHITECTURE.md")
    ensure("docs/compatibility.md" in readme_n, "README.md precisa apontar para docs/COMPATIBILITY.md")
    ensure("docs/workflow.md" in readme_n, "README.md precisa apontar para docs/WORKFLOW.md")
    ensure("tests/readme.md" in readme_n, "README.md precisa apontar para tests/README.md")
    ensure("python/aury/fish_bridge.py" in readme, "README.md precisa citar python/aury/fish_bridge.py")
    ensure("python/aury/cli.py" in readme, "README.md precisa citar python/aury/cli.py")
    ensure("release_gate_minimo.sh" in readme, "README.md precisa citar release_gate_minimo.sh")
    ensure("worktree_gate_minimo.sh" in readme, "README.md precisa citar worktree_gate_minimo.sh")
    ensure("ordem de leitura" in readme_n, "README.md precisa explicitar a ordem de leitura pública")
    ensure("documentacao" in readme_n, "README.md precisa manter a indexação pública de documentação")
    ensure("contrato" in readme_n and "workflow" in readme_n and "arquitetura" in readme_n, "README.md precisa distinguir os papéis de contrato, workflow e arquitetura")

    workflow = read("docs/WORKFLOW.md")
    workflow_n = normalize(workflow)
    ensure("worktree hygiene" in workflow_n, "docs/WORKFLOW.md precisa explicitar worktree hygiene")
    ensure("release hygiene" in workflow_n, "docs/WORKFLOW.md precisa explicitar release hygiene")
    ensure("stage vazia" in workflow_n, "docs/WORKFLOW.md precisa tratar falha por stage vazia")
    ensure("git_index_file" in workflow_n, "docs/WORKFLOW.md precisa citar GIT_INDEX_FILE")
    ensure("nao inspeciona a stage publica" in workflow_n, "docs/WORKFLOW.md precisa explicitar que o preflight não inspeciona a stage pública")

    tests_readme = read("tests/README.md")
    tests_readme_n = normalize(tests_readme)
    ensure("docs/workflow.md" in tests_readme_n, "tests/README.md precisa apontar para docs/WORKFLOW.md como leitura primária da ladder")
    ensure("worktree hygiene" in tests_readme_n, "tests/README.md precisa explicitar worktree hygiene")
    ensure("release hygiene" in tests_readme_n, "tests/README.md precisa explicitar release hygiene")
    ensure("audit_docs_pv_workflow.py" in tests_readme, "tests/README.md precisa listar audit_docs_pv_workflow.py")
    ensure("audit_gate_ladder.py" in tests_readme, "tests/README.md precisa listar audit_gate_ladder.py")
    ensure("nao inspeciona a stage publica" in tests_readme_n, "tests/README.md precisa explicitar que o preflight não inspeciona a stage pública")

    print("audit_docs_pv_workflow: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
