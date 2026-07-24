"""Build the public, fully synthetic Simple Seasonal Forecasting Lab."""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUTPUT = Path("examples/simple_seasonal_forecasting_lab.ipynb")


def build_notebook() -> nbformat.NotebookNode:
    """Return a deterministic notebook that exercises the public card vocabulary."""
    cells = [
        new_markdown_cell(
            "# Simple Seasonal Forecasting Lab\n\n"
            "A synthetic monthly series. A visible equation. One untouched year."
        ),
        new_code_cell(
            """import numpy as np
import pandas as pd
import plotly.graph_objects as go

from wm_notecards import WMTheme, init_notebook
from wm_notecards.cards import (
    big_number_card,
    glossary_card,
    next_think_card,
    preview_card,
    question_card,
    question_pair,
    takeaway_card,
    verdict_card,
    wm_check_card,
    wm_counterintuitive_card,
    wm_formula_card,
)
from wm_notecards.charts import style_fig_wm, wm_render_figure_card
from wm_notecards.eda import wm_build_category_share_table, wm_eda_overview
from wm_notecards.pictogram import pictogram_card
from wm_notecards.tables import wm_render_styler

theme = WMTheme.light()
init_notebook()
RNG_SEED = 20260718"""
        ),
        new_code_cell(
            """question_card(
    theme=theme,
    title="Can a simple model recover a rhythm we created on purpose?",
    body=(
        "We know the answer because we own the data-generating equation. "
        "The notebook's job is to make the evidence legible before asking you to decide."
    ),
    kicker="01, synthetic data, question",
    chip_text="SAFE TO SHARE",
)

glossary_card(
    theme=theme,
    title="Three terms before the evidence",
    terms={
        "Trend": "A long-run change in level across time.",
        "Seasonality": "A pattern that repeats at a known calendar interval.",
        "Hold-out": "The final observations kept unseen while the model is fitted.",
    },
    kicker="01, glossary",
)"""
        ),
        new_code_cell(
            """rng = np.random.default_rng(RNG_SEED)
dates = pd.date_range("2018-01-01", periods=84, freq="MS")
t = np.arange(len(dates))
season = 18 * np.sin(2 * np.pi * t / 12 - np.pi / 3)
values = 72 + 0.55 * t + season + rng.normal(0, 4.5, len(t))
demo = pd.DataFrame({
    "record_id": [f"SYN-{index:03d}" for index in range(len(dates))],
    "month": dates,
    "value": values,
    "channel": np.resize(["Direct", "Partner", "Community"], len(dates)),
    "exposure": rng.lognormal(mean=1.2, sigma=0.9, size=len(dates)),
    "is_peak_window": pd.Series(dates).dt.month.isin([4, 5, 6]).to_numpy(),
})
demo.loc[[7, 38], "exposure"] = np.nan
demo["split"] = np.where(demo.index < 72, "Train", "Hold-out")

question_pair(
    theme=theme,
    kicker="02, reading order",
    chip_text="EDA",
    left={"title": "Is there drift?", "body": "Compare the beginning and end of the line."},
    right={"title": "Is there rhythm?", "body": "Look for peaks roughly twelve months apart."},
)"""
        ),
        new_code_cell(
            r"""eda_contract = wm_eda_overview(
    demo,
    theme=theme,
    target="value",
    identifier_columns=["record_id"],
    datetime_columns=["month"],
    categorical_columns=["channel", "split"],
    columns=["value", "exposure", "channel", "split", "is_peak_window"],
    skew_threshold=1.0,
    visible_cards=3,
)

category_share = wm_build_category_share_table(
    demo,
    ["channel", "split"],
    labels={"channel": "Acquisition channel", "split": "Evidence role"},
)
wm_render_styler(
    category_share.style.format({"share of all rows": "{:.1%}"}).hide(),
    theme=theme,
    title="Process fields stay grouped, ordered, and reconciled to all rows",
    subtitle="Each field group is sorted from most common to least common",
    kicker="02, EDA, categorical shares",
)

wm_formula_card(
    theme=theme,
    title="The math and the processing order stay visible",
    items=[
        {
            "label": "Data-generating equation",
            "latex": r"\[y_t = 72 + 0.55t + 18\sin(2\pi t/12 - \pi/3) + \epsilon_t\]",
            "fallback": "level + trend + annual rhythm + seeded Gaussian noise",
        },
        {
            "label": "Pipeline rule",
            "latex": r"\[x \rightarrow \text{{inspect}} \rightarrow \text{{split in time}} \rightarrow \hat{{y}}\]",
            "fallback": "inspect first -> preserve time order -> fit -> forecast",
        },
    ],
    kicker="02, formula, preprocessing contract",
)"""
        ),
        new_code_cell(
            """summary = pd.DataFrame({
    "evidence": ["Starting level", "Ending level", "Hold-out rows", "Random seed"],
    "value": [f"{demo.value.iloc[0]:.1f}", f"{demo.value.iloc[-1]:.1f}", "12", str(RNG_SEED)],
    "how to read it": [
        "The series begins near its designed baseline.",
        "Trend and seasonality both influence the endpoint.",
        "The final year stays unseen by the training fit.",
        "Anyone can regenerate the exact same teaching data.",
    ],
})
wm_render_styler(
    summary.style,
    theme=theme,
    title="The evidence has an audit trail",
    kicker="03, table, exact values",
    wrap_columns={"how to read it": 320},
)

fig = go.Figure()
for split, color in [("Train", theme.accent), ("Hold-out", "#B74C5F")]:
    part = demo[demo.split == split]
    fig.add_trace(go.Scatter(x=part.month, y=part.value, mode="lines+markers", name=split,
                             line={"color": color, "width": 3}))
style_fig_wm(
    fig,
    theme=theme,
    title="The line climbs while the annual wave keeps returning",
    subtitle="Cyan is training evidence; rose is the untouched final year",
)
wm_render_figure_card(fig, theme=theme, file_stub="simple_seasonal_forecasting_lab", kicker="03, chart")"""
        ),
        new_code_cell(
            """peak_month_share = float((demo.month.dt.month.isin([4, 5, 6])).mean())
pictogram_card(
    percent=peak_month_share,
    headline="One quarter of observations sit in the designed peak-season window",
    subtitle=f"{peak_month_share:.0%} of synthetic months",
    theme=theme,
    icon="chart_bar",
    chip_text="SCALE",
    kicker="04, pictogram",
)

big_number_card(
    theme=theme,
    title="The hold-out is deliberately one full seasonal cycle",
    value="12",
    value_label="months kept out of training",
    body="That gives every calendar month one honest chance to surprise the model.",
    kicker="04, big number",
)"""
        ),
        new_code_cell(
            """wm_counterintuitive_card(
    theme=theme,
    why_misread="A smooth seasonal fit can look like proof that the model understands time.",
    ordinary_process="We manufactured the rhythm and used only one hold-out cycle.",
    conclusion_boundary="This proves the rendering and teaching workflow, not production accuracy.",
    math_items=[{"label": "Boundary", "fallback": "demo evidence != deployment evidence"}],
    kicker="05, counterintuitive boundary",
)

preview_card(
    theme=theme,
    title="Before the decision, check what actually survived",
    body="The release gate separates reproducibility, readability, and claims.",
    bullets=["Seed is public.", "No external CSV is bundled.", "The conclusion stays inside the evidence."],
    kicker="05, preview",
)

wm_check_card(
    theme=theme,
    title="Open-source example release gate",
    checks=[
        {"label": "Provenance", "status": "PASS", "detail": "Equation and seed are visible."},
        {"label": "Layout", "status": "PASS", "detail": "Every role uses the shared shell."},
        {"label": "Claims", "status": "PASS", "detail": "Teaching demo only."},
    ],
    kicker="05, checklist",
)"""
        ),
        new_code_cell(
            """takeaway_card(
    theme=theme,
    title="The untouched year keeps the climb and the annual wave.",
    metric="12 consecutive months held out",
    body=(
        "The visual pattern survives the time split. That earns a forecasting question; "
        "it does not yet crown a model."
    ),
    bullets=[
        "The equation makes the synthetic trend and seasonality auditable.",
        "The table preserves exact values while the chart carries shape.",
        "One seasonal cycle is enough for this lesson, not a production claim.",
    ],
    kicker="06, takeaway",
)

verdict_card(
    theme=theme,
    title="Ready as an OSS teaching example",
    verdict="check",
    body="Safe to share because the data is generated here and the evidence boundary is explicit.",
    kicker="06, verdict",
)

next_think_card(
    theme=theme,
    title="Your decision: which real question should this interface help you think through?",
    body="Swap in data you have the right to use. Keep the choreography and the release gates.",
    kicker="06, human decision",
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
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3"},
        },
    )


def main() -> None:
    """Write the deterministic example notebook."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(build_notebook(), OUTPUT)
    print(f"Wrote {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
