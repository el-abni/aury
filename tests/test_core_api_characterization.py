from __future__ import annotations

import os
import stat
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

import aury.host as aury_host
from aury.contracts import Analysis
from aury.core_api import (
    ActionExecutionPlan,
    HostMaintenanceActionPolicy,
    HostProfile,
    PackageActionPolicy,
    PackageExecutionPlan,
    SequenceExecutionPlan,
    build_package_execution_plan,
    detect_host_profile,
    plan_action_execution,
    plan_sequence_execution,
    resolve_host_maintenance_action_policy,
    resolve_package_action_policy,
)

_ORIGINAL_PATH_EXISTS = Path.exists


def write_stub(bin_dir: Path, name: str) -> None:
    path = bin_dir / name
    path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
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


@contextmanager
def temporary_env(overrides: dict[str, str]):
    sentinel = object()
    previous: dict[str, object] = {}
    for key, value in overrides.items():
        previous[key] = os.environ.get(key, sentinel)
        os.environ[key] = value
    try:
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is sentinel:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(old_value)


@contextmanager
def mutable_host_detection() -> None:
    def _path_exists(path: Path) -> bool:
        if path == Path("/run/ostree-booted"):
            return False
        return _ORIGINAL_PATH_EXISTS(path)

    with mock.patch.object(aury_host.Path, "exists", new=_path_exists):
        yield


def package_analysis(intent: str, target: str) -> Analysis:
    summary = f"{intent} o pacote do host '{target}'."
    return Analysis(
        original_text=f"{intent} {target}",
        normalized_text=f"{intent} {target}",
        intent=intent,
        domain="pacote",
        status="CONSISTENTE",
        reason="characterization test",
        summary=summary,
        entities={"alvo_principal": target},
    )


def host_maintenance_analysis(intent: str) -> Analysis:
    return Analysis(
        original_text=f"{intent} sistema",
        normalized_text=f"{intent} sistema",
        intent=intent,
        domain="sistema",
        status="CONSISTENTE",
        reason="characterization test",
        summary=f"{intent} sistema",
        entities={"alvo_principal": "sistema"},
    )


