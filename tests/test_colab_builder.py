from __future__ import annotations

import json
from pathlib import Path

from build_zerve_notebook import (
    build_notebook,
    clear_cell_state,
    collect_wm_package_files,
    sanitize_embedded_python_source,
)
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


def test_portable_notebook_clears_execution_state_and_preserves_order(tmp_path: Path) -> None:
    takeover = new_notebook(
        cells=[
            new_markdown_cell("# Question"),
            new_code_cell("answer = 42", execution_count=7, outputs=[]),
        ]
    )
    scratch = new_notebook(cells=[*takeover.cells, new_code_cell("exploration = True")])
    takeover_path = tmp_path / "takeover.ipynb"
    scratch_path = tmp_path / "scratch.ipynb"
    takeover_path.write_text(json.dumps(takeover), encoding="utf-8")
    scratch_path.write_text(json.dumps(scratch), encoding="utf-8")

    generated = build_notebook(
        takeover_path=takeover_path,
        scratch_path=scratch_path,
        output_path=tmp_path / "portable.ipynb",
        file_entries=[],
        install_wm_editable=False,
        include_scratch=True,
    )

    assert generated.cells[0].source == "# Question"
    assert generated.cells[1].source == "answer = 42"
    assert generated.cells[1].execution_count is None
    assert generated.cells[1].outputs == []
    assert generated.cells[-1].source == "exploration = True"


def test_embed_sanitizer_removes_editor_notes_and_keeps_runnable_source() -> None:
    source = """# NOTE TO AI EDITORS:
# Internal prose that must not ship in an embedded runtime.

VALUE = 3
WM_NOTEBOOK_LANGUAGE_GUIDE = \"\"\"
private authoring guide
\"\"\"

def answer():
    return VALUE
"""

    sanitized = sanitize_embedded_python_source(source)

    assert "AI EDITORS" not in sanitized
    assert "private authoring guide" not in sanitized
    assert "Source-only guide omitted" in sanitized
    namespace: dict[str, object] = {}
    exec(sanitized, namespace)
    assert namespace["answer"]() == 3  # type: ignore[operator]


def test_embedded_package_manifest_contains_only_distributable_runtime() -> None:
    project_root = Path(__file__).resolve().parents[1]

    entries = collect_wm_package_files(project_root)
    keys = [key for _, key in entries]

    assert "_vendor/wm_notecards_pkg/pyproject.toml" in keys
    assert "_vendor/wm_notecards_pkg/src/wm_notecards/charts.py" in keys
    assert all(".env" not in key for key in keys)
    assert all(".webapp-tester" not in key for key in keys)


def test_clear_cell_state_does_not_mutate_the_input_cell() -> None:
    original = new_code_cell("x = 1", execution_count=9, outputs=[])

    cleared = clear_cell_state(original)

    assert original.execution_count == 9
    assert cleared.execution_count is None
