from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from aury import core_api

CANONICAL_PACKAGE_DIR = ROOT / "python" / "aury"
DIVERGENT_PACKAGE_DIR = ROOT / "aury" / "python" / "aury"
EXPECTED_CORE_API_EXPORTS = {
    "HostProfile",
    "PackageActionPolicy",
    "HostMaintenanceActionPolicy",
    "PackageExecutionPlan",
    "SupportedRuntimeRoute",
    "ActionExecutionPlan",
    "SequenceExecutionPlan",
    "detect_host_profile",
    "resolve_package_action_policy",
    "resolve_host_maintenance_action_policy",
    "build_package_execution_plan",
    "plan_action_execution",
    "plan_sequence_execution",
}


class CanonicalCoreSurfaceAuditTestCase(unittest.TestCase):
    def test_core_api_exports_only_the_canonical_subset(self) -> None:
        self.assertEqual(set(core_api.__all__), EXPECTED_CORE_API_EXPORTS)
        self.assertFalse(hasattr(core_api, "execute"))
        self.assertFalse(hasattr(core_api, "prepare_analyses"))
        self.assertEqual(Path(core_api.__file__).resolve(), CANONICAL_PACKAGE_DIR / "core_api.py")

    def test_core_api_symbols_resolve_from_the_canonical_tree(self) -> None:
        if not DIVERGENT_PACKAGE_DIR.is_dir():
            self.skipTest("artefato aninhado não está presente nesta worktree")

        self.assertTrue((DIVERGENT_PACKAGE_DIR / "host.py").is_file())
        self.assertFalse((DIVERGENT_PACKAGE_DIR / "core_api.py").exists())

        for export_name in core_api.__all__:
            with self.subTest(symbol=export_name):
                exported = getattr(core_api, export_name)
                module = importlib.import_module(exported.__module__)
                module_path = Path(module.__file__).resolve()
                self.assertTrue(
                    CANONICAL_PACKAGE_DIR in module_path.parents or module_path == CANONICAL_PACKAGE_DIR / "__init__.py",
                )
                self.assertNotIn(DIVERGENT_PACKAGE_DIR, module_path.parents)


if __name__ == "__main__":
    unittest.main()
