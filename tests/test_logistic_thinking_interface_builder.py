from __future__ import annotations

import runpy
from pathlib import Path


def _build_notebook():
    namespace = runpy.run_path(
        Path(__file__).parents[1] / "scripts" / "build_logistic_thinking_interface.py"
    )
    return namespace["build_notebook"]()


def _sources() -> list[str]:
    return [str(cell.get("source", "")) for cell in _build_notebook().cells]


def test_logistic_story_uses_a_real_three_way_pipeline() -> None:
    source = "\n".join(_sources())

    assert "assert customers.shape == (rows, 40)" in source
    assert "LogisticRegression(" in source
    assert 'validation_start = pd.Timestamp("2024-09-01")' in source
    assert 'test_start = pd.Timestamp("2024-11-01")' in source
    assert 'reviewed["snapshot_month"] < validation_start' in source
    assert 'reviewed["snapshot_month"] >= test_start' in source
    assert 'validation["snapshot_month"].max() < test["snapshot_month"].min()' in source
    assert "SimpleImputer(strategy=\"median\"" in source
    assert "OneHotEncoder(handle_unknown=\"ignore\")" in source
    assert "model.fit(" in source
    assert "precision_recall_curve(" in source
    assert "f1_score(" in source
    assert "test_probability = winner.predict_proba" in source
    assert "confusion_matrix(" in source


def test_pandas_and_notecards_follow_one_human_reading_order() -> None:
    sources = _sources()

    raw_head = next(i for i, source in enumerate(sources) if ".head(6)" in source)
    dtype_review = next(i for i, source in enumerate(sources) if "display_cols_by_dtype(" in source)
    missing_bridge = next(i for i, source in enumerate(sources) if "memory bridge" in source)
    missing_visual = next(i for i, source in enumerate(sources) if "logistic_missingness_first_pass" in source)
    numeric_describe = next(i for i, source in enumerate(sources) if "reviewed[numeric_fields].describe()" in source)
    numeric_profiles = next(i for i, source in enumerate(sources) if "columns=numeric_fields" in source)
    categorical_describe = next(i for i, source in enumerate(sources) if "describe(include=\"all\")" in source)
    categorical_profiles = next(i for i, source in enumerate(sources) if "columns=categorical_fields" in source)

    assert raw_head < dtype_review < missing_bridge < missing_visual
    assert missing_visual < numeric_describe < numeric_profiles
    assert numeric_profiles < categorical_describe < categorical_profiles


def test_target_contract_is_loud_and_complete() -> None:
    source = "\n".join(_sources())

    assert "What exactly are we asking the model to predict?" in source
    assert "pictogram_card(" in source
    assert "Customers who left in the next month" in source
    assert "Missing target" in source
    assert "Business cost" in source
    assert "Goodwill boundary" in source
    assert "Expected clues" in source
    assert "base rate becomes the precision-recall baseline" in source


def test_public_model_outputs_use_notecard_tables() -> None:
    sources = _sources()
    source = "\n".join(sources)

    assert "wm_render_styler(\n    scores.style" in source
    assert "wm_render_styler(\n    thresholds.style" in source
    assert "wm_render_styler(\n    confusion_receipt.style" in source
    assert "wm_render_styler(\n    top_coefficients.style" in source
    assert "wm_render_styler(\n    feature_ledger.style" in source
    assert all(not item.rstrip().endswith("scores") for item in sources)
    assert all(not item.rstrip().endswith("thresholds") for item in sources)
    assert all(not item.rstrip().endswith("confusion_receipt") for item in sources)
    assert all(not item.rstrip().endswith("feature_ledger") for item in sources)


def test_exact_tables_stay_adjacent_to_their_visual_explanations() -> None:
    sources = _sources()

    model_cell = next(source for source in sources if "logistic_precision_recall" in source)
    threshold_cell = next(source for source in sources if "logistic_threshold_tradeoff" in source)
    confusion_cell = next(source for source in sources if "logistic_confusion_matrix" in source)
    coefficient_cell = next(source for source in sources if "logistic_coefficient_directions" in source)
    plan_cell = next(source for source in sources if "logistic_plan_leave_rate" in source)

    assert "scores.style" in model_cell
    assert "thresholds.style" in threshold_cell
    assert "confusion_receipt.style" in confusion_cell
    assert "top_coefficients.style" in coefficient_cell
    assert "plan_rates.style" in plan_cell


def test_threshold_is_derived_from_validation_not_invented() -> None:
    source = "\n".join(_sources())

    assert "selected_threshold = float(threshold_path[int(np.argmax(f1_path))])" in source
    assert "Validation F1 selects" in source
    assert "It is not a business policy" in source
    assert "selected_threshold = 0.40" not in source
    assert "Review line: 25%" not in source
    assert "review_target" not in source
    assert "cohort_rate" not in source


def test_split_visual_has_rectangular_train_validation_and_test_blocks() -> None:
    source = "\n".join(_sources())

    assert '("Training",' in source
    assert '("Validation",' in source
    assert '("Test",' in source
    assert "go.Bar(" in source
    assert "lines+markers+text" not in source
    assert "Eight months train. Two choose. Two test once." in source


def test_pipeline_build_fit_score_and_test_are_separate_cells() -> None:
    sources = _sources()

    helper_index = next(i for i, source in enumerate(sources) if "def _pipeline(" in source)
    fit_index = next(i for i, source in enumerate(sources) if "model.fit(" in source)
    score_index = next(i for i, source in enumerate(sources) if "score_rows = []" in source)
    test_index = next(i for i, source in enumerate(sources) if "test_probability =" in source)

    assert helper_index < fit_index < score_index < test_index
    assert "model.fit(" not in sources[helper_index]
    assert "score_rows" not in sources[fit_index]
    assert "test_probability" not in sources[score_index]


def test_visible_copy_avoids_em_dash_and_interface_narration() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells)

    assert "—" not in source
    forbidden = [
        "traditional pandas workflow",
        "the better version",
        "what this component does",
        "how the ui helps",
        "no-skill baseline",
        "customer cohort",
    ]
    assert all(phrase not in source.lower() for phrase in forbidden)


def test_notebook_keeps_public_code_metadata_and_synthetic_boundary() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells).lower()

    assert "synthetic" in source
    assert notebook.cells[1].metadata["tags"] == ["wm-noise"]
    assert all(
        "wm-hide-source" in cell.metadata.get("tags", [])
        for cell in notebook.cells
        if cell.cell_type == "code" and "wm-noise" not in cell.metadata.get("tags", [])
    )
