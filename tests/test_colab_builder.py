from __future__ import annotations

import json
from pathlib import Path

from build_zerve_notebook import (
    WM_COLLAPSE_OUTPUT_TAG,
    WM_ESSENTIAL_TAG,
    WM_HIDE_SOURCE_TAG,
    WM_NOISE_TAG,
    apply_portable_cell_policy,
    build_embed_cell,
    build_embed_cell_source,
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
    scratch = new_notebook(
        cells=[
            takeover.cells[0],
            new_code_cell("scratch_before = True"),
            takeover.cells[1],
            new_code_cell("exploration = True"),
        ]
    )
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
    sources = [cell.source for cell in generated.cells]
    assert sources.count("answer = 42") == 1
    assert sources[-2:] == ["scratch_before = True", "exploration = True"]


def test_embed_sanitizer_removes_editor_notes_and_keeps_runnable_source() -> None:
    source = """# NOTE TO AI EDITORS:
# Internal prose that must not ship in an embedded runtime.

VALUE = 3
WM_NOTEBOOK_LANGUAGE_GUIDE: str = \"\"\"
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


def test_colab_bootstrap_always_prioritizes_embedded_runtime(tmp_path: Path) -> None:
    package_file = tmp_path / "theme.py"
    package_file.write_text("VALUE = 'embedded'\n", encoding="utf-8")

    source = build_embed_cell_source(
        title="Embed",
        cell_tag="embedded",
        file_entries=[(package_file, "_vendor/wm_notecards_pkg/src/wm_notecards/theme.py")],
        install_wm_editable=True,
    )

    assert "_sys.path.insert(0, _r)" in source
    assert "del _sys.modules[_name]" in source
    assert "importlib.invalidate_caches()" in source
    assert "Activated embedded wm-notecards" in source


def test_portable_visibility_policy_is_explicit_and_essential_wins() -> None:
    noise = new_code_cell("print('setup')", metadata={"tags": [WM_NOISE_TAG]})
    hidden = new_code_cell("x = 1", metadata={"tags": [WM_HIDE_SOURCE_TAG]})
    raw = new_code_cell("model.summary()", metadata={"tags": [WM_COLLAPSE_OUTPUT_TAG]})
    essential = new_code_cell(
        "takeaway_card(...)",
        metadata={"tags": [WM_COLLAPSE_OUTPUT_TAG, WM_ESSENTIAL_TAG]},
    )

    noise_out = apply_portable_cell_policy(noise)
    hidden_out = apply_portable_cell_policy(hidden)
    raw_out = apply_portable_cell_policy(raw)
    essential_out = apply_portable_cell_policy(essential)

    assert noise_out.metadata["cellView"] == "form"
    assert noise_out.metadata["jupyter"]["source_hidden"] is True
    assert noise_out.metadata["jupyter"]["outputs_hidden"] is True
    assert noise_out.metadata["collapsed"] is True
    assert hidden_out.metadata["jupyter"]["source_hidden"] is True
    assert "outputs_hidden" not in hidden_out.metadata["jupyter"]
    assert raw_out.metadata["collapsed"] is True
    assert essential_out.metadata["jupyter"]["outputs_hidden"] is False
    assert essential_out.metadata["collapsed"] is False


def test_embedded_helper_is_tagged_as_collapsed_noise(tmp_path: Path) -> None:
    source_file = tmp_path / "helper.py"
    source_file.write_text("VALUE = 1\n", encoding="utf-8")

    cell = build_embed_cell(
        title="Embed",
        cell_tag="embedded",
        file_entries=[(source_file, "helper.py")],
    )

    assert cell is not None
    assert WM_NOISE_TAG in cell.metadata["tags"]
    assert cell.metadata["collapsed"] is True
    assert cell.metadata["jupyter"]["source_hidden"] is True
    assert cell.metadata["jupyter"]["outputs_hidden"] is True
