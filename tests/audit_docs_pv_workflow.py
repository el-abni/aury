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

    pv = read(".aury-private/arquivo/contexto/PV_VIVO_E_HISTORICO.md")
    pv_n = normalize(pv)
    ensure("arquivo/contexto/README.md".lower() in pv.lower(), "PV_VIVO_E_HISTORICO.md precisa apontar para arquivo/contexto/README.md")
    ensure("curadoria" in pv_n and "handoff" in pv_n, "PV_VIVO_E_HISTORICO.md precisa classificar curadoria/handoff")
    ensure("temporario" in pv_n and "local" in pv_n, "PV_VIVO_E_HISTORICO.md precisa classificar material temporário/local")
    ensure("2026-04-19_09_IMPLEMENTACAO_ONDA_0_CANONIZACAO_AURY.md" in pv, "PV_VIVO_E_HISTORICO.md precisa manter o relatório da Onda 0 como registro vivo")
    ensure("2026-04-19_10_IMPLEMENTACAO_ONDA_1_ORGANIZACAO_ESTRUTURAL_AURY.md" in pv, "PV_VIVO_E_HISTORICO.md precisa manter o relatório da Onda 1 como registro vivo")

    context_readme = read(".aury-private/arquivo/contexto/README.md")
    context_readme_n = normalize(context_readme)
    ensure("pv_vivo_e_historico.md" in context_readme_n, "arquivo/contexto/README.md precisa apontar para PV_VIVO_E_HISTORICO.md")
    ensure("workflow_canonico_release_aury.md" in context_readme_n, "arquivo/contexto/README.md precisa apontar para WORKFLOW_CANONICO_RELEASE_AURY.md")
    ensure("ordem de leitura" in context_readme_n, "arquivo/contexto/README.md precisa explicitar a ordem de leitura")

    brainstorms_readme = read(".aury-private/arquivo/brainstorms/README.md")
    brainstorms_readme_n = normalize(brainstorms_readme)
    ensure("patrimonio historico" in brainstorms_readme_n, "arquivo/brainstorms/README.md precisa manter brainstorm como patrimônio histórico")
    ensure("excecao" in brainstorms_readme_n or "elevad" in brainstorms_readme_n, "arquivo/brainstorms/README.md precisa explicitar a exceção dos relatórios promovidos")

    workflow_private = read(".aury-private/arquivo/contexto/WORKFLOW_CANONICO_RELEASE_AURY.md")
    workflow_private_n = normalize(workflow_private)
    ensure("docs/workflow.md" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa citar docs/WORKFLOW.md")
    ensure("checklist_release_segura_aury.md" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa citar CHECKLIST_RELEASE_SEGURA_AURY.md")
    ensure("fluxo_fechamento_de_versao_aury.md" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa citar FLUXO_FECHAMENTO_DE_VERSAO_AURY.md")
    ensure("worktree hygiene" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa explicitar worktree hygiene")
    ensure("release hygiene" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa explicitar release hygiene")
    ensure("git_index_file" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa registrar o uso de GIT_INDEX_FILE")
    ensure("tests/_gate_common.sh" in workflow_private, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa refletir o helper comum dos gates")
    ensure("tests/audit_gate_ladder.py" in workflow_private, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa refletir o guardrail da ladder")
    ensure('git commit -m "Aury vX.Y.Z"' in workflow_private, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa congelar o commit curto de release")
    ensure('git tag -a vX.Y.Z -m "💜 vX.Y.Z"' in workflow_private, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa congelar o título curto de tag/release")
    ensure("titulo curto" in workflow_private_n and "💜 vx.y.z" in workflow_private_n, "WORKFLOW_CANONICO_RELEASE_AURY.md precisa registrar o título curto de release")

    checklist = read(".aury-private/estrategia/CHECKLIST_RELEASE_SEGURA_AURY.md")
    checklist_n = normalize(checklist)
    ensure("workflow_canonico_release_aury.md" in checklist_n, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa citar WORKFLOW_CANONICO_RELEASE_AURY.md")
    ensure("fluxo_fechamento_de_versao_aury.md" in checklist_n, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa citar FLUXO_FECHAMENTO_DE_VERSAO_AURY.md")
    ensure("release hygiene" in checklist_n, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa explicitar release hygiene")
    ensure("git_index_file" in checklist_n, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa registrar o uso de GIT_INDEX_FILE")
    ensure("tests/_gate_common.sh" in checklist, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa refletir o helper comum dos gates")
    ensure("tests/audit_gate_ladder.py" in checklist, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa refletir o guardrail da ladder")
    ensure('git commit -m "Aury vX.Y.Z"' in checklist, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa congelar o commit curto de release")
    ensure("💜 vX.Y.Z" in checklist, "CHECKLIST_RELEASE_SEGURA_AURY.md precisa registrar o título curto de release")

    short_flow = read(".aury-private/estrategia/FLUXO_FECHAMENTO_DE_VERSAO_AURY.md")
    short_flow_n = normalize(short_flow)
    ensure("workflow_canonico_release_aury.md" in short_flow_n, "FLUXO_FECHAMENTO_DE_VERSAO_AURY.md precisa deferir para WORKFLOW_CANONICO_RELEASE_AURY.md")
    ensure("checklist_release_segura_aury.md" in short_flow_n, "FLUXO_FECHAMENTO_DE_VERSAO_AURY.md precisa deferir para CHECKLIST_RELEASE_SEGURA_AURY.md")
    ensure("espelho estrategico" in short_flow_n or "versao curta" in short_flow_n, "FLUXO_FECHAMENTO_DE_VERSAO_AURY.md precisa se classificar como versão curta/espelho estratégico")
    ensure("git_index_file" in short_flow_n, "FLUXO_FECHAMENTO_DE_VERSAO_AURY.md precisa registrar o uso de GIT_INDEX_FILE")
    ensure("aury vx.y.z" in short_flow_n and "💜 vx.y.z" in short_flow_n, "FLUXO_FECHAMENTO_DE_VERSAO_AURY.md precisa registrar o shape curto de commit/release")

    print("audit_docs_pv_workflow: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
