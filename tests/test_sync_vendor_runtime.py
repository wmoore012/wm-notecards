from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_sync_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "sync_vendor_runtime.py"
    spec = importlib.util.spec_from_file_location("sync_vendor_runtime", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_vendor_sync_copies_changes_and_reports_stale_files(tmp_path) -> None:
    module = _load_sync_module()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    (source / "module.py").write_text("answer = 42\n", encoding="utf-8")
    (target / "module.py").write_text("answer = 0\n", encoding="utf-8")
    (target / "stale.py").write_text("old = True\n", encoding="utf-8")

    changed, stale = module.sync_vendor(source, target)

    assert changed == ["module.py"]
    assert stale == ["stale.py"]
    assert (target / "module.py").read_text(encoding="utf-8") == "answer = 42\n"
    assert (target / "stale.py").exists()
