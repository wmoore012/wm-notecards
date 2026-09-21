from __future__ import annotations

import runpy
from pathlib import Path


def _build_notebook():
    namespace = runpy.run_path(
        Path(__file__).parents[1] / "scripts" / "build_eda_before_after_demo.py"
    )
    return namespace["build_notebook"]()


def test_wide_schema_demo_proves_the_before_after_contract() -> None:
    notebook = _build_notebook()
    source = "\n".join(str(cell.get("source", "")) for cell in notebook.cells)

    assert "assert raw.shape == (rows, 40)" in source
    assert "expected_types=" in source
    assert "display_dtype_change_chips(" in source
    assert "display_data_chips(" in source
    assert "wm_build_preprocessing_log(" in source
    assert 'fit_scope="train_only"' in source
    assert "wm_validate_feature_manifest(" in source
    assert "wm_compare_fields(" in source
    assert "No automatic changes" not in source
    assert "Color names the analytical role" not in source
    assert "A 40-column CSV is not something you should memorize" not in source
    assert "value_counts().nunique() > 1" in source
    assert notebook.cells[1].metadata["tags"] == ["wm-noise"]
    assert all("wm-hide-source" in cell.metadata.get("tags", []) for cell in notebook.cells[2:])
