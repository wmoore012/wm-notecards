"""Build the public 40-Column EDA Scratchbook from deterministic synthetic data."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUTPUT = Path("examples/40_column_eda_scratchbook.ipynb")


def build_notebook() -> nbformat.NotebookNode:
    """Return the canonical scratch notebook without private or borrowed data."""
    cells = [
        new_markdown_cell("# 40-Column EDA Scratchbook"),
        new_code_cell(
            """import numpy as np
import pandas as pd
from IPython.display import HTML
from IPython.display import display as display_html

from wm_notecards import (
    FeatureDecision,
    PreprocessingDecision,
    WMTheme,
    init_notebook,
    wm_build_preprocessing_log,
    wm_compare_fields,
    wm_validate_feature_manifest,
)
from wm_notecards.cards import next_think_card, question_card
from wm_notecards.charts import style_fig_wm, wm_render_figure_card
from wm_notecards.eda import display_data_chips
from wm_notecards.tables import (
    display_cols_by_dtype,
    display_dtype_change_chips,
    wm_render_micro_profile_cards,
    wm_render_styler,
)

theme = WMTheme.light()
init_notebook()
RNG_SEED = 20260718"""
        ),
        new_code_cell(
            """rng = np.random.default_rng(RNG_SEED)
rows = 120
dates = pd.date_range("2024-01-01", periods=rows, freq="D")
raw = pd.DataFrame({
    "record_id": [f"SYN-{i:04d}" for i in range(rows)],
    "month": dates.strftime("%Y-%m-%d"),
    "target": rng.normal(82, 9, rows),
    "amount_usd": np.round(rng.lognormal(4.2, .55, rows), 2).astype(str),
    "units": rng.integers(1, 9, rows).astype(str),
    "account_balance": rng.normal(5100, 1250, rows),
    "session_minutes": rng.gamma(3, 8, rows),
    "distance_km": rng.gamma(2, 4, rows),
    "quality_score": rng.beta(6, 2, rows),
    "conversion_rate": rng.beta(2, 8, rows),
    "trend_index": np.arange(rows) / rows,
    "temperature_c": rng.normal(21, 5, rows),
    "discount_rate": rng.choice([0., .1, .2], rows, p=[.58, .30, .12]),
    "customer_age": rng.integers(18, 81, rows),
    "visits_30d": rng.integers(1, 28, rows),
    "impressions_30d": rng.integers(20, 900, rows),
    "clicks_30d": rng.integers(0, 95, rows),
    "orders_30d": rng.integers(0, 12, rows),
    "support_tickets": rng.integers(0, 6, rows),
    "login_attempts": rng.integers(1, 5, rows),
    "days_active": rng.integers(1, 366, rows),
    "tenure_months": rng.integers(1, 121, rows),
    "items_viewed": rng.integers(1, 70, rows),
    "returns_12m": rng.integers(0, 5, rows),
    "cart_adds_30d": rng.integers(0, 45, rows),
    "channel": rng.choice(["Direct", "Partner", "Community"], rows, p=[.55, .30, .15]),
    "region": rng.choice(["North", "South", "East", "West"], rows, p=[.44, .28, .18, .10]),
    "plan": rng.choice(["Free", "Plus", "Pro"], rows, p=[.58, .30, .12]),
    "campaign": rng.choice(["Organic", "Referral", "Launch"], rows, p=[.50, .32, .18]),
    "device": rng.choice(["Mobile", "Desktop", "Tablet"], rows, p=[.62, .30, .08]),
    "market": rng.choice(["US", "CA", "GB", "AU"], rows, p=[.50, .22, .17, .11]),
    "browser": rng.choice(["Chrome", "Safari", "Firefox"], rows, p=[.57, .29, .14]),
    "is_reviewed": rng.choice([True, False], rows, p=[.72, .28]),
    "is_new_customer": rng.choice([True, False], rows, p=[.24, .76]),
    "is_peak_window": pd.Series(dates).dt.month.isin([6, 7, 8]).to_numpy(),
    "has_discount": rng.choice([True, False], rows, p=[.36, .64]),
    "is_returning": rng.choice([True, False], rows, p=[.68, .32]),
    "comment": [f"synthetic review note {i}" for i in range(rows)],
    "source_note": [f"generated row {i}" for i in range(rows)],
    "analyst_note": [f"review later {i}" for i in range(rows)],
})
raw.loc[[7, 38, 91], "amount_usd"] = None
raw.loc[[14, 62], "region"] = None
raw.loc[[3, 57, 99], "comment"] = None
assert raw.shape == (rows, 40)
assert raw["channel"].value_counts().nunique() > 1
assert raw["region"].value_counts().nunique() > 1"""
        ),
        new_code_cell(
            """question_card(
    theme=theme,
    title="Can this file explain why some sessions convert?",
    body=("The outcome is present. Before it becomes a model target, we need to know "
          "whether time, money, and missing values arrived in forms we can trust."),
    kicker="01, source question",
)
display_html(HTML(
    "<style>.wm-raw-scroll{overflow:auto;max-width:100%;padding-bottom:8px}</style>"
    f"<div class='wm-raw-scroll'>{raw.head(5).to_html()}</div>"
))
display_html(HTML(
    f"<div class='wm-raw-scroll'>{raw.describe(include='all').T.head(12).to_html()}</div>"
))
display_cols_by_dtype(
    raw.dtypes, theme, "What arrived in each dtype lane?",
    expected_types={"month": "time", "amount_usd": "numeric", "units": "numeric"},
)"""
        ),
        new_code_cell(
            """reviewed = raw.copy()