class CoreAPICharacterizationTestCase(unittest.TestCase):
    def test_detect_host_profile_characterizes_mutable_debian_tier_1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("apt-cache", "apt-get", "flatpak", "rpm-ostree"):
                write_stub(bin_dir, command)
            os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "0",
            }
            with mutable_host_detection():
                profile = detect_host_profile(environ=env)
            self.assertIsInstance(profile, HostProfile)
            self.assertEqual(profile.linux_family, "debian")
            self.assertEqual(profile.mutability, "mutable")
            self.assertEqual(profile.support_tier, "tier_1")
            self.assertEqual(profile.package_backends, ("apt-cache", "apt-get"))
            self.assertEqual(profile.observed_package_tools, ("flatpak", "rpm-ostree"))

    def test_resolve_package_action_policy_blocks_atomic_hosts_even_with_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            write_stub(bin_dir, "dnf")
            os_release = write_os_release(root, distro_id="bazzite", distro_like="fedora", name="Bazzite")
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "1",
            }
            policy = resolve_package_action_policy("instalar", environ=env)
            self.assertIsInstance(policy, PackageActionPolicy)
            self.assertEqual(policy.route, "package_install")
            self.assertEqual(policy.status, "SUPPORTED_WITH_POLICY_BLOCK")
            self.assertEqual(policy.backend_label, "-")
            self.assertIn("Atomic/imutável", policy.reason)
            self.assertIsNotNone(policy.block_message)

    def test_resolve_host_maintenance_action_policy_keeps_arch_as_local_maintenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("paru", "pacman"):
                write_stub(bin_dir, command)
            os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "0",
            }
            with mutable_host_detection():
                policy = resolve_host_maintenance_action_policy("atualizar", environ=env)
            self.assertIsInstance(policy, HostMaintenanceActionPolicy)
            self.assertEqual(policy.status, "FUTURE_MIGRATION_CANDIDATE")
            self.assertEqual(policy.route, "maintenance_local_atualizar")
            self.assertEqual(policy.backend_label, "paru + pacman")
            self.assertIn("manutenção local atendida pelo adaptador Fish", policy.reason)

    def test_build_package_execution_plan_characterizes_opensuse_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("zypper", "sudo", "rpm"):
                write_stub(bin_dir, command)
            os_release = write_os_release(
                root,
                distro_id="opensuse-tumbleweed",
                distro_like="opensuse suse",
                name="openSUSE Tumbleweed",
            )
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "0",
            }
            with mutable_host_detection():
                execution_plan = build_package_execution_plan("instalar", "obs studio", environ=env)
            self.assertIsInstance(execution_plan, PackageExecutionPlan)
            self.assertEqual(execution_plan.policy.status, "SUPPORTED_NOW")
            self.assertEqual(execution_plan.package_target, "obs-studio")
            self.assertEqual(
                execution_plan.command,
                ("sudo", "zypper", "--non-interactive", "install", "--", "obs-studio"),
            )
            self.assertEqual(execution_plan.required_commands, ("zypper", "sudo"))
            self.assertEqual(execution_plan.state_probe_label, "rpm")
            self.assertEqual(execution_plan.state_probe_command, ("rpm", "-q", "obs-studio"))

    def test_plan_action_execution_characterizes_supported_package_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("apt-cache", "apt-get", "sudo"):
                write_stub(bin_dir, command)
            os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "0",
            }
            with temporary_env(env), mutable_host_detection():
                action_plan = plan_action_execution(package_analysis("instalar", "firefox"))
            self.assertIsInstance(action_plan, ActionExecutionPlan)
            self.assertEqual(action_plan.status, "SUPPORTED_NOW")
            self.assertEqual(action_plan.route, "package_install")
            self.assertEqual(action_plan.backend, "sudo + apt-get")
            self.assertTrue(action_plan.executes_in_python)

    def test_plan_sequence_execution_executes_in_python_when_all_actions_have_explicit_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("apt-cache", "apt-get", "sudo"):
                write_stub(bin_dir, command)
            os_release = write_os_release(root, distro_id="ubuntu", distro_like="debian", name="Ubuntu")
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "0",
            }
            analyses = [
                package_analysis("procurar", "vlc"),
                package_analysis("instalar", "firefox"),
            ]
            with temporary_env(env), mutable_host_detection():
                sequence_plan = plan_sequence_execution(analyses)
            self.assertIsInstance(sequence_plan, SequenceExecutionPlan)
            self.assertEqual(sequence_plan.decision, "EXECUTE_IN_PYTHON")
            self.assertTrue(sequence_plan.executes_in_python)
            self.assertEqual(tuple(action.route for action in sequence_plan.action_plans), ("package_search", "package_install"))

    def test_plan_sequence_execution_returns_to_fish_when_host_maintenance_stays_local(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bin_dir = root / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            for command in ("paru", "pacman"):
                write_stub(bin_dir, command)
            os_release = write_os_release(root, distro_id="cachyos", distro_like="arch", name="CachyOS")
            env = {
                "PATH": str(bin_dir),
                "AURY_OS_RELEASE_PATH": str(os_release),
                "AURY_OSTREE_BOOTED": "0",
            }
            analyses = [
                package_analysis("instalar", "firefox"),
                host_maintenance_analysis("atualizar"),
            ]
            with temporary_env(env), mutable_host_detection():
                sequence_plan = plan_sequence_execution(analyses)
            self.assertIsInstance(sequence_plan, SequenceExecutionPlan)
            self.assertEqual(sequence_plan.decision, "RETURN_TO_FISH")
            self.assertFalse(sequence_plan.executes_in_python)
            self.assertEqual(sequence_plan.action_plans[0].route, "package_install")
            self.assertEqual(sequence_plan.action_plans[1].status, "FUTURE_MIGRATION_CANDIDATE")
            self.assertIn("adaptador Fish", sequence_plan.reason)


if __name__ == "__main__":
    unittest.main()
