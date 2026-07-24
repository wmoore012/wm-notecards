from __future__ import annotations

import pandas as pd
import pytest

from wm_notecards import WMTheme, eda


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "record_id": ["a", "b", "c", "d", "e", "f"],
            "event_date": [
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                None,
                "2026-01-05",
                "2026-01-06",
            ],
            "outcome": [0, 1, 0, 1, 1, 0],
            "amount": [1.0, 1.0, 1.0, 2.0, None, 80.0],
            "channel": ["web", "web", "store", "web", "store", "web"],
            "is_returning": [True, False, True, True, False, True],
            "note": [f"unique note {index}" for index in range(6)],
        }
    )


def test_eda_contract_is_non_mutating_and_makes_roles_explicit() -> None:
    frame = _frame()
    original = frame.copy(deep=True)

    contract = eda.wm_build_eda_contract(
        frame,
        target="outcome",
        datetime_columns=["event_date"],
        categorical_columns=["channel"],
        skew_threshold=0.75,
    )

    pd.testing.assert_frame_equal(frame, original)
    roles = contract.set_index("field")["role"].to_dict()
    assert roles == {
        "record_id": "identifier",
        "event_date": "time",
        "outcome": "target",
        "amount": "numeric",
        "channel": "categorical",
        "is_returning": "boolean / flag",
        "note": "text / high-cardinality",
    }
    amount = contract.set_index("field").loc["amount"]
    assert amount["status"] == "CHECK"
    assert "training data only" in amount["what deserves a decision"]
    assert "0.75" in amount["what deserves a decision"]


def test_eda_contract_rejects_unknown_explicit_columns() -> None:
    with pytest.raises(ValueError, match="Unknown dataframe columns: typo"):
        eda.wm_build_eda_contract(_frame(), datetime_columns=["typo"])


def test_category_share_table_is_grouped_and_ranked_by_share() -> None:
    result = eda.wm_build_category_share_table(
        _frame(),
        ["channel", "is_returning"],
        labels={"channel": "Channel used", "is_returning": "Returning"},
    )

    channel = result[result["field group"] == "Channel used"]
    assert channel["category"].tolist() == ["web", "store"]
    assert channel["share of all rows"].tolist() == pytest.approx([4 / 6, 2 / 6])
    assert result.groupby("field group")["share of all rows"].sum().tolist() == pytest.approx(
        [1.0, 1.0]
    )


def test_correlation_clues_print_the_chosen_threshold_and_rank_pairs() -> None:
    frame = pd.DataFrame(
        {
            "a": [1, 2, 3, 4, 5],
            "duplicate": [2, 4, 6, 8, 10],
            "other": [1, 0, 1, 0, 1],
        }
    )

    clues = eda.wm_build_correlation_clues(frame, threshold=0.90)

    assert clues.iloc[0]["field A"] == "a"
    assert clues.iloc[0]["field B"] == "duplicate"
    assert clues.iloc[0]["status"] == "CHECK"
    assert "0.90 review threshold" in clues.iloc[0]["how to read it"]
    assert "causation" in " ".join(clues["how to read it"])


def test_data_chips_escape_names_and_only_show_incomplete_percentages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered: list[str] = []
    monkeypatch.setattr(
        eda,
        "display",
        lambda obj: rendered.append(str(getattr(obj, "data", obj))),
    )
    frame = pd.DataFrame({"<unsafe>": [1.0, None], "group": ["A", "B"]})

    eda.display_data_chips(frame, theme=WMTheme.light(), categorical_columns=["group"])

    html = rendered[-1]
    assert "&lt;unsafe&gt;" in html
    assert "<unsafe>" not in html
    assert "50% complete" in html
    assert "100% complete" not in html
    assert "wm-data-chip--missing" in html
    assert "--wm-chip-color:#16C7E8" in html
    assert "--wm-chip-color:#EAFBFE" in html
    assert "background:var(--wm-chip-color)" in html
    assert "color:var(--wm-chip-text)" in html
    assert "Only fields with missing values glow" not in html
    assert "The model question" not in html
    assert "border:0" in html
    assert "text-shadow:none" in html
    assert "box-shadow:none" in html
    assert "outline:none" in html
    assert "box-shadow:0 0 0 5px" in html
    assert "#FFF5C4" in html


