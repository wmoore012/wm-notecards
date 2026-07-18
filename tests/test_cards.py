from __future__ import annotations

import pandas as pd
import pytest

from wm_notecards import WMTheme, cards


def _capture(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    rendered: list[str] = []

    def fake_display(obj: object) -> None:
        rendered.append(str(getattr(obj, "data", obj)))

    monkeypatch.setattr(cards, "display", fake_display)
    return rendered


def test_card_family_renders_one_consistent_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = _capture(monkeypatch)
    theme = WMTheme.light()
    common = {"theme": theme, "kicker": "STANDARD,03,EDA", "chip_text": "Review"}

    cards.question_card(title="What changed?", body="Look at the evidence.", **common)
    cards.question_pair(
        theme=theme,
        left={"title": "What?", "body": "Signal"},
        right={"title": "Why?", "body": "Context"},
        kicker="03,EDA",
    )
    cards.preview_card(title="Preview", body="First answer.", bullets=["Evidence"], **common)
    cards.takeaway_card(title="Takeaway", metric="R² = 0.54", body="Bounded claim.", **common)
    cards.next_think_card(title="Choose next", body="The learner decides.", **common)
    cards.verdict_card(title="Verdict", verdict="check", body="Review, not proof.", **common)
    cards.big_number_card(
        title="Coverage", value="85/690", value_label="weeks", body="A narrow pattern.", **common
    )
    cards.glossary_card(title="Terms", terms=["queue", "lift"], theme=theme, kicker="03,EDA")
    cards.wm_check_card(
        title="Release gate",
        checks=[
            {"label": "Math", "status": "PASS", "detail": "Recomputed"},
            {"label": "Layout", "status": "CHECK"},
            {"label": "Privacy", "status": "FAIL"},
        ],
        **common,
    )
    cards.wm_formula_card(
        title="Formula",
        items=[{"label": "Mean", "latex": r"\bar{x}=\frac{1}{n}\sum_i x_i", "fallback": "average"}],
        **common,
    )
    cards.wm_counterintuitive_card(
        why_misread="A high score can feel conclusive.",
        ordinary_process="Ordinary variation can also create it.",
        conclusion_boundary="Treat it as a review signal.",
        math_items=[{"label": "Score", "fallback": "signal + uncertainty"}],
        **common,
    )

    assert len(rendered) == 11
    assert all("wm-" in html for html in rendered)
    assert any("prefers-reduced-motion" in html for html in rendered)
    assert all("Review" not in html or "wm-shell-chip" in html for html in rendered)


def test_helpers_keep_labels_plain_and_claims_bounded() -> None:
    assert cards.wm_term_definition(" lift ")
    assert cards.wm_display_label("unknown") == "unknown"
    assert "account" in cards.wm_reason_display_label("Amount spike (Z=3.2)")
    assert "unusually" in cards.wm_reason_explainer("Amount spike (Z=3.2)")
    assert cards.stat_card(label="RMSE", value="337.7", theme=WMTheme.light())

    summary = cards.wm_build_reason_summary(pd.Series(["A | B", "A", None]))
    assert summary.to_dict("records") == [
        {"reason": "A", "count": 2},
        {"reason": "B", "count": 1},
    ]


def test_invalid_check_and_formula_inputs_fail_loudly(monkeypatch: pytest.MonkeyPatch) -> None:
    _capture(monkeypatch)
    theme = WMTheme.light()
    with pytest.raises(ValueError, match="at least one"):
        cards.wm_check_card(title="Empty", checks=[], theme=theme)
    with pytest.raises(ValueError, match="formula block"):
        cards.wm_formula_card(title="Empty", items=[], theme=theme)
    with pytest.raises(ValueError, match="at least one"):
        cards._math_panel_html(theme, {})
