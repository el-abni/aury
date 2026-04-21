#!/usr/bin/env python3
from __future__ import annotations

import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    helper = read("tests/_gate_common.sh")
    ensure("gate_require_commands()" in helper, "tests/_gate_common.sh precisa concentrar a checagem mínima de dependências dos gates")
    ensure("gate_assert_clean_worktree_diff()" in helper, "tests/_gate_common.sh precisa concentrar a hygiene textual da worktree")
    ensure("gate_require_public_stage()" in helper, "tests/_gate_common.sh precisa concentrar a exigência de stage pública explícita")
    ensure("gate_assert_public_stage_scope()" in helper, "tests/_gate_common.sh precisa concentrar o recorte público permitido da stage")
    ensure("gate_assert_clean_staged_diff()" in helper, "tests/_gate_common.sh precisa concentrar a hygiene textual da stage")
    ensure("git diff --check" in helper, "tests/_gate_common.sh precisa manter a checagem textual da worktree")
    ensure("git diff --cached --check" in helper, "tests/_gate_common.sh precisa manter a checagem textual da stage")
    ok("helper comum dos gates preservado")

    preflight = read("tests/preflight_canonico.sh")
    ensure('source "$ROOT/tests/_gate_common.sh"' in preflight, "tests/preflight_canonico.sh precisa usar o helper comum dos gates")
    ensure("gate_require_commands fish python3" in preflight, "tests/preflight_canonico.sh precisa declarar dependências sem puxar semântica de Git/stage")
    for audit_path in (
        "audit_canonical_layout.py",
        "audit_hybrid_boundary.py",
        "audit_public_coherence.py",
        "audit_docs_pv_workflow.py",
        "audit_gate_ladder.py",
        "audit_dev_parity.py",
    ):
        ensure(
            f'"$ROOT/tests/{audit_path}"' in preflight,
            f"tests/preflight_canonico.sh precisa manter {audit_path} no degrau curto da ladder",
        )
    ensure('bash "$ROOT/tests/public_ux_smoke.sh"' in preflight, "tests/preflight_canonico.sh precisa manter o smoke público mínimo")
    ensure('python3 "$ROOT/tests/python_core_smoke.py"' in preflight, "tests/preflight_canonico.sh precisa manter o smoke do núcleo Python")
    ensure("git diff --check" not in preflight and "git diff --cached" not in preflight, "tests/preflight_canonico.sh não pode disputar semântica de worktree/release hygiene")
    ensure("audit_exit_surfaces.py" not in preflight, "tests/preflight_canonico.sh não deve absorver o auditor de superfícies de saída do gate de worktree")
    ensure("tests.test_canonical_core_surface" not in preflight, "tests/preflight_canonico.sh não deve absorver os unittests canônicos do core_api")
    ensure("tests.test_core_api_characterization" not in preflight, "tests/preflight_canonico.sh não deve absorver os unittests canônicos do core_api")
    ok("preflight preserva o degrau curto da ladder")

    worktree_gate = read("tests/worktree_gate_minimo.sh")
    ensure('source "$ROOT/tests/_gate_common.sh"' in worktree_gate, "tests/worktree_gate_minimo.sh precisa usar o helper comum dos gates")
    ensure("gate_require_commands git fish python3" in worktree_gate, "tests/worktree_gate_minimo.sh precisa declarar o toolchain canônico do gate de worktree")
    ensure("gate_assert_clean_worktree_diff" in worktree_gate, "tests/worktree_gate_minimo.sh precisa continuar fechando a hygiene textual da worktree")
    ensure('bash "$ROOT/tests/preflight_canonico.sh"' in worktree_gate, "tests/worktree_gate_minimo.sh precisa compor o preflight canônico")
    ensure('python3 "$ROOT/tests/audit_exit_surfaces.py"' in worktree_gate, "tests/worktree_gate_minimo.sh precisa compor o auditor de superfícies de saída")
    ensure(
        "python3 -m unittest tests.test_canonical_core_surface tests.test_core_api_characterization" in worktree_gate,
        "tests/worktree_gate_minimo.sh precisa compor os unittests canônicos do core_api",
    )
    ensure("git diff --cached" not in worktree_gate, "tests/worktree_gate_minimo.sh não pode puxar semântica stage-based")
    ok("gate de worktree preserva sua composição própria")

    release_gate = read("tests/release_gate_minimo.sh")
    ensure('source "$ROOT/tests/_gate_common.sh"' in release_gate, "tests/release_gate_minimo.sh precisa usar o helper comum dos gates")
    ensure("gate_require_commands git fish python3" in release_gate, "tests/release_gate_minimo.sh precisa declarar o toolchain canônico do gate final")
    ensure('staged="$(gate_require_public_stage)"' in release_gate, "tests/release_gate_minimo.sh precisa continuar exigindo stage pública explícita")
    ensure('gate_assert_public_stage_scope "$staged"' in release_gate, "tests/release_gate_minimo.sh precisa continuar protegendo o recorte público da stage")
    ensure("gate_assert_clean_staged_diff" in release_gate, "tests/release_gate_minimo.sh precisa continuar protegendo a hygiene textual da stage")
    ensure('bash "$ROOT/tests/worktree_gate_minimo.sh"' in release_gate, "tests/release_gate_minimo.sh precisa compor o gate de worktree já aprovado")
    ensure("audit_exit_surfaces.py" not in release_gate, "tests/release_gate_minimo.sh não deve duplicar checks já compostos pelo gate de worktree")
    ensure("tests.test_canonical_core_surface" not in release_gate, "tests/release_gate_minimo.sh não deve duplicar os unittests canônicos do core_api")
    ensure("tests.test_core_api_characterization" not in release_gate, "tests/release_gate_minimo.sh não deve duplicar os unittests canônicos do core_api")
    ok("gate final preserva a semântica stage-based por composição")

    workflow = normalize(read("docs/WORKFLOW.md"))
    ensure("nao inspeciona a stage publica" in workflow, "docs/WORKFLOW.md precisa explicitar que o preflight não inspeciona a stage pública")
    ensure("worktree hygiene" in workflow and "release hygiene" in workflow, "docs/WORKFLOW.md precisa manter a separação entre worktree hygiene e release hygiene")
    ok("workflow público preserva a leitura da ladder")

    tests_readme = normalize(read("tests/README.md"))
    ensure("audit_gate_ladder.py" in read("tests/README.md"), "tests/README.md precisa listar audit_gate_ladder.py")
    ensure("nao inspeciona a stage publica" in tests_readme, "tests/README.md precisa explicitar que o preflight não inspeciona a stage pública")
    ensure("gate de worktree ja composto" in tests_readme, "tests/README.md precisa registrar que o gate final compõe o gate de worktree")
    ok("README de testes preserva a leitura executável da ladder")

    print("audit_gate_ladder: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
