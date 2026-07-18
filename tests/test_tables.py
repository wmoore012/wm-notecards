import pandas as pd
import pytest

from wm_notecards import WMTheme
from wm_notecards.tables import (
    WMTableTheme,
    display_cols_by_dtype,
    semantic_table_css,
    style_describe_wm,
    style_df_wm,
    style_outlier_report_wm,
    style_semantic_wm,
    style_with_bg,
    wm_before_after_table,
    wm_fe_decision_table,
    wm_render_micro_profile_cards,
    wm_render_styler,
    wm_semantic_table,
)


def _capture_display(monkeypatch):
    rendered = []

    def fake_display(obj):
        rendered.append(getattr(obj, "data", str(obj)))

    monkeypatch.setattr("wm_notecards.tables.display", fake_display)
    return rendered


def test_style_semantic_wm_adds_status_classes() -> None:
    df = pd.DataFrame(
        {
            "check": ["pass", "fail", "warn", "cached", "missing"],
            "value": [1, 2, 3, 4, 5],
        }
    )

    html = style_semantic_wm(
        df,
        theme=WMTheme.light(),
        semantic_columns=["check"],
    ).to_html()

    assert "wm-semantic--pass" in html
    assert "wm-semantic--fail" in html
    assert "wm-semantic--warn" in html
    assert "wm-semantic--cached" in html
    assert "wm-semantic--missing" in html


def test_semantic_table_css_has_light_and_dark_readable_tokens() -> None:
    light_css = semantic_table_css(WMTheme.light())
    dark_css = semantic_table_css(WMTheme.dark())

    for css in (light_css, dark_css):
        assert ".wm-semantic--before" in css
        assert ".wm-semantic--after" in css
        assert ".wm-semantic--raw" in css
        assert ".wm-semantic--cleaned" in css
        assert "background-color:" in css
        assert "color:" in css
        assert "border-color:" in css


def test_wm_semantic_table_renders_theme_css_without_inline_red_green(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    df = pd.DataFrame({"status": ["before", "after"], "field": ["raw", "cleaned"]})

    wm_semantic_table(
        df,
        theme=WMTheme.light(),
        semantic_columns=["status", "field"],
        title="Cleaning check",
    )

    html = rendered[-1]
    assert "wm-semantic--before" in html
    assert "wm-semantic--after" in html
    assert "wm-semantic--raw" in html
    assert "wm-semantic--cleaned" in html
    assert "#d9534f" not in html
    assert "#5cb85c" not in html


def test_wm_before_after_table_marks_role_columns(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    df = pd.DataFrame(
        {
            "Type (Before)": ["object"],
            "Type (After)": ["datetime64[ns]"],
        }
    )

    wm_before_after_table(
        df,
        theme=WMTheme.light(),
        before_columns=["Type (Before)"],
        after_columns=["Type (After)"],
        title="Before after check",
    )

    html = rendered[-1]
    assert "wm-semantic--before" in html
    assert "wm-semantic--after" in html


def test_wm_render_styler_remains_backward_compatible(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    df = pd.DataFrame({"artist": ["Lute"], "score": [0.91]})

    wm_render_styler(df.style, theme=WMTheme.light(), title="Regular table")

    html = rendered[-1]
    assert "Regular table" in html
    assert "wm-table-card" in html
    assert "wm-semantic--" not in html.split("<tbody", maxsplit=1)[1]


def test_long_table_gets_bounded_scroll_and_sticky_header(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    df = pd.DataFrame({"artist": [f"Artist {idx}" for idx in range(20)]})

    wm_render_styler(df.style, theme=WMTheme.light(), title="Who leads top-N?")

    html = rendered[-1]
    assert "wm-table-scroll--bounded" in html
    assert "max-height:560px" in html
    assert "position: sticky" in html
    assert "tabindex='0'" in html


def test_short_table_stretches_without_forced_vertical_scroll(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    df = pd.DataFrame({"metric": ["HR"], "leader": ["Random"]})

    wm_render_styler(df.style, theme=WMTheme.light(), title="Leaders")

    html = rendered[-1]
    assert "class='wm-table-scroll'" in html
    assert "class='wm-table-scroll wm-table-scroll--bounded'" not in html
    assert "width: max-content; min-width: 100%" in html


def test_standard_tables_enforce_visible_zebra_rows() -> None:
    light = WMTheme.light()
    dark = WMTheme.dark()

    assert light.table_stripe_bg == "rgba(17,17,17,0.055)"
    assert dark.table_stripe_bg == "rgba(255,255,255,0.045)"
    for theme in (light, dark):
        css = WMTableTheme().css(theme)
        assert "tbody tr:nth-child(even) td" in css
        assert f"background: {theme.table_stripe_bg}" in css


def test_table_styling_family_and_micro_profiles(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    theme = WMTheme.light()
    frame = pd.DataFrame(
        {
            "amount": [1.0, 2.0, 99.0, None],
            "outlier_rate": [0.0, 0.03, 0.08, 0.2],
            "status": ["yes", "no", "yes", None],
        }
    )

    assert "background-color" in style_describe_wm(frame.describe(), theme).to_html()
    assert "background-color" in style_outlier_report_wm(
        frame[["outlier_rate"]], theme
    ).to_html()
    assert "font-family" in style_with_bg(frame[["amount"]], theme).to_html()
    assert "Regular" in style_df_wm(frame[["amount"]], "Regular", theme).to_html()

    display_cols_by_dtype(frame.dtypes, theme, "Source schema")
    wm_render_micro_profile_cards(
        frame,
        theme=theme,
        ordinal_columns=["status"],
        visible_cards=2,
    )
    assert "wm-chip-groups" in rendered[-2]
    assert "wm-micro-rail" in rendered[-1]
    assert "wm-micro-violin" in rendered[-1]
    assert "wm-cat-wrap" in rendered[-1]


def test_feature_engineering_table_validates_rows(monkeypatch) -> None:
    rendered = _capture_display(monkeypatch)
    wm_fe_decision_table(
        rows=[
            {
                "status": "pass",
                "call": "Pass: lead candidate",
                "reason": "Built from training data only.",
            }
        ],
        theme=WMTheme.light(),
        title="Feature decision",
    )
    assert "wm-fe-decision-table" in rendered[-1]

    with pytest.raises(ValueError, match="status"):
        wm_fe_decision_table(
            rows=[{"status": "maybe", "call": "Pass: lead candidate", "reason": "x"}],
            theme=WMTheme.light(),
            title="Bad",
        )
