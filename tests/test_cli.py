from __future__ import annotations

import json
from typing import TYPE_CHECKING

from wm_notecards.cli import scan_project

if TYPE_CHECKING:
    from pathlib import Path


def test_doctor_reports_local_helpers_without_reading_outputs(tmp_path: Path) -> None:
    notebook = {
        "cells": [
            {"cell_type": "code", "source": ["def question_card():\n", "    pass\n"]},
            {"cell_type": "code", "source": ["print('safe')\n"]},
        ]
    }
    (tmp_path / "lesson.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
    outputs = tmp_path / "outputs"
    outputs.mkdir()
    (outputs / "ignored.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
    checkpoints = tmp_path / ".ipynb_checkpoints"
    checkpoints.mkdir()
    (checkpoints / "lesson-checkpoint.ipynb").write_text(
        json.dumps(notebook), encoding="utf-8"
    )

    findings = scan_project(tmp_path)

    assert [(item.kind, item.path, item.cell) for item in findings] == [
        ("local-helper", "lesson.ipynb", 0)
    ]


def test_doctor_catches_copied_eda_helpers(tmp_path: Path) -> None:
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["def display_cols_by_dtype(frame):\n", "    return frame.dtypes\n"],
            }
        ]
    }
    (tmp_path / "wide_eda.ipynb").write_text(json.dumps(notebook), encoding="utf-8")

    findings = scan_project(tmp_path)

    assert len(findings) == 1
    assert findings[0].kind == "local-helper"
    assert "display_cols_by_dtype" in findings[0].detail


def test_doctor_reports_legacy_theme_vendor_and_colab_copy(tmp_path: Path) -> None:
    (tmp_path / "wm_theme.py").write_text("THEME = {}\n", encoding="utf-8")
    vendor = tmp_path / "_vendor" / "wm_notecards_pkg" / "src" / "wm_notecards"
    vendor.mkdir(parents=True)
    (vendor / "__init__.py").write_text("__version__ = 'old'\n", encoding="utf-8")
    (tmp_path / "lesson_COLAB.ipynb").write_text('{"cells": []}', encoding="utf-8")

    kinds = {item.kind for item in scan_project(tmp_path)}

    assert kinds == {"legacy-theme", "vendored-runtime", "duplicate-notebook"}
