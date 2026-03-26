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


def write_os_release(
    root: Path,
    *,
    distro_id: str,
    distro_like: str = "",
    variant_id: str = "",
    name: str = "",
) -> Path:
    path = root / "os-release"
    lines = [f"ID={distro_id}"]
    if distro_like:
        lines.append(f'ID_LIKE="{distro_like}"')
    if variant_id:
        lines.append(f'VARIANT_ID="{variant_id}"')
    if name:
        lines.append(f'NAME="{name}"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


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
        ensure(direct_proc.returncode == 0, "runtime Python direto precisa sair com 0 para criar arquivo suportado agora")
        ensure("eu criei o arquivo 'teste.txt'" in direct_proc.stdout, "runtime Python direto precisa materializar a criação simples de arquivo")
        ensure((workdir / "teste.txt").is_file(), "runtime Python direto precisa criar o arquivo simples")
        ensure(not direct_proc.stderr.strip(), "runtime Python direto não pode vazar stderr em criação simples de arquivo")

        status, output, stderr = run_public(["criar", "arquivo", "teste.txt"], cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para criar arquivo suportado agora")
        ensure("eu criei o arquivo 'teste.txt'" in output, "entrada pública precisa preservar a mensagem canônica de criação de arquivo")
        ensure((workdir / "teste.txt").is_file(), "entrada pública precisa manter o arquivo criado")
        ensure(not stderr, "criação pública de arquivo não pode vazar stderr")
    ok("criação simples de arquivo já fecha direto em Python com superfície pública preservada")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        (workdir / "Downloads").mkdir(parents=True, exist_ok=True)
        direct_proc = run_python(["criar", "pasta", "Relatorios", "em", "Downloads"], cwd=workdir)
        ensure(direct_proc.returncode == 0, "runtime Python direto precisa sair com 0 para criar pasta localizada suportada agora")
        ensure("eu criei a pasta 'Downloads/Relatorios'" in direct_proc.stdout, "runtime Python direto precisa materializar a criação localizada de pasta")
        ensure((workdir / "Downloads" / "Relatorios").is_dir(), "runtime Python direto precisa criar a pasta localizada")
        ensure(not direct_proc.stderr.strip(), "runtime Python direto não pode vazar stderr em criação localizada de pasta")

        status, output, stderr = run_public(["criar", "pasta", "Relatorios", "em", "Downloads"], cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para criar pasta localizada suportada agora")
        ensure("eu criei a pasta 'Downloads/Relatorios'" in output, "entrada pública precisa preservar a mensagem canônica de criação localizada de pasta")
        ensure((workdir / "Downloads" / "Relatorios").is_dir(), "entrada pública precisa manter a pasta localizada criada")
        ensure(not stderr, "criação pública localizada de pasta não pode vazar stderr")
    ok("criação localizada de pasta já fecha direto em Python com superfície pública preservada")

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

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        os_release = write_os_release(workdir, distro_id="cachyos", distro_like="arch", name="CachyOS")
        direct_proc = run_python(["procurar", "steam"], env={"PATH": "", "AURY_OS_RELEASE_PATH": str(os_release)}, cwd=workdir)
        ensure(direct_proc.returncode == 1, "backend ausente em rota Python suportada precisa sair com status 1")
        ensure("backend 'pacman' não está disponível" in direct_proc.stdout, "backend ausente em rota Python suportada precisa expor erro honesto")
        ensure(not direct_proc.stderr.strip(), "backend ausente em rota Python suportada não pode vazar stderr")
    ok("backend ausente em rota Python suportada sai com 1")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "pacman", f"#!{BASH_BIN}\nexit 12\n")
        os_release = write_os_release(workdir, distro_id="cachyos", distro_like="arch", name="CachyOS")
        direct_proc = run_python(["procurar", "steam"], env={"PATH": str(bin_dir), "AURY_OS_RELEASE_PATH": str(os_release)}, cwd=workdir)
        ensure(direct_proc.returncode == 1, "falha operacional em rota Python suportada precisa sair com status 1")
        ensure("backend 'pacman' retornou erro operacional" in direct_proc.stdout, "falha operacional em rota Python suportada precisa expor erro honesto")
        ensure(not direct_proc.stderr.strip(), "falha operacional em rota Python suportada não pode vazar stderr")
    ok("falha operacional em rota Python suportada sai com 1")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\nprintf 'DNF_SHOULD_NOT_RUN\\n'\n")
        os_release = write_os_release(workdir, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 1, "host Atomic bloqueado precisa sair com status 1 no runtime Python direto")
        ensure("bloqueado por política" in direct_proc.stdout, "host Atomic bloqueado precisa expor explicitamente o bloqueio por política")
        ensure("detectado como Atomic/imutável" in direct_proc.stdout, "host Atomic bloqueado precisa expor a mensagem pública honesta")
        ensure("DNF_SHOULD_NOT_RUN" not in direct_proc.stdout, "host Atomic bloqueado não pode tentar mutar pacote do sistema")
        ensure("backend '" not in direct_proc.stdout, "host Atomic bloqueado não pode parecer ausência simples de backend")
        ensure("ferramenta auxiliar" not in direct_proc.stdout, "host Atomic bloqueado não pode parecer ausência de sonda auxiliar")
        ensure(not direct_proc.stderr.strip(), "host Atomic bloqueado não pode vazar stderr")

        status, output, stderr = run_public(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(status == 1, "host Atomic bloqueado precisa sair com status 1 também pela entrada pública")
        ensure("bloqueado por política" in output, "entrada pública precisa expor explicitamente o bloqueio por política em host Atomic")
        ensure("detectado como Atomic/imutável" in output, "entrada pública precisa preservar o bloqueio honesto para host Atomic")
        ensure("DNF_SHOULD_NOT_RUN" not in output, "entrada pública não pode tentar rodar backend de pacote no host Atomic")
        ensure("backend '" not in output, "entrada pública não pode tratar host Atomic como ausência simples de backend")
        ensure("ferramenta auxiliar" not in output, "entrada pública não pode tratar host Atomic como ausência de sonda auxiliar")
        ensure(not stderr, "entrada pública não pode vazar stderr no bloqueio Atomic")

        status, output, stderr = run_public(["dev", "instalar", "firefox"], env=env, cwd=workdir)
        ensure(status == 0, "aury dev em host Atomic precisa continuar saindo com 0")
        ensure("fronteira:" in output and "bloqueado por política" in output, "aury dev em host Atomic precisa tornar a fronteira de compatibilidade explícita")
        ensure("compatibilidade:" in output and "bloqueado por política" in output, "aury dev em host Atomic precisa alinhar a taxonomia da ação de pacote")
        ensure(not stderr, "aury dev em host Atomic não pode vazar stderr")
    ok("host Atomic fica bloqueado com honestidade e sem mutação implícita")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        os_release = write_os_release(workdir, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        env = {"PATH": "", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 1, "host Atomic sem backend aparente precisa continuar bloqueado por política")
        ensure("bloqueado por política" in direct_proc.stdout, "host Atomic sem backend aparente precisa continuar saindo como política de produto")
        ensure("backend '" not in direct_proc.stdout, "host Atomic sem backend aparente não pode parecer simples ausência de backend")
        ensure("ferramenta auxiliar" not in direct_proc.stdout, "host Atomic sem backend aparente não pode parecer simples ausência de sonda auxiliar")
        ensure(not direct_proc.stderr.strip(), "host Atomic sem backend aparente não pode vazar stderr")
    ok("host Atomic continua bloqueado por política mesmo sem backend aparente")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "paru", "#!/usr/bin/env bash\nprintf 'PARU_UPDATE_STUB %s\\n' \"$*\"\n")
        write_stub(bin_dir, "pacman", "#!/usr/bin/env bash\nprintf 'PACMAN_UNUSED %s\\n' \"$*\"\n")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "journalctl", "#!/usr/bin/env bash\nprintf 'JOURNALCTL_STUB %s\\n' \"$*\"\n")
        write_stub(bin_dir, "paccache", "#!/usr/bin/env bash\nprintf 'PACCACHE_STUB %s\\n' \"$*\"\n")
        os_release = write_os_release(workdir, distro_id="cachyos", distro_like="arch", name="CachyOS")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["atualizar", "sistema"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 120, "manutenção local em Arch precisa continuar devolvendo 120 no runtime Python direto")
        ensure(not direct_proc.stdout.strip(), "runtime Python direto não deve fingir execução de atualizar sistema ainda local ao Fish")
        ensure(not direct_proc.stderr.strip(), "runtime Python direto não pode vazar stderr para atualizar sistema ainda local ao Fish")

        status, output, stderr = run_public(["atualizar", "sistema"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para atualizar sistema ainda local em Arch")
        ensure("PARU_UPDATE_STUB -Syu" in output, "entrada pública precisa preservar a rota local de atualização em Arch")
        ensure(not stderr, "entrada pública não pode vazar stderr em atualizar sistema local de Arch")

        direct_proc = run_python(["otimizar", "sistema"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 120, "manutenção local em Arch precisa continuar devolvendo 120 no runtime Python direto para otimizar sistema")
        ensure(not direct_proc.stdout.strip(), "runtime Python direto não deve fingir execução de otimizar sistema ainda local ao Fish")
        ensure(not direct_proc.stderr.strip(), "runtime Python direto não pode vazar stderr para otimizar sistema ainda local ao Fish")

        status, output, stderr = run_public(["otimizar", "sistema"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para otimizar sistema ainda local em Arch")
        ensure("PACCACHE_STUB -rk2" in output, "entrada pública precisa preservar a rota local de otimização em Arch")
        ensure("JOURNALCTL_STUB --vacuum-time=7d" in output, "entrada pública precisa preservar o passo local de journalctl em Arch")
        ensure(not stderr, "entrada pública não pode vazar stderr em otimizar sistema local de Arch")
    ok("manutenção local em Arch continua no Fish sem fingir rota Python portátil")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        os_release = write_os_release(workdir, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
        env = {"PATH": os.environ["PATH"], "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["atualizar", "sistema"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 1, "atualizar sistema em Debian precisa sair com status 1 no runtime Python direto")
        ensure("manutenção do host" in direct_proc.stdout, "atualizar sistema em Debian precisa expor que pertence à manutenção do host")
        ensure("fora do recorte equivalente" in direct_proc.stdout, "atualizar sistema em Debian precisa expor a ausência de equivalência na linha 1.x")
        ensure("backend '" not in direct_proc.stdout, "atualizar sistema em Debian não pode parecer simples ausência de backend")
        ensure(not direct_proc.stderr.strip(), "atualizar sistema em Debian não pode vazar stderr")

        status, output, stderr = run_public(["atualizar", "sistema"], env=env, cwd=workdir)
        ensure(status == 1, "entrada pública precisa sair com status 1 para atualizar sistema em Debian")
        ensure("manutenção do host" in output, "entrada pública precisa preservar o enquadramento de manutenção do host em Debian")
        ensure("fora do recorte equivalente" in output, "entrada pública precisa preservar a ausência de equivalência em Debian")
        ensure("backend '" not in output, "entrada pública não pode tratar atualizar sistema em Debian como backend ausente")
        ensure(not stderr, "entrada pública não pode vazar stderr para atualizar sistema em Debian")
    ok("manutenção do host em Debian sai como fora do recorte, não como backend ausente")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "dnf", "#!/usr/bin/env bash\nprintf 'DNF_SHOULD_NOT_RUN\\n'\n")
        os_release = write_os_release(workdir, distro_id="bazzite", distro_like="fedora", name="Bazzite")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["otimizar", "sistema"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 1, "host Atomic precisa sair com status 1 ao bloquear otimizar sistema no runtime Python direto")
        ensure("bloqueado por política" in direct_proc.stdout, "host Atomic precisa expor bloqueio por política em otimizar sistema")
        ensure("DNF_SHOULD_NOT_RUN" not in direct_proc.stdout, "host Atomic não pode tentar backend local para otimizar sistema")
        ensure("backend '" not in direct_proc.stdout, "host Atomic não pode parecer ausência simples de backend em otimizar sistema")
        ensure(not direct_proc.stderr.strip(), "host Atomic não pode vazar stderr ao bloquear otimizar sistema")

        status, output, stderr = run_public(["otimizar", "sistema"], env=env, cwd=workdir)
        ensure(status == 1, "entrada pública precisa sair com status 1 para otimizar sistema em host Atomic")
        ensure("bloqueado por política" in output, "entrada pública precisa preservar o bloqueio por política em otimizar sistema")
        ensure("DNF_SHOULD_NOT_RUN" not in output, "entrada pública não pode tentar backend local em otimizar sistema no host Atomic")
        ensure("backend '" not in output, "entrada pública não pode tratar host Atomic como backend ausente em otimizar sistema")
        ensure(not stderr, "entrada pública não pode vazar stderr ao bloquear otimizar sistema em host Atomic")
    ok("manutenção do host em Atomic continua bloqueada por política")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        firefox_state = workdir / "firefox.installed"
        vlc_state = workdir / "vlc.installed"
        vlc_state.write_text("installed\n", encoding="utf-8")
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(
            bin_dir,
            "zypper",
            "#!/usr/bin/env bash\n"
            f"firefox_state={firefox_state!s}\n"
            f"vlc_state={vlc_state!s}\n"
            "if [ \"$1\" = \"search\" ] && [ \"$3\" = \"steam\" ]; then\n"
            "  printf 'ZYPPER_SEARCH_STUB %s\\n' \"$*\"\n"
            "  exit 0\n"
            "fi\n"
            "if [ \"$1\" = \"--non-interactive\" ] && [ \"$2\" = \"install\" ] && [ \"$4\" = \"firefox\" ]; then\n"
            "  touch \"$firefox_state\"\n"
            "  printf 'ZYPPER_INSTALL_STUB %s\\n' \"$*\"\n"
            "  exit 0\n"
            "fi\n"
            "if [ \"$1\" = \"--non-interactive\" ] && [ \"$2\" = \"remove\" ] && [ \"$4\" = \"vlc\" ]; then\n"
            "  rm -f \"$vlc_state\"\n"
            "  printf 'ZYPPER_REMOVE_STUB %s\\n' \"$*\"\n"
            "  exit 0\n"
            "fi\n"
            "exit 12\n",
        )
        write_stub(
            bin_dir,
            "rpm",
            "#!/usr/bin/env bash\n"
            f"firefox_state={firefox_state!s}\n"
            f"vlc_state={vlc_state!s}\n"
            "if [ \"$1\" = \"-q\" ] && [ \"$2\" = \"firefox\" ]; then\n"
            "  if [ -f \"$firefox_state\" ]; then\n"
            "    exit 0\n"
            "  fi\n"
            "  exit 1\n"
            "fi\n"
            "if [ \"$1\" = \"-q\" ] && [ \"$2\" = \"vlc\" ]; then\n"
            "  if [ -f \"$vlc_state\" ]; then\n"
            "    exit 0\n"
            "  fi\n"
            "  exit 1\n"
            "fi\n"
            "exit 1\n",
        )
        os_release = write_os_release(workdir, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["procurar", "steam"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 0, "OpenSUSE mutável precisa executar busca de pacote no runtime Python direto")
        ensure("ZYPPER_SEARCH_STUB search -- steam" in direct_proc.stdout, "OpenSUSE mutável precisa usar zypper na busca de pacote")
        ensure(not direct_proc.stderr.strip(), "busca de pacote em OpenSUSE mutável não pode vazar stderr")

        status, output, stderr = run_public(["procurar", "steam"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para busca de pacote em OpenSUSE mutável")
        ensure("ZYPPER_SEARCH_STUB search -- steam" in output, "entrada pública precisa preservar a busca real em zypper")
        ensure(not stderr, "entrada pública não pode vazar stderr na busca em OpenSUSE mutável")

        firefox_state.unlink(missing_ok=True)
        direct_proc = run_python(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 0, "OpenSUSE mutável precisa executar instalação de pacote no runtime Python direto")
        ensure("ZYPPER_INSTALL_STUB --non-interactive install -- firefox" in direct_proc.stdout, "OpenSUSE mutável precisa usar sudo + zypper na instalação")
        ensure(not direct_proc.stderr.strip(), "instalação de pacote em OpenSUSE mutável não pode vazar stderr")

        firefox_state.unlink(missing_ok=True)
        status, output, stderr = run_public(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para instalação de pacote em OpenSUSE mutável")
        ensure("ZYPPER_INSTALL_STUB --non-interactive install -- firefox" in output, "entrada pública precisa preservar a instalação real em zypper")
        ensure(not stderr, "entrada pública não pode vazar stderr na instalação em OpenSUSE mutável")

        vlc_state.write_text("installed\n", encoding="utf-8")
        direct_proc = run_python(["remover", "vlc"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 0, "OpenSUSE mutável precisa executar remoção de pacote no runtime Python direto")
        ensure("ZYPPER_REMOVE_STUB --non-interactive remove -- vlc" in direct_proc.stdout, "OpenSUSE mutável precisa usar sudo + zypper na remoção")
        ensure(not direct_proc.stderr.strip(), "remoção de pacote em OpenSUSE mutável não pode vazar stderr")

        vlc_state.write_text("installed\n", encoding="utf-8")
        status, output, stderr = run_public(["remover", "vlc"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para remoção de pacote em OpenSUSE mutável")
        ensure("ZYPPER_REMOVE_STUB --non-interactive remove -- vlc" in output, "entrada pública precisa preservar a remoção real em zypper")
        ensure(not stderr, "entrada pública não pode vazar stderr na remoção em OpenSUSE mutável")
    ok("OpenSUSE mutável entra com execução real contida de pacote do host")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nprintf 'No matching items found.\\n'\nexit 104\n")
        os_release = write_os_release(workdir, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["procurar", "steam"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 0, "busca sem resultado em OpenSUSE mutável precisa sair com 0 no runtime Python direto")
        ensure("não encontrei resultados para 'steam' no backend 'zypper'" in direct_proc.stdout, "busca sem resultado em OpenSUSE mutável precisa expor a superfície honesta da Aury")
        ensure("No matching items found." not in direct_proc.stdout, "busca sem resultado em OpenSUSE mutável não pode vazar a saída crua do zypper")
        ensure(not direct_proc.stderr.strip(), "busca sem resultado em OpenSUSE mutável não pode vazar stderr")

        status, output, stderr = run_public(["procurar", "steam"], env=env, cwd=workdir)
        ensure(status == 0, "entrada pública precisa sair com 0 para busca sem resultado em OpenSUSE mutável")
        ensure("não encontrei resultados para 'steam' no backend 'zypper'" in output, "entrada pública precisa preservar a mensagem honesta de busca sem resultado em OpenSUSE mutável")
        ensure("No matching items found." not in output, "entrada pública não pode vazar a saída crua do zypper em busca sem resultado")
        ensure(not stderr, "entrada pública não pode vazar stderr em busca sem resultado em OpenSUSE mutável")
    ok("OpenSUSE mutável mantém saída honesta para busca sem resultado")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bin_dir = workdir / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        write_stub(bin_dir, "sudo", "#!/usr/bin/env bash\n\"$@\"\n")
        write_stub(bin_dir, "zypper", "#!/usr/bin/env bash\nprintf 'ZYPPER_SHOULD_NOT_RUN\\n'\n")
        os_release = write_os_release(workdir, distro_id="opensuse-tumbleweed", distro_like="opensuse suse", name="openSUSE Tumbleweed")
        env = {"PATH": f"{bin_dir}:{os.environ['PATH']}", "AURY_OS_RELEASE_PATH": str(os_release)}

        direct_proc = run_python(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(direct_proc.returncode == 1, "OpenSUSE mutável sem sonda auxiliar precisa sair com status 1 no runtime Python direto")
        ensure("ferramenta auxiliar 'rpm'" in direct_proc.stdout, "OpenSUSE mutável sem sonda auxiliar precisa expor a dependência de confirmação de estado")
        ensure("ZYPPER_SHOULD_NOT_RUN" not in direct_proc.stdout, "OpenSUSE mutável sem sonda auxiliar não pode tentar instalar sem a confirmação necessária")
        ensure(not direct_proc.stderr.strip(), "OpenSUSE mutável sem sonda auxiliar não pode vazar stderr no runtime Python direto")

        status, output, stderr = run_public(["instalar", "firefox"], env=env, cwd=workdir)
        ensure(status == 1, "entrada pública precisa sair com status 1 quando falta a sonda auxiliar em OpenSUSE mutável")
        ensure("ferramenta auxiliar 'rpm'" in output, "entrada pública precisa preservar a explicação honesta da sonda auxiliar ausente")
        ensure("ZYPPER_SHOULD_NOT_RUN" not in output, "entrada pública não pode tentar instalar pacote sem a sonda auxiliar")
        ensure(not stderr, "entrada pública não pode vazar stderr quando falta a sonda auxiliar em OpenSUSE mutável")
    ok("OpenSUSE mutável distingue backend ausente de sonda auxiliar ausente")

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

        status, output, stderr = run_public(["instalar", "firefox"], env=path_env)
        ensure(status == 1, "pacote público precisa sair com status 1 quando o runtime Python não sobe")
        ensure(
            "não consegui aplicar a política canônica de pacote porque o runtime Python não está disponível." in output,
            "pacote público precisa bloquear honestamente quando a política canônica não pode subir",
        )
        ensure(not stderr, "bloqueio público de pacote sem runtime Python não pode vazar stderr")
    ok("help/version/dev continuam limpos com Python 127, e pacote bloqueia honestamente sem política canônica")

    print("audit_exit_surfaces: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
