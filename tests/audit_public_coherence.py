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
        ("checagem rapida", "verificacao rapida", "uso rapido"),
        f"{source} precisa tratar 'aury dev' sem frase como checagem curta, sem exigir frase exata",
    )
    ensure_any(
        normalized,
        ("relatorio canonico", "relatorio principal"),
        f"{source} precisa preservar que o relatório canônico segue em 'aury dev <frase>'",
    )


def assert_readme_opening(readme: str) -> None:
    normalized = normalize(readme)
    ensure(CURRENT_VERSION in readme, "README.md precisa citar a versão pública atual")
    ensure("linha 1.6" in normalized, "README.md precisa manter a linha 1.6.x como referência já entregue")
    ensure_any(
        normalized,
        ("fechada", "encerrada"),
        "README.md precisa tratar a linha 1.6.x como fechada/encerrada",
    )
    v17_section = readme.partition("### v1.7")[2].partition("### v1.8")[0]
    ensure(v17_section.strip(), "README.md precisa manter a seção pública da abertura da v1.7")
    scope_hits = concept_hits(
        normalize(v17_section),
        (
            ("coerencia publica", "higiene publica", "superficie publica"),
            ("workflow canonico", "fluxo canonico"),
            ("fronteira fish/python", "fronteira hibrida fish/python", "fish/python"),
            ("tooling minimo", "auditoria minima", "tooling inicial"),
        ),
    )
    ensure(scope_hits >= 2, "README.md precisa manter a abertura da v1.7 descrita por conceitos centrais, sem depender de uma frase única")


def assert_dev_output(text: str, source: str) -> None:
    normalized = normalize(text)
    ensure("adaptador fish" in normalized, f"{source} precisa declarar o escopo estreito do adaptador Fish")
    ensure_any(
        normalized,
        ("checagem rapida", "verificacao rapida", "sintaxe"),
        f"{source} precisa deixar claro que sem frase o recorte é curto",
    )
    ensure_any(
        normalized,
        ("aury dev <frase>", "uma frase"),
        f"{source} precisa direcionar o relatório canônico para uma frase explícita",
    )
    ensure("relatorio" in normalized and "canonico" in normalized, f"{source} precisa preservar a ideia de relatório canônico")


def main() -> int:
    ensure(CURRENT_VERSION.startswith("v1."), "VERSION vazia ou inválida")
    ok("VERSION preenchida")

    help_text = read("resources/help.txt")
    ensure("{version}" in help_text, "resources/help.txt precisa manter o placeholder {version}")
    assert_help_dev_note(help_text, "resources/help.txt")
    ok("help público mantém placeholder e nota honesta sobre aury dev")

    readme = read("README.md")
    assert_readme_opening(readme)
    ok("README.md alinhado à versão atual e à abertura operacional contida da v1.7")

    changelog = read("CHANGELOG.md")
    ensure(f"## {CURRENT_VERSION}" in changelog, "CHANGELOG.md precisa expor a versão pública atual")
    ok("CHANGELOG.md alinhado à versão pública atual")

    for runtime_file in ("bin/aury.fish", "python/aury/resources.py", "install.sh", "uninstall.sh"):
        assert_no_runtime_hardcode(runtime_file)

    help_output = run_fish("ajuda")
    ensure(f"💜 Aury {CURRENT_VERSION}" in help_output, "aury ajuda precisa renderizar a versão ativa")
    assert_help_dev_note(help_output, "aury ajuda")
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
