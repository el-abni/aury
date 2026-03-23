#!/usr/bin/env python3
from __future__ import annotations

import os
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
FISH_BIN = shutil.which("fish") or "fish"
BASH_BIN = shutil.which("bash") or "/usr/bin/bash"
DIRNAME_BIN = shutil.which("dirname") or "/usr/bin/dirname"
PYTHON_ENV = os.environ.copy()
PYTHON_ENV["PYTHONPATH"] = str(ROOT / "python")
PYTHON_ENV["AURY_SHARE_DIR"] = str(ROOT)
STATUS_MARKER = "__AURY_STATUS__:"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK: {message}")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def write_stub(bin_dir: Path, name: str, body: str) -> None:
    path = bin_dir / name
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run_public(args: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> tuple[int, str, str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    quoted_args = " ".join(shlex.quote(arg) for arg in args)
    script = (
        f"source {shlex.quote(str(ROOT / 'bin' / 'aury.fish'))}; "
        f"aury {quoted_args}; "
        f"printf '\\n{STATUS_MARKER}%s\\n' $status"
    )
    proc = subprocess.run(
        [FISH_BIN, "--no-config", "-c", script],
        cwd=cwd or ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout = proc.stdout
    if STATUS_MARKER not in stdout:
        fail(f"não consegui capturar o status público para {args!r}")
    body, _marker, tail = stdout.rpartition(STATUS_MARKER)
    status_line = tail.strip().splitlines()[0]
    try:
        status = int(status_line)
    except ValueError as exc:
        fail(f"status público inválido para {args!r}: {status_line!r} ({exc})")
    return status, body.rstrip(), proc.stderr.strip()


def run_python(args: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = PYTHON_ENV.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", "aury", *args],
        cwd=cwd or ROOT,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    status, output, stderr = run_public(["ajuda"])
    ensure(status == 0, "aury ajuda precisa sair com status 0")
    ensure(f"💜 Aury {CURRENT_VERSION}" in output, "aury ajuda precisa expor a versão ativa")
    ensure(not stderr, "aury ajuda não pode vazar stderr no caminho nominal")
    ok("ajuda pública sai com 0 e sem ruído")

    status, output, stderr = run_public(["abra", "o", "arquivo", "relatorio.pdf"])
    ensure(status == 1, "fallback honesto precisa sair com status 1")
    ensure("não consegui entender esse pedido com segurança" in output, "fallback honesto precisa expor a mensagem pública esperada")
    ensure("aury ajuda" in output, "fallback honesto precisa oferecer dica de ajuda")
    ensure(not stderr, "fallback honesto não pode vazar stderr")
    ok("fallback honesto sai com 1")

    status, output, stderr = run_public(["remover", "ela"])
    ensure(status == 1, "bloqueio destrutivo sem alvo seguro precisa sair com status 1")
    ensure("não vou remover nada sem um alvo explícito." in output, "bloqueio destrutivo precisa expor a mensagem pública esperada")
    ensure(not stderr, "bloqueio destrutivo não pode vazar stderr")
    ok("bloqueio destrutivo sai com 1")

    direct_proc = run_python(["abra", "o", "arquivo", "relatorio.pdf"])
    ensure(direct_proc.returncode == 120, "runtime Python direto precisa devolver 120 para pedido fora do recorte")
    ensure(not direct_proc.stdout.strip(), "runtime Python direto não deve fingir fallback honesto para pedido fora do recorte")
    ensure(not direct_proc.stderr.strip(), "runtime Python direto não deve vazar stderr para pedido fora do recorte")

    direct_proc = run_python(["remover", "ela"])
    ensure(direct_proc.returncode == 120, "runtime Python direto precisa devolver 120 para bloqueio destrutivo sem alvo seguro")
    ensure(not direct_proc.stdout.strip(), "runtime Python direto não deve fingir bloqueio público quando a ação ainda depende do Fish")
    ensure(not direct_proc.stderr.strip(), "runtime Python direto não deve vazar stderr para bloqueio destrutivo sem alvo seguro")
    ok("rota Python não suportada permanece silenciosa para fora do recorte e bloqueio destrutivo")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        direct_proc = run_python(["criar", "arquivo", "teste.txt"], cwd=workdir)
        ensure(direct_proc.returncode == 120, "runtime Python direto precisa devolver 120 quando a ação ainda depende do Fish")
        ensure(not direct_proc.stdout.strip(), "runtime Python direto não deve fingir sucesso em ação ainda híbrida")
        ensure(not direct_proc.stderr.strip(), "runtime Python direto não deve vazar erro para ação ainda híbrida")

        status, output, stderr = run_public(["criar", "arquivo", "teste.txt"], cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 quando o fallback para o Fish fecha a ação")
        ensure("eu criei o arquivo 'teste.txt'" in output, "entrada pública precisa materializar o sucesso no Fish")
        ensure((workdir / "teste.txt").is_file(), "entrada pública precisa executar a criação do arquivo no fallback Fish")
        ensure(not stderr, "fallback estrutural para o Fish não pode vazar stderr")
    ok("fronteira Python 120 -> Fish 0 permanece explícita e auditável")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (workdir / "teste.txt").write_text("ok\n", encoding="utf-8")
        write_stub(
            bin_dir,
            "zip",
            "#!/usr/bin/env bash\narchive=\"$2\"\n: > \"$archive\"\n",
        )
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        direct_proc = run_python(["compactar", "arquivo", "teste.txt", "para", "teste.zip"], cwd=workdir, env=env)
        ensure(direct_proc.returncode == 120, "runtime Python direto precisa devolver 120 para compactação ainda híbrida")
        ensure(not direct_proc.stdout.strip(), "runtime Python direto não deve fingir sucesso na compactação ainda híbrida")
        ensure(not direct_proc.stderr.strip(), "runtime Python direto não deve vazar erro na compactação ainda híbrida")

        status, output, stderr = run_public(["compactar", "arquivo", "teste.txt", "para", "teste.zip"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 quando a compactação fecha no Fish")
        ensure("eu compactei 'teste.txt' em 'teste.zip'" in output, "compactação pública precisa materializar o sucesso no Fish")
        ensure((workdir / "teste.zip").is_file(), "compactação pública precisa produzir o arquivo final esperado")
        ensure(not stderr, "compactação pública bem-sucedida não pode vazar stderr")
    ok("fronteira Python 120 -> Fish 0 também permanece explícita para compactação")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        (workdir / "teste.txt").write_text("ok\n", encoding="utf-8")
        (workdir / "projetos").mkdir(parents=True, exist_ok=True)

        status, output, stderr = run_public(["compactar", "arquivo", "ausente.txt", "para", "teste.zip"], cwd=workdir)
        ensure(status == 1, "compactação com arquivo inexistente precisa sair com status 1")
        ensure("não encontrei o arquivo 'ausente.txt' para compactar." in output, "compactação com arquivo inexistente precisa expor erro honesto")
        ensure(not stderr, "compactação com arquivo inexistente não pode vazar stderr")

        status, output, stderr = run_public(["compactar", "arquivo", "projetos/", "para", "teste.zip"], cwd=workdir)
        ensure(status == 1, "compactação com tipo de origem incompatível precisa sair com status 1")
        ensure("esperei um arquivo para compactar, mas 'projetos/' é uma pasta." in output, "compactação com tipo incompatível precisa expor erro honesto")
        ensure(not stderr, "compactação com tipo incompatível não pode vazar stderr")

        status, output, stderr = run_public(["compactar", "arquivo", "teste.txt", "para", "saida/teste.zip"], cwd=workdir)
        ensure(status == 1, "compactação com diretório-pai inexistente precisa sair com status 1")
        ensure("o arquivo de saída precisa ser um caminho válido terminado em .zip ou .tar.gz." in output, "compactação com saída inválida precisa expor erro honesto")
        ensure(not stderr, "compactação com saída inválida não pode vazar stderr")

        (workdir / "teste.zip").write_text("old\n", encoding="utf-8")
        status, output, stderr = run_public(["compactar", "arquivo", "teste.txt", "para", "teste.zip"], cwd=workdir)
        ensure(status == 1, "compactação com conflito de saída precisa sair com status 1")
        ensure("o arquivo de saída já existe: 'teste.zip'." in output, "compactação com conflito de saída precisa expor erro honesto")
        ensure(not stderr, "compactação com conflito de saída não pode vazar stderr")
    ok("bloqueios públicos mínimos da compactação saem com 1 e sem ruído")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (workdir / "teste.txt").write_text("ok\n", encoding="utf-8")
        write_stub(bin_dir, "dirname", f"#!{BASH_BIN}\nexec {DIRNAME_BIN} \"$@\"\n")
        status, output, stderr = run_public(
            ["compactar", "arquivo", "teste.txt", "para", "teste.zip"],
            env={"PATH": str(bin_dir)},
            cwd=workdir,
        )
        ensure(status == 1, "compactação sem backend precisa sair com status 1")
        ensure("não encontrei o backend necessário para criar 'teste.zip'." in output, "compactação sem backend precisa expor erro honesto")
        ensure(not stderr, "compactação sem backend não pode vazar stderr")
    ok("ausência do backend de compactação sai com 1")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (workdir / "teste.txt").write_text("ok\n", encoding="utf-8")
        write_stub(
            bin_dir,
            "zip",
            "#!/usr/bin/env bash\narchive=\"$2\"\nprintf 'partial\\n' > \"$archive\"\nexit 12\n",
        )
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        status, output, stderr = run_public(["compactar", "arquivo", "teste.txt", "para", "teste.zip"], env=env, cwd=workdir)
        ensure(status == 1, "falha operacional da compactação precisa sair com status 1")
        ensure("não consegui compactar 'teste.txt' em 'teste.zip'." in output, "falha operacional da compactação precisa expor erro honesto")
        ensure(not stderr, "falha operacional da compactação não pode vazar stderr")
        ensure(not (workdir / "teste.zip").exists(), "falha operacional da compactação não pode deixar o arquivo final")
        ensure(
            not any(path.name.startswith(".aury-compact.") for path in workdir.iterdir()),
            "falha operacional da compactação não pode deixar artefato temporário parcial",
        )
    ok("falha operacional da compactação limpa o artefato parcial")

    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "librespeed-cli", "#!/usr/bin/env bash\nexit 12\n")
        status, output, stderr = run_public(["velocidade", "da", "internet"], env={"PATH": f"{bin_dir}:{os.environ['PATH']}"})
        ensure(status == 1, "falha operacional do speedtest precisa sair com status 1")
        ensure("retornou erro operacional" in output, "falha operacional do speedtest precisa expor erro honesto")
        ensure(not stderr, "falha operacional do speedtest não pode vazar stderr")
    ok("erro operacional do speedtest sai com 1")

    direct_proc = run_python(["procurar", "steam"], env={"PATH": ""})
    ensure(direct_proc.returncode == 1, "backend ausente em rota Python suportada precisa sair com status 1")
    ensure("backend 'pacman' não está disponível" in direct_proc.stdout, "backend ausente em rota Python suportada precisa expor erro honesto")
    ensure(not direct_proc.stderr.strip(), "backend ausente em rota Python suportada não pode vazar stderr")
    ok("backend ausente em rota Python suportada sai com 1")

    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", f"#!{BASH_BIN}\nexit 12\n")
        direct_proc = run_python(["procurar", "steam"], env={"PATH": str(bin_dir)})
        ensure(direct_proc.returncode == 1, "falha operacional em rota Python suportada precisa sair com status 1")
        ensure("backend 'pacman' retornou erro operacional" in direct_proc.stdout, "falha operacional em rota Python suportada precisa expor erro honesto")
        ensure(not direct_proc.stderr.strip(), "falha operacional em rota Python suportada não pode vazar stderr")
    ok("falha operacional em rota Python suportada sai com 1")

    with tempfile.TemporaryDirectory() as tmp:
        bin_dir = Path(tmp) / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "python3", "#!/usr/bin/env bash\nexit 127\n")
        write_stub(bin_dir, "python", "#!/usr/bin/env bash\nexit 127\n")
        path_env = {"PATH": f"{bin_dir}:{os.environ['PATH']}"}

        status, output, stderr = run_public(["ajuda"], env=path_env)
        ensure(status == 0, "fallback local de ajuda precisa sair com 0 quando o Python não sobe")
        ensure(f"💜 Aury {CURRENT_VERSION}" in output, "fallback local de ajuda precisa continuar lendo VERSION da base ativa")
        ensure(not stderr, "fallback local de ajuda não pode vazar stderr")

        status, output, stderr = run_public(["--version"], env=path_env)
        ensure(status == 0, "fallback local de version precisa sair com 0 quando o Python não sobe")
        ensure(output.strip() == f"💜 Aury {CURRENT_VERSION}", "fallback local de version precisa continuar lendo VERSION da base ativa")
        ensure(not stderr, "fallback local de version não pode vazar stderr")

        status, output, stderr = run_public(["dev", "instalar", "firefox"], env=path_env)
        ensure(status == 0, "fallback local de 'aury dev <frase>' precisa sair com 0 quando o Python não sobe")
        ensure("Entrada global" in output, "fallback local de 'aury dev <frase>' precisa expor o relatório local do Fish")
        ensure("Instalar 'firefox'." in output, "fallback local de 'aury dev <frase>' precisa preservar o resumo público")
        ensure(not stderr, "fallback local de 'aury dev <frase>' não pode vazar stderr")
    ok("fallbacks técnicos de help/version/dev continuam limpos quando o Python devolve 127")

    print("audit_exit_surfaces: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
