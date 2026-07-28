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
    assert "validation_prevalence" in source
    assert "precision_recall_curve(" in source
    assert "Outcome prevalence" in source
    assert "No-skill baseline" not in source
    assert "thresholds.round(3)" in source
    assert "confusion_receipt" in source
    assert "selected_threshold = 0.40" in source
    assert "top_coefficients.round(3)" in source
    assert "feature_ledger" in source
    assert "feature_receipt" in source
    assert "logistic_missingness_first_pass" in source
    assert "logistic_feature_decisions" in source
    assert "logistic_threshold_tradeoff" in source
    assert "logistic_confusion_matrix" in source
    assert "actual vs prior vs target" in source
    assert "rose vs previous month" in source
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
        ('rename("missing").to_frame()', "logistic_missingness_first_pass"),
        ("\ndecision_log", "wm_render_styler(\n    decision_log.style"),
        ("scores.round(3)", "Which model survives validation?"),
        ("prevalence_receipt", "How hard is the less-common outcome"),
        ("thresholds.round(3)", "What changes when recall matters more?"),
        ("\nconfusion_receipt", "At 0.40, who receives outreach"),
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


def test_reference_comparison_keeps_semantics_out_of_color_alone() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells)

    assert 'bar_colors = ["#D8DEE3"]' in source
    assert "bar_colors[focus_index] = theme.accent" in source
    assert 'marker={"symbol": "triangle-up"' in source
    assert 'line_dash="dash"' in source
    assert 'annotation_text="Review line: 25%"' in source
    assert "higher than the prior month" in source
    assert 'y=[0.012] * len(rose)' in source
    assert "cohort in cyan" not in source
    assert 'category_policy="preserve"' in source
    assert source.count("showlegend=False") >= 2


def test_confusion_receipt_is_reconciled_to_validation_rows() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells)

    assert "selected_tn, selected_fp, selected_fn, selected_tp" in source
    assert '== len(validation)' in source
    assert '"validation rows": len(validation)' in source
    assert '"outcome prevalence": validation_prevalence' in source
    assert "go.Heatmap(" in source


def test_missingness_precedes_selected_profile_cards() -> None:
    notebook = _build_notebook()
    sources = [str(cell.get("source", "")) for cell in notebook.cells]

    missing_index = next(
        i for i, source in enumerate(sources) if "logistic_missingness_first_pass" in source
    )
    profile_index = next(
        i for i, source in enumerate(sources) if "wm_render_micro_profile_cards(" in source
    )
    assert missing_index < profile_index


def test_public_audit_tables_are_decision_sized() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells)

    assert 'missing_decisions[["field", "candidate", "decision"]]' in source
    assert 'feature_ledger[[\n    "field", "decision", "observed evidence", "validation test"' in source
    assert "feature_ledger.style" not in source