reviewed["month"] = pd.to_datetime(reviewed["month"], errors="raise")
reviewed["amount_usd"] = pd.to_numeric(reviewed["amount_usd"], errors="coerce")
reviewed["units"] = pd.to_numeric(reviewed["units"], errors="raise")
display_dtype_change_chips(
    raw.dtypes, reviewed.dtypes, theme=theme,
    title="Three fields moved. The other 37 stayed put.",
    subtitle="month → datetime · amount_usd → float64 · units → int64",
)"""
        ),
        new_code_cell(
            """missingness = wm_compare_fields(reviewed, fields=["amount_usd"], kind="missingness")
wm_render_styler(
    missingness.table.style.format({"complete": "{:.1%}"}), theme=theme,
    title="Three different missingness decisions",
    subtitle="amount_usd can be modeled; region and comment still need semantic decisions.",
    kicker="02, missingness, evidence",
)
style_fig_wm(missingness.figure, title="Missing values by field", theme=theme)
wm_render_figure_card(missingness.figure, theme=theme, file_stub="eda_missingness")"""
        ),
        new_code_cell(
            """suggestions = pd.DataFrame([
    {"field": "amount_usd", "candidate action": "training median + missing indicator",
     "why it is plausible": "Right-skewed measure; the flag preserves the event.", "decision": "APPROVE"},
    {"field": "region", "candidate action": "confirm source semantics",
     "why it is plausible": "Unknown and not applicable are different categories.", "decision": "WAIT"},
    {"field": "comment", "candidate action": "leave missing",
     "why it is plausible": "Optional free text does not need an invented sentence.", "decision": "KEEP NULL"},
])
wm_render_styler(
    suggestions.style, theme=theme, title="One fill is defensible. Two are not.",
    kicker="03, preprocessing, human decision", wrap_columns={"why it is plausible": 360},
)"""
        ),
        new_code_cell(
            """train_end = 96
train_median = reviewed.loc[:train_end - 1, "amount_usd"].median()
prepared = reviewed.copy()
prepared["amount_usd_missing"] = prepared["amount_usd"].isna()
prepared["amount_usd"] = prepared["amount_usd"].fillna(train_median)
decision_log = wm_build_preprocessing_log(
    reviewed, prepared,
    [PreprocessingDecision(
        field="amount_usd", action="impute", method=f"training median ({train_median:.2f})",
        reason="Right-skewed currency measure; retain missingness indicator.",
        fit_scope="train_only", keep_missing_indicator=True,
    )],
)
wm_render_styler(
    decision_log.style, theme=theme, title="The audit trail starts after the change",
    kicker="04, preprocessing, applied decision", wrap_columns={"reason": 320},
)"""
        ),
        new_code_cell(
            """display_data_chips(
    prepared, theme=theme, target="target", identifier_columns=["record_id"],
    datetime_columns=["month"],
    categorical_columns=["channel", "region", "plan", "campaign", "device", "market"],
    group_label="Forty fields. Six jobs.",
)
wm_render_micro_profile_cards(
    prepared, theme=theme,
    columns=["target", "amount_usd", "account_balance", "channel", "region"],
    visible_cards=3, skew_threshold=1.0,
)"""
        ),
        new_code_cell(
            """channel_evidence = wm_compare_fields(prepared, fields=["channel"])
wm_render_styler(
    channel_evidence.table.style.format({"share": "{:.1%}"}), theme=theme,
    title="Direct is the largest channel—not one of three equal placeholders",
    kicker="05, channel, evidence",
)
style_fig_wm(channel_evidence.figure, title="Sessions by channel", theme=theme)
wm_render_figure_card(channel_evidence.figure, theme=theme, file_stub="eda_channel")

amount_by_channel = wm_compare_fields(prepared, fields=["amount_usd", "channel"])
wm_render_styler(
    amount_by_channel.table.style.format("{:.2f}"), theme=theme,
    title="Amount distribution by channel", kicker="06, selected fields, evidence",
)
style_fig_wm(amount_by_channel.figure, title="Amount by channel", theme=theme)
wm_render_figure_card(amount_by_channel.figure, theme=theme, file_stub="eda_amount_channel")"""
        ),
        new_code_cell(
            """manifest = [
    FeatureDecision("target", "target", "target", "Outcome to explain."),
    FeatureDecision("amount_usd", "numeric", "candidate", "Reviewed currency measure."),
    FeatureDecision("channel", "categorical", "candidate", "Acquisition context."),
    FeatureDecision("month", "time", "context", "Split boundary and drift context."),
    FeatureDecision("record_id", "identifier", "exclude", "Audit key, not behavior."),
    FeatureDecision("comment", "text", "review_only", "Optional reviewer context."),
]
model_frame = prepared[["target", "amount_usd", "channel", "month"]].copy()
manifest_table = wm_validate_feature_manifest(model_frame, manifest)
wm_render_styler(
    manifest_table.style, theme=theme, title="Two candidates enter. The ID stays out.",
    kicker="07, feature boundary, evidence", wrap_columns={"reason": 300},
)
next_think_card(
    theme=theme, title="Which evidence would change the feature boundary?",
    bullets=[
        "Does channel still matter after time and campaign are controlled?",
        "Is missing amount itself associated with the target?",
        "Does the chronological hold-out preserve the same category mix?",
    ], kicker="08, your decision",
)"""
        ),
    ]
    cells[0].metadata["tags"] = ["wm-essential"]
    cells[1].metadata["tags"] = ["wm-noise"]
    for cell in cells[2:]:
        cell.metadata["tags"] = ["wm-essential", "wm-hide-source"]
    return new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "wm-notecards", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
    )


def main() -> None:
    """Write the deterministic public example notebook."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(build_notebook(), OUTPUT)
    print(f"Wrote {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
