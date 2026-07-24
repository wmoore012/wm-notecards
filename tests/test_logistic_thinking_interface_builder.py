from __future__ import annotations

import runpy
from pathlib import Path


def _build_notebook():
    namespace = runpy.run_path(
        Path(__file__).parents[1] / "scripts" / "build_logistic_thinking_interface.py"
    )
    return namespace["build_notebook"]()


def test_logistic_story_uses_real_notebook_cells_without_changing_evidence() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells)

    assert "assert customers.shape == (rows, 40)" in source
    assert "LogisticRegression(" in source
    assert "scores.iloc[0][\"model\"] == 'Activity + account context'" in source
    assert "train = prepared.iloc[:split_at]" in source
    assert "validation = prepared.iloc[split_at:]" in source
    assert "SimpleImputer(strategy=\"median\"" in source
    assert "wm_build_preprocessing_log(" in source
    assert "display_data_chips(" in source
    assert "wm_render_micro_profile_cards(" in source
    assert "wm_counterintuitive_card(" in source
    assert "takeaway_card(" in source
    assert "raw_preview" in source
    assert "scores.round(3)" in source
    assert "thresholds.round(3)" in source
    assert "top_coefficients.round(3)" in source
    assert "_plain_panel" not in source
    assert "_captured_html" not in source
    assert "_pair(" not in source
    assert "two_up(" not in source
    assert "capture_output" not in source


def test_each_ordinary_output_precedes_its_notecard_response() -> None:
    notebook = _build_notebook()
    sources = [str(cell.get("source", "")) for cell in notebook.cells]

    expected_pairs = [
        ("raw_preview", "display_cols_by_dtype("),
        ("describe().round(2).T", "wm_render_micro_profile_cards("),
        ('rename("missing").to_frame()', "missing_decisions = pd.DataFrame"),
        ("\ndecision_log", "wm_render_styler(\n    decision_log.style"),
        ("scores.round(3)", "Which model survives validation?"),
        ("thresholds.round(3)", "What changes when recall matters more?"),
        ("top_coefficients.round(3)", "Which signals move the probability most?"),
    ]
    for ordinary, notecard in expected_pairs:
        ordinary_index = next(i for i, source in enumerate(sources) if ordinary in source)
        notecard_index = next(i for i, source in enumerate(sources) if notecard in source)
        assert ordinary_index < notecard_index


def test_logistic_story_keeps_production_language_out_of_visuals() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells).lower()

    forbidden = [
        "before vs. after",
        "traditional pandas workflow",
        "the better version",
        "what this component does",
        "how the ui helps",
        "screenshot 3",
    ]
    assert all(phrase not in source for phrase in forbidden)
    assert notebook.cells[1].metadata["tags"] == ["wm-noise"]
    assert all(
        "wm-hide-source" in cell.metadata.get("tags", [])
        for cell in notebook.cells[2:-1]
        if cell.cell_type == "code" and "wm-noise" not in cell.metadata.get("tags", [])
    )
