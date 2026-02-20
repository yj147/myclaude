import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import install  # noqa: E402


def _module_cfg(target: str) -> dict:
    return {"operations": [{"type": "copy_dir", "target": target}]}


class InstalledStatusDetectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tmpdir.name)
        self.install_dir = self.root / "install"
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.ctx = {
            "install_dir": self.install_dir,
            "status_file": self.install_dir / "installed_modules.json",
            "config_dir": self.root,
        }

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _write_status(self, modules: dict) -> None:
        payload = {"modules": modules}
        self.ctx["status_file"].write_text(json.dumps(payload), encoding="utf-8")

    def test_status_file_takes_precedence_over_filesystem_overlap(self) -> None:
        config = {
            "modules": {
                "do": _module_cfg("skills/do"),
                # claudekit shares target with do, which used to cause false positives.
                "claudekit": _module_cfg("skills/do"),
            }
        }
        (self.install_dir / "skills" / "do").mkdir(parents=True, exist_ok=True)
        self._write_status({"do": {"module": "do", "status": "success"}})

        installed = install.get_installed_modules(config, self.ctx)
        self.assertTrue(installed["do"])
        self.assertFalse(installed["claudekit"])

    def test_filesystem_fallback_when_status_file_missing(self) -> None:
        config = {
            "modules": {
                "do": _module_cfg("skills/do"),
                "course": _module_cfg("skills/dev"),
            }
        }
        (self.install_dir / "skills" / "do").mkdir(parents=True, exist_ok=True)

        installed = install.get_installed_modules(config, self.ctx)
        self.assertTrue(installed["do"])
        self.assertFalse(installed["course"])

    def test_filesystem_fallback_when_status_file_is_invalid(self) -> None:
        config = {"modules": {"do": _module_cfg("skills/do")}}
        (self.install_dir / "skills" / "do").mkdir(parents=True, exist_ok=True)
        self.ctx["status_file"].write_text("{invalid json", encoding="utf-8")

        installed = install.get_installed_modules(config, self.ctx)
        self.assertTrue(installed["do"])


if __name__ == "__main__":
    unittest.main()