def test_eda_overview_does_not_invent_a_question(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(eda, "question_card", lambda **kwargs: calls.append(("question", kwargs)))
    monkeypatch.setattr(
        eda, "display_data_chips", lambda *args, **kwargs: calls.append(("chips", kwargs))
    )
    monkeypatch.setattr(
        eda,
        "wm_render_micro_profile_cards",
        lambda *args, **kwargs: calls.append(("profiles", kwargs)),
    )
    monkeypatch.setattr(
        eda,
        "wm_render_styler",
        lambda *args, **kwargs: calls.append(("contract", kwargs)),
    )

    result = eda.wm_eda_overview(
        _frame(),
        theme=WMTheme.light(),
        target="outcome",
        datetime_columns=["event_date"],
        categorical_columns=["channel"],
        skew_threshold=0.75,
    )

    assert [name for name, _ in calls] == ["chips", "profiles", "contract"]
    assert calls[1][1]["skew_threshold"] == 0.75  # type: ignore[index]
    assert list(result.columns) == [
        "field",
        "role",
        "dtype",
        "complete",
        "missing",
        "unique",
        "skew",
        "status",
        "what deserves a decision",
    ]


def test_eda_overview_renders_a_caller_supplied_question(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, object]] = []
    monkeypatch.setattr(eda, "question_card", lambda **kwargs: calls.append(("question", kwargs)))
    monkeypatch.setattr(eda, "display_data_chips", lambda *args, **kwargs: None)
    monkeypatch.setattr(eda, "wm_render_micro_profile_cards", lambda *args, **kwargs: None)
    monkeypatch.setattr(eda, "wm_render_styler", lambda *args, **kwargs: None)

    eda.wm_eda_overview(
        _frame(),
        theme=WMTheme.light(),
        question_title="Which fields can answer the retention question?",
        question_body="Start with the outcome and the time boundary.",
    )

    assert calls[0][1]["title"] == "Which fields can answer the retention question?"  # type: ignore[index]


def test_preprocessing_log_uses_observed_before_and_after_counts() -> None:
    before = pd.DataFrame({"amount": [1.0, None, 3.0]})
    after = pd.DataFrame({"amount": [1.0, 2.0, 3.0], "amount_missing": [False, True, False]})
    decisions = [
        eda.PreprocessingDecision(
            field="amount",
            action="impute",
            method="training median",
            reason="Right-skewed measure with one missing value.",
            fit_scope="train_only",
            keep_missing_indicator=True,
        )
    ]

    log = eda.wm_build_preprocessing_log(before, after, decisions)

    assert log.loc[0, "missing before"] == 1
    assert log.loc[0, "missing after"] == 0
    assert log.loc[0, "fit scope"] == "train_only"
    assert log.loc[0, "status"] == "APPLIED"


def test_feature_manifest_blocks_excluded_fields_from_reentering() -> None:
    decisions = [
        eda.FeatureDecision("amount", "numeric", "candidate", "Measures activity."),
        eda.FeatureDecision("record_id", "identifier", "exclude", "Join key only."),
    ]

    with pytest.raises(ValueError, match="Excluded fields re-entered"):
        eda.wm_validate_feature_manifest(
            pd.DataFrame({"amount": [1.0], "record_id": ["a"]}), decisions
        )


def test_compare_fields_returns_exact_table_and_visual() -> None:
    result = eda.wm_compare_fields(_frame(), fields=["channel"])

    assert result.resolved_fields == ("channel",)
    assert result.comparison_kind == "categorical"
    assert result.table.index.tolist() == ["web", "store"]
    assert result.figure.data[0].orientation == "h"


def test_candidate_chip_alternation_skips_absent_roles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered: list[str] = []
    monkeypatch.setattr(
        eda, "display", lambda obj: rendered.append(str(getattr(obj, "data", obj)))
    )
    frame = pd.DataFrame({"number": [1, 2], "free_text": ["one long note", "another"]})

    eda.display_data_chips(frame, theme=WMTheme.light())

    html = rendered[-1]
    assert "--wm-chip-color:#16C7E8" in html
    assert "--wm-chip-color:#EAFBFE" in html
    assert "border:0" in html
    assert "text-shadow:none" in html
