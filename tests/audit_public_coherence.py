#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SEMVER_RE = re.compile(r"v\d+\.\d+\.\d+")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return " ".join(text.lower().split())


def ensure(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def ensure_any(text: str, options: tuple[str, ...], message: str) -> None:
    if not any(option in text for option in options):
        fail(message)


def concept_hits(text: str, groups: tuple[tuple[str, ...], ...]) -> int:
    return sum(1 for group in groups if any(option in text for option in group))


def run_fish(*args: str) -> str:
    proc = subprocess.run(
        ["fish", "-c", f"source '{ROOT / 'bin' / 'aury.fish'}'; aury $argv", "--", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        fail(f"execução Fish falhou para {' '.join(args)!r}: {proc.stderr or proc.stdout}")
    return proc.stdout


def assert_no_runtime_hardcode(path: str) -> None:
    text = read(path)
    if CURRENT_VERSION in text or SEMVER_RE.search(text):
        fail(f"{path} ainda contém hardcode de versão no runtime público")
    ok(f"{path} sem hardcode de versão")


def assert_help_dev_note(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure("aury dev sem frase" in normalized, f"{source} precisa mencionar 'aury dev' sem frase")
    ensure("adaptador fish" in normalized, f"{source} precisa explicitar que a checagem curta continua no adaptador Fish")
    ensure("aury dev <frase>" in normalized, f"{source} precisa apontar para 'aury dev <frase>' como relatório principal")
    ensure_any(
        normalized,
        ("checagem rapida", "verificacao rapida", "verificacao local", "verificacao local curta", "uso rapido"),
        f"{source} precisa tratar 'aury dev' sem frase como checagem curta, sem exigir frase exata",
    )
    ensure_any(
        normalized,
        ("uso secundario", "utilitario secundario", "secundaria do adaptador fish", "secundario nesta linha"),
        f"{source} precisa enquadrar 'aury dev' sem frase como uso secundário da linha 1.x",
    )
    ensure_any(
        normalized,
        ("relatorio canonico", "relatorio principal"),
        f"{source} precisa preservar que o relatório canônico segue em 'aury dev <frase>'",
    )
    ensure("provisorio" not in normalized, f"{source} não deve mais tratar 'aury dev' sem frase como provisório")


def assert_package_contract_note(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure("pacote do host" in normalized, f"{source} precisa explicitar o pacote do host como contrato público")
    ensure("flatpak" in normalized and "rpm-ostree" in normalized, f"{source} precisa enquadrar flatpak e rpm-ostree de forma explícita")
    ensure_any(
        normalized,
        ("software do usuario", "app store", "multiplas rotas", "politica de origem"),
        f"{source} precisa bloquear inferência de software do usuário, app store, múltiplas rotas ou política de origem",
    )


def assert_final_matrix_note(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure("suportado agora" in normalized, f"{source} precisa explicitar o bloco suportado agora")
    ensure("suportado contido" in normalized, f"{source} precisa explicitar o bloco suportado contido")
    ensure("bloqueado por politica" in normalized, f"{source} precisa explicitar o bloco bloqueado por política")
    ensure_any(
        normalized,
        ("fora do contrato ativo", "observadas fora do contrato ativo"),
        f"{source} precisa enquadrar ferramentas observadas fora do contrato ativo",
    )


def assert_aurora_handoff_note(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure("aurora" in normalized, f"{source} precisa mencionar a Aurora no handoff final")
    ensure_any(
        normalized,
        ("software do usuario", "multiplas origens", "politica de origem", "source/trust", "hosts imutaveis"),
        f"{source} precisa registrar o escopo que já pertence à Aurora",
    )
    ensure_any(
        normalized,
        ("pertencem a aurora", "pertence a aurora", "nao a aury 1.x", "handoff"),
        f"{source} precisa deixar o handoff para a Aurora explícito",
    )


def assert_line_closure_note(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure_any(
        normalized,
        (
            "linha 1.x encerrada",
            "encerra canonicamente",
            "encerramento canonico",
            "compatibilidade linux da aury 1.x se encerra",
            "fechamento canonico",
        ),
        f"{source} precisa tratar a linha 1.x como encerrada canonicamente",
    )


def assert_readme_state(readme: str) -> None:
    normalized = normalize(readme)
    ensure(CURRENT_VERSION in readme, "README.md precisa citar a versão pública atual")
    ensure("linha 1.6" in normalized, "README.md precisa manter a linha 1.6.x como referência já entregue")
    ensure_any(
        normalized,
        ("fechada", "encerrada"),
        "README.md precisa tratar a linha 1.6.x como fechada/encerrada",
    )
    state_section = readme.partition(f"## Estado público da {CURRENT_VERSION}")[2].partition("## Roadmap")[0]
    ensure(state_section.strip(), f"README.md precisa manter a seção pública do estado da {CURRENT_VERSION}")
    scope_hits = concept_hits(
        normalize(state_section),
        (
            ("abertura operacional", "fechamento estrutural", "superficie publica"),
            ("compactacao local simples", ".zip", ".tar.gz"),
            ("fronteira fish/python", "fronteira hibrida", "adaptador fish", "nucleo python"),
            ("workflow canonico", "auditoria publica", "auditoria minima"),
        ),
    )
    ensure(scope_hits >= 2, f"README.md precisa manter o estado da {CURRENT_VERSION} descrito por conceitos centrais, sem depender de uma frase única")
    assert_package_contract_note(readme, "README.md")
    assert_final_matrix_note(readme, "README.md")
    assert_aurora_handoff_note(readme, "README.md")
    assert_line_closure_note(readme, "README.md")


def assert_architecture_state(architecture: str) -> None:
    normalized = normalize(architecture)
    ensure(CURRENT_VERSION in architecture, "docs/ARCHITECTURE.md precisa citar a versão pública atual")
    ensure("adaptador fish" in normalized, "docs/ARCHITECTURE.md precisa manter o papel público do adaptador Fish")
    ensure("runtime python" in normalized, "docs/ARCHITECTURE.md precisa explicitar o runtime Python atual")
    ensure("criar arquivo" in normalized, "docs/ARCHITECTURE.md precisa registrar a micro-migração de criar arquivo")
    ensure("criar pasta" in normalized, "docs/ARCHITECTURE.md precisa registrar a micro-migração de criar pasta")
    ensure_any(
        normalized,
        ("hibrida", "fronteira fish/python", "camada de compatibilidade"),
        "docs/ARCHITECTURE.md precisa preservar a honestidade da fronteira híbrida",
    )
    assert_package_contract_note(architecture, "docs/ARCHITECTURE.md")
    assert_final_matrix_note(architecture, "docs/ARCHITECTURE.md")
    assert_aurora_handoff_note(architecture, "docs/ARCHITECTURE.md")
    assert_line_closure_note(architecture, "docs/ARCHITECTURE.md")


def assert_tests_readme_state(text: str) -> None:
    normalized = normalize(text)
    ensure("gate final canonico" in normalized, "tests/README.md precisa explicitar o gate final canônico")
    ensure("release_gate_minimo.sh" in text, "tests/README.md precisa apontar para release_gate_minimo.sh")
    assert_final_matrix_note(text, "tests/README.md")
    assert_aurora_handoff_note(text, "tests/README.md")
    assert_line_closure_note(text, "tests/README.md")


def assert_changelog_state(changelog: str) -> None:
    ensure(f"## {CURRENT_VERSION}" in changelog, "CHANGELOG.md precisa expor a versão pública atual")
    current_section = changelog.partition(f"## {CURRENT_VERSION}")[2].partition("\n## ")[0]
    ensure(current_section.strip(), "CHANGELOG.md precisa manter a seção pública da versão atual")
    assert_final_matrix_note(current_section, "CHANGELOG.md")
    assert_aurora_handoff_note(current_section, "CHANGELOG.md")
    assert_line_closure_note(current_section, "CHANGELOG.md")


def assert_dev_output(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure("adaptador fish" in normalized, f"{source} precisa declarar o escopo estreito do adaptador Fish")
    ensure_any(
        normalized,
        ("checagem rapida", "verificacao rapida", "verificacao local", "verificacao local curta", "sintaxe"),
        f"{source} precisa deixar claro que sem frase o recorte é curto",
    )
    ensure_any(
        normalized,
        ("uso secundario", "utilitario secundario", "secundario nesta linha"),
        f"{source} precisa enquadrar 'aury dev' sem frase como uso secundário",
    )
    ensure_any(
        normalized,
        ("aury dev <frase>", "uma frase"),
        f"{source} precisa direcionar o relatório canônico para uma frase explícita",
    )
    ensure("relatorio" in normalized and "canonico" in normalized, f"{source} precisa preservar a ideia de relatório canônico")
    ensure("provisorio" not in normalized, f"{source} não deve mais tratar 'aury dev' sem frase como provisório")


def main() -> int:
    ensure(CURRENT_VERSION.startswith("v1."), "VERSION vazia ou inválida")
    ok("VERSION preenchida")

    help_text = read("resources/help.txt")
    ensure("{version}" in help_text, "resources/help.txt precisa manter o placeholder {version}")
    assert_help_dev_note(help_text, "resources/help.txt")
    assert_package_contract_note(help_text, "resources/help.txt")
    assert_final_matrix_note(help_text, "resources/help.txt")
    assert_aurora_handoff_note(help_text, "resources/help.txt")
    assert_line_closure_note(help_text, "resources/help.txt")
    ok("help público mantém placeholder e nota honesta sobre aury dev")

    readme = read("README.md")
    assert_readme_state(readme)
    ok(f"README.md alinhado à versão atual e ao fechamento público de {CURRENT_VERSION}")

    changelog = read("CHANGELOG.md")
    assert_changelog_state(changelog)
    ok("CHANGELOG.md alinhado à versão pública atual")

    architecture = read("docs/ARCHITECTURE.md")
    assert_architecture_state(architecture)
    ok("docs/ARCHITECTURE.md alinhado ao estado público atual")

    tests_readme = read("tests/README.md")
    assert_tests_readme_state(tests_readme)
    ok("tests/README.md alinhado ao fechamento canônico da linha 1.x")

    for runtime_file in ("bin/aury.fish", "python/aury/resources.py", "install.sh", "uninstall.sh"):
        assert_no_runtime_hardcode(runtime_file)

    help_output = run_fish("ajuda")
    ensure(f"💜 Aury {CURRENT_VERSION}" in help_output, "aury ajuda precisa renderizar a versão ativa")
    assert_help_dev_note(help_output, "aury ajuda")
    assert_package_contract_note(help_output, "aury ajuda")
    assert_final_matrix_note(help_output, "aury ajuda")
    assert_aurora_handoff_note(help_output, "aury ajuda")
    assert_line_closure_note(help_output, "aury ajuda")
    ok("ajuda renderizada pela entrada pública Fish")

    version_output = run_fish("--version")
    ensure(version_output.strip() == f"💜 Aury {CURRENT_VERSION}", "aury --version precisa refletir VERSION exatamente")
    ok("version renderizada pela entrada pública Fish")

    dev_output = run_fish("dev")
    assert_dev_output(dev_output, "aury dev")
    ok("aury dev sem frase com UX honesta")

    print("audit_public_coherence: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
