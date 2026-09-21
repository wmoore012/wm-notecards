from __future__ import annotations

import inspect
import warnings

import pandas as pd
import pytest

from wm_notecards import WMTheme, cards, init_notebook


def _capture(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    rendered: list[str] = []

    def fake_display(obj: object) -> None:
        rendered.append(str(getattr(obj, "data", obj)))

    monkeypatch.setattr(cards, "display", fake_display)
    return rendered


def test_public_quick_start_exposes_a_zero_argument_notebook_initializer() -> None:
    signature = inspect.signature(init_notebook)

    assert all(
        parameter.default is not inspect.Parameter.empty
        for parameter in signature.parameters.values()
    )


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


def test_question_chip_reflows_below_title_row_on_narrow_screens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered = _capture(monkeypatch)
    cards.question_card(
        title="Can a simple model recover the rhythm?",
        body="Keep the evidence legible.",
        chip_text="Safe to share",
        theme=WMTheme.light(),
    )

    html = rendered[0]
    assert "flex-direction:column;align-items:stretch" in html
    assert "font-size:clamp(28px,8.5vw,34px) !important" in html


def test_takeaway_card_renders_every_field_used_by_homework_colab(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered = _capture(monkeypatch)
    bullets = [
        "Winter peak is encoded in monthly adjustments.",
        "Trend leaves room for season.",
        "SES can lose to an honest linear model.",
        "Every forecast is reproducible.",
    ]

    cards.takeaway_card(
        theme=WMTheme.light(),
        title="You picked the model that knew the story.",
        metric="Best validation RMSE and MAPE",
        body="The data wanted two nouns: growth and season.",
        bullets=bullets,
        kicker="Q4 answered, forecasting, assignment complete",
    )

    assert len(rendered) == 1
    html = rendered[0]
    assert "You picked the model that knew the story." in html
    assert "Best validation RMSE and MAPE" in html
    assert "growth and season" in html
    assert "Q4 ANSWERED" in html
    assert all(bullet in html for bullet in bullets)


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


def test_glossary_unknown_terms_fail_instead_of_rendering_a_blank_card(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _capture(monkeypatch)

    with pytest.raises(ValueError, match="Pass a dict"):
        cards.glossary_card(
            title="Terms",
            terms=["not-a-built-in-term"],
            theme=WMTheme.light(),
        )


def test_markdown_cards_render_safe_inline_emphasis(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = _capture(monkeypatch)

    cards.preview_card(
        title="Assignment checklist",
        theme=WMTheme.light(),
        body="Fit **four** models, keep *one* boundary, and copy `summary()`.",
        bullets=["Name the **best** model with `RMSE` evidence."],
    )

    html = rendered[-1]
    assert "<strong>four</strong>" in html
    assert "<em>one</em>" in html
    assert "<code>summary()</code>" in html
    assert "<strong>best</strong>" in html
    assert "**four**" not in html


def test_question_pair_keeps_shared_kicker_inside_both_cards(monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = _capture(monkeypatch)

    cards.question_pair(
        theme=WMTheme.light(),
        kicker="03,MODEL 4,SES,Q3",
        left={"title": "How much memory?", "body": "Tune alpha."},
        right={"title": "Why flat?", "body": "No calendar memory."},
    )

    html = rendered[-1]
    assert html.count("03 • MODEL 4 • SES • Q3") == 2
    assert "margin:0 auto 8px auto" not in html
    assert "grid-template-columns:repeat(2,minmax(0,1fr))" in html
    assert "grid-template-columns:minmax(0,1fr)" in html
    assert ".wm-two-up > *{height:100%;min-width:0;}" in html


def test_formula_card_repairs_real_notebook_double_braces_without_warnings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rendered = _capture(monkeypatch)
    items = [
        {
            "label": "Logistic probability",
            "latex": r"\[\Pr(\text{{claim}}=1\mid x)=\sigma\left(\beta_0 + \sum_j \beta_j x_j\right)\]",
            "fallback": "P(claim=1 | x) = sigmoid(weighted features)",
        },
        {
            "label": "Pipeline rule",
            "latex": r"\[x \rightarrow \text{{impute / scale / encode}} \rightarrow \text{{model}} \rightarrow \hat{{p}}\]",
            "fallback": "raw features -> preprocess -> model -> predicted score",
        },
    ]

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cards.wm_formula_card(
            theme=WMTheme.light(),
            title="The final claim keeps the math visible",
            items=items,
        )

    html = rendered[-1]
    assert caught == []
    assert html.count("class='wm-math-panel'") == 2
    assert html.count("<svg") == 2
    assert r"\text{{" not in html
    assert r"\hat{{" not in html
