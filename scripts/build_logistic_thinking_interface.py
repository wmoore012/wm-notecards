"""Build the public logistic-regression thinking-interface notebook.

The notebook deliberately keeps ordinary Pandas inspection and wm-notecards in
the same analysis. Pandas is the fast audit surface; notecards preserve the
question, reading order, boundaries, and human decision.
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUTPUT = Path("examples/logistic_regression_thinking_interface.ipynb")


def _code(source: str, *, noise: bool = False) -> nbformat.NotebookNode:
    """Return a code cell with the public-example source visibility contract."""
    cell = new_code_cell(source)
    cell.metadata["tags"] = ["wm-noise"] if noise else ["wm-essential", "wm-hide-source"]
    return cell


def _markdown(source: str) -> nbformat.NotebookNode:
    """Return visible notebook prose that survives plain Jupyter and Colab."""
    cell = new_markdown_cell(source)
    cell.metadata["tags"] = ["wm-essential"]
    return cell


def build_notebook() -> nbformat.NotebookNode:
    """Return a deterministic, screenshot-ready logistic-regression notebook."""
    cells = [
        _markdown(
            """# Can recent behavior help us find customers who may leave next month?

This notebook follows a customer file from first inspection to one final test. We will
use ordinary Pandas when it is the fastest honest check, and wm-notecards when the
result needs a reading order, a boundary, or a decision.

The data is synthetic and seeded. The workflow is real: inspect, document, split,
prepare, compare, choose, and test once."""
        ),
        _code(
            """from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from wm_notecards import (
    PreprocessingDecision,
    WMTheme,
    init_notebook,
    wm_build_preprocessing_log,
)
from wm_notecards.cards import (
    question_card,
    takeaway_card,
    wm_check_card,
    wm_counterintuitive_card,
    wm_formula_card,
)
from wm_notecards.charts import style_fig_wm, wm_render_figure_card
from wm_notecards.eda import display_data_chips
from wm_notecards.pictogram import pictogram_card
from wm_notecards.tables import (
    display_cols_by_dtype,
    wm_render_micro_profile_cards,
    wm_render_styler,
)

theme = WMTheme.light()
init_notebook()
RNG_SEED = 20260724""",
            noise=True,
        ),
        _code(
            """# Seeded data keeps the lesson reproducible without pretending it is production evidence.
rng = np.random.default_rng(RNG_SEED)
rows = 1_200
snapshot_month = np.repeat(pd.date_range("2024-01-01", periods=12, freq="MS"), 100)
signup_date = snapshot_month - pd.to_timedelta(rng.integers(45, 900, rows), unit="D")
tenure_months = np.maximum(1, ((snapshot_month - signup_date).days / 30.4).astype(int))
plan = rng.choice(["Starter", "Plus", "Pro"], rows, p=[0.48, 0.36, 0.16])
channel = rng.choice(["Direct", "Partner", "Community"], rows, p=[0.52, 0.29, 0.19])
region = rng.choice(["North", "South", "West", "East"], rows, p=[0.38, 0.27, 0.21, 0.14])
support_tickets = rng.poisson(1.2, rows)
sessions_30d = rng.poisson(8.5, rows)
days_since_login = np.clip(rng.gamma(2.1, 3.4, rows), 0, 45)
monthly_spend = np.round(
    rng.lognormal(3.25, 0.38, rows)
    + np.select([plan == "Plus", plan == "Pro"], [18.0, 52.0], default=0.0),
    2,
)
discount_rate = rng.choice([0.0, 0.10, 0.20], rows, p=[0.62, 0.27, 0.11])
renewal_month = rng.integers(1, 13, rows)

logit = (
    -2.55
    + 0.105 * days_since_login
    + 0.31 * support_tickets
    - 0.085 * sessions_30d
    - 0.013 * tenure_months
    + 0.95 * (plan == "Starter")
    - 0.70 * (plan == "Pro")
    + 0.72 * (discount_rate >= 0.20)
)
left_service = rng.binomial(1, 1 / (1 + np.exp(-logit)))

customers = pd.DataFrame({
    "customer_id": [f"CUS-{i:05d}" for i in range(rows)],
    "signup_date": signup_date.strftime("%Y-%m-%d"),
    "left_service": left_service,
    "plan": plan,
    "channel": channel,
    "region": region,
    "monthly_spend": monthly_spend.astype(str),
    "tenure_months": tenure_months,
    "sessions_30d": sessions_30d,
    "days_since_login": np.round(days_since_login, 1),
    "support_tickets": support_tickets,
    "discount_rate": discount_rate,
    "renewal_month": renewal_month.astype(str),
    "device": rng.choice(["Mobile", "Desktop", "Tablet"], rows, p=[0.61, 0.31, 0.08]),
    "browser": rng.choice(["Chrome", "Safari", "Firefox"], rows, p=[0.58, 0.28, 0.14]),
    "market": rng.choice(["US", "CA", "GB", "AU"], rows, p=[0.55, 0.20, 0.15, 0.10]),
    "campaign": rng.choice(["Organic", "Referral", "Launch"], rows, p=[0.51, 0.31, 0.18]),
    "email_opens_30d": rng.poisson(4.1, rows),
    "feature_clicks_30d": rng.poisson(12.5, rows),
    "invoices_paid": rng.poisson(8.2, rows),
    "late_payments_12m": rng.poisson(0.8, rows),
    "team_size": rng.integers(1, 75, rows),
    "projects_active": rng.integers(0, 18, rows),
    "storage_gb": np.round(rng.gamma(2.5, 8.0, rows), 1),
    "api_calls_30d": rng.integers(0, 9_000, rows),
    "exports_30d": rng.poisson(3.5, rows),
    "collaborators_30d": rng.integers(0, 22, rows),
    "mobile_sessions_30d": rng.poisson(4.5, rows),
    "desktop_sessions_30d": rng.poisson(5.0, rows),
    "help_articles_30d": rng.poisson(1.4, rows),
    "survey_score": rng.integers(1, 11, rows),
    "nps_group": rng.choice(["Detractor", "Passive", "Promoter"], rows, p=[0.24, 0.31, 0.45]),
    "autopay": rng.choice([True, False], rows, p=[0.72, 0.28]),
    "annual_plan": rng.choice([True, False], rows, p=[0.41, 0.59]),
    "used_onboarding": rng.choice([True, False], rows, p=[0.68, 0.32]),
    "admin_role": rng.choice([True, False], rows, p=[0.36, 0.64]),
    "comment": [f"synthetic account note {i}" for i in range(rows)],
    "source_note": [f"generated customer {i}" for i in range(rows)],
    "analyst_note": [f"review batch {i % 8}" for i in range(rows)],
    "snapshot_month": snapshot_month.strftime("%Y-%m-%d"),
})
customers.loc[rng.choice(rows, 34, replace=False), "monthly_spend"] = None
customers.loc[rng.choice(rows, 19, replace=False), "region"] = None
customers.loc[rng.choice(rows, 27, replace=False), "comment"] = None

assert customers.shape == (rows, 40)
assert 0.10 < customers["left_service"].mean() < 0.45"""
        ),
        _code(
            """question_card(
    theme=theme,
    title="What arrived in the file?",
    body="Start with rows a human can recognize. Then check types, gaps, and the target.",
    kicker="01, source, question",
)"""
        ),
        _markdown("""### First look: six customer snapshots

Pandas stays here because the fastest way to understand a file is still to look at it."""),
        _code(
            """customers[[
    "customer_id", "snapshot_month", "left_service", "plan", "channel",
    "region", "monthly_spend", "days_since_login",
]].head(6)"""
        ),
        _code(
            """display_cols_by_dtype(
    customers.dtypes,
    theme,
    "Which fields arrived in the wrong type family?",
    expected_types={
        "signup_date": "time",
        "snapshot_month": "time",
        "monthly_spend": "numeric",
        "renewal_month": "numeric",
    },
)"""
        ),
        _code(
            """# Conversions are explicit. The inspection helper never changes the source.
reviewed = customers.copy()
reviewed["signup_date"] = pd.to_datetime(reviewed["signup_date"], errors="raise")
reviewed["snapshot_month"] = pd.to_datetime(reviewed["snapshot_month"], errors="raise")
reviewed["monthly_spend"] = pd.to_numeric(reviewed["monthly_spend"], errors="coerce")
reviewed["renewal_month"] = pd.to_numeric(reviewed["renewal_month"], errors="raise")

source_checks = [
    {"label": "1,200 rows loaded", "status": "PASS", "detail": "No rows disappeared during parsing."},
    {"label": "No duplicate rows or customer IDs", "status": "PASS", "detail": "The customer snapshot key is unique."},
    {"label": "Target contains only 0 and 1", "status": "PASS", "detail": "0 = stayed; 1 = left next month."},
    {"label": "Observation month parsed for every row", "status": "PASS", "detail": "Time can support a chronological split."},
]
wm_check_card(
    theme=theme,
    title="The file passed its arrival checks.",
    checks=source_checks,
    subtitle="Identity, target, and time are intact. Missingness is the next decision.",
    kicker="01, source contract, checks",
)"""
        ),
        _code(
            """missing_counts = reviewed.isna().sum().loc[lambda s: s.gt(0)].sort_values(ascending=False)
missing_roles = pd.DataFrame({
    "field": missing_counts.index,
    "type": ["numeric", "text", "categorical"],
    "missing": missing_counts.values,
    "share": missing_counts.values / len(reviewed),
})
question_card(
    theme=theme,
    title="Three fields need a decision before we profile anything.",
    body=(
        f"NUMERIC: monthly_spend ({missing_counts['monthly_spend']:,})  |  "
        f"TEXT: comment ({missing_counts['comment']:,})  |  "
        f"CATEGORICAL: region ({missing_counts['region']:,}). "
        "The next views keep this order so nothing has to be remembered."
    ),
    kicker="02, missingness, memory bridge",
    chip_text="3 fields",
)"""
        ),
        _code(
            """missing_summary = missing_roles.copy()
missing_summary["complete"] = len(reviewed) - missing_summary["missing"]
role_colors = {
    "numeric": theme.role_numeric,
    "text": theme.role_text,
    "categorical": theme.role_categorical,
}

missing_fig = go.Figure()
missing_fig.add_trace(go.Bar(
    x=missing_summary["complete"],
    y=missing_summary["field"],
    orientation="h",
    marker_color=[role_colors[kind] for kind in missing_summary["type"]],
    opacity=0.28,
    name="Complete",
    hovertemplate="%{y}: %{x:,} complete<extra></extra>",
))
missing_fig.add_trace(go.Bar(
    x=missing_summary["missing"],
    y=missing_summary["field"],
    orientation="h",
    marker_color=theme.color_missing_accent,
    text=[
        f"{count:,} missing | {share:.1%}"
        for count, share in zip(missing_summary["missing"], missing_summary["share"], strict=True)
    ],
    textposition="outside",
    cliponaxis=False,
    name="Missing",
    hovertemplate="%{y}: %{x:,} missing<extra></extra>",
))
missing_fig.update_layout(barmode="stack", showlegend=False)
missing_fig.update_xaxes(title="Rows", range=[0, len(reviewed) * 1.18], tickformat=",")
missing_fig.update_yaxes(autorange="reversed", title=None)
style_fig_wm(
    missing_fig,
    theme=theme,
    title="Most fields are complete. These three are not.",
    subtitle="Exact counts and shares stay visible before any value is filled",
    category_policy="preserve",
)
wm_render_figure_card(
    missing_fig,
    theme=theme,
    file_stub="logistic_missingness_first_pass",
    kicker="02, missingness, evidence",
)"""
        ),
        _code(
            """missing_decisions = pd.DataFrame([
    {
        "field": "monthly_spend",
        "evidence": "34 gaps in a right-skewed numeric measure.",
        "candidate action": "Training median plus a missing flag",
        "human decision": "TEST",
    },
    {
        "field": "comment",
        "evidence": "27 gaps in optional free text.",
        "candidate action": "Keep null; exclude text from this baseline",
        "human decision": "HOLD OUT",
    },
    {
        "field": "region",
        "evidence": "19 gaps across four named regions.",
        "candidate action": "Confirm what a blank means before encoding",
        "human decision": "CHECK",
    },
])
wm_render_styler(
    missing_decisions.style,
    theme=theme,
    title="What could happen to each gap?",
    subtitle="These are candidate actions. The preprocessing receipt appears only after a method runs.",
    kicker="02, missingness, options",
)"""
        ),
        _code(
            """display_data_chips(
    reviewed,
    theme=theme,
    target="left_service",
    identifier_columns=["customer_id"],
    datetime_columns=["signup_date", "snapshot_month"],
    categorical_columns=["plan", "channel", "region", "device", "market"],
)"""
        ),
        _markdown("""### Numeric fields: Pandas first, then the shapes

The table is the audit trail. The cards put spread, missingness, and skew beside the
same field so the next decision is easier to see."""),
        _code(
            """numeric_fields = [
    "monthly_spend", "tenure_months", "sessions_30d", "days_since_login",
    "support_tickets", "discount_rate",
]
reviewed[numeric_fields].describe().round(2).T"""
        ),
        _code(
            """wm_render_micro_profile_cards(
    reviewed,
    theme=theme,
    columns=numeric_fields,
    visible_cards=3,
    skew_threshold=1.0,
)"""
        ),
        _markdown("""### Categorical fields: counts first, then composition

Missing fields appear first. Counts and percentages use the same denominator."""),
        _code(
            """categorical_fields = ["region", "plan", "channel", "device", "market"]
reviewed[categorical_fields].describe(include="all").T"""
        ),
        _code(
            """wm_render_micro_profile_cards(
    reviewed,
    theme=theme,
    columns=categorical_fields,
    visible_cards=3,
)"""
        ),
        _code(
            """target_counts = (
    reviewed["left_service"]
    .map({0: "Stayed", 1: "Left next month"})
    .value_counts()
    .rename_axis("outcome")
    .reset_index(name="customers")
)
target_counts["share"] = target_counts["customers"] / len(reviewed)
leave_count = int(reviewed["left_service"].sum())
leave_rate = float(reviewed["left_service"].mean())

question_card(
    theme=theme,
    title="What exactly are we asking the model to predict?",
    body=(
        "TARGET: left_service. One row is one customer snapshot. "
        "A 1 means the customer left during the next month. There are no missing target values. "
        "The observed outcome is already binary: the customer left or stayed. The model can rank "
        "outreach review, but the outreach cutoff remains a separate business choice."
    ),
    kicker="03, target contract, question",
    chip_text="BINARY TARGET",
)
pictogram_card(
    percent=leave_rate,
    headline="Customers who left in the next month",
    subtitle=(
        f"{leave_count:,} of {len(reviewed):,} customers left. "
        "This base rate becomes the precision-recall baseline later."
    ),
    big_text=f"{leave_rate:.1%}",
    theme=theme,
    kicker="03, target prevalence, evidence",
)"""
        ),
        _code(
            """target_contract = pd.DataFrame([
    {"question": "Definition", "answer": "Left service during the month after this snapshot"},
    {"question": "Missing target", "answer": "0 rows"},
    {"question": "Decision", "answer": "Rank a human-reviewed outreach queue"},
    {"question": "Business cost", "answer": "Missed leavers vs unwanted outreach to stayers"},
    {"question": "Goodwill boundary", "answer": "A high score does not make contact welcome"},
    {"question": "Expected clues", "answer": "Recent absence and support friction are hypotheses, not facts"},
])
wm_render_styler(
    target_contract.style,
    theme=theme,
    title="The target has a definition, a clock, and a consequence.",
    kicker="03, target contract, documentation",
)"""
        ),
        _code(
            """question_card(
    theme=theme,
    title="Does recent absence separate customers who stay from customers who leave?",
    body="Read the medians and middle halves first. The dots are individual values beyond the whiskers.",
    kicker="03, numeric relationship, question",
)

numeric_by_outcome = reviewed.assign(
    outcome=reviewed["left_service"].map({0: "Stayed", 1: "Left next month"})
)
relationship_fig = go.Figure()
for outcome, color in [("Stayed", "#AAB5BD"), ("Left next month", theme.accent)]:
    values = numeric_by_outcome.loc[numeric_by_outcome["outcome"].eq(outcome), "days_since_login"]
    relationship_fig.add_trace(go.Box(
        y=values,
        name=outcome,
        marker_color=color,
        boxpoints="outliers",
        hovertemplate=f"{outcome}<br>Days since login: %{{y:.1f}}<extra></extra>",
    ))
relationship_fig.update_yaxes(title="Days since last login")
relationship_fig.update_xaxes(title=None)
style_fig_wm(
    relationship_fig,
    theme=theme,
    title="Customers who left had usually been away longer.",
    subtitle="The distributions still overlap, so absence alone cannot decide who leaves",
    category_policy="preserve",
)
wm_render_figure_card(
    relationship_fig,
    theme=theme,
    file_stub="logistic_days_since_login_by_outcome",
    kicker="03, numeric relationship, evidence",
)"""
        ),
        _code(
            """wm_counterintuitive_card(
    theme=theme,
    title="A long absence is a clue, not a verdict.",
    why_misread="Some customers who stayed also had long gaps between logins.",
    ordinary_process="Vacations, seasonality, and low-frequency use can create the same pattern.",
    conclusion_boundary="Absence earns a modeling test. It does not justify outreach by itself.",
    kicker="03, target relationship, reading guide",
)"""
        ),
        _code(
            """plan_rates = (
    reviewed.groupby("plan", dropna=False)["left_service"]
    .agg(customers="size", leavers="sum", leave_rate="mean")
    .sort_values("leave_rate", ascending=True)
    .reset_index()
)
question_card(
    theme=theme,
    title="Do the plan groups leave at the same rate?",
    body="Read the percentage with its numerator and denominator. A small group should not sound louder than it is.",
    kicker="03, categorical relationship, question",
)
wm_render_styler(
    plan_rates.style.format({"leave_rate": "{:.1%}"}),
    theme=theme,
    title="Plan size and leave rate",
    kicker="03, categorical relationship, exact values",
)

plan_fig = go.Figure(go.Bar(
    x=plan_rates["leave_rate"],
    y=plan_rates["plan"],
    orientation="h",
    marker_color=["#B9C4CB", "#82DCE8", theme.accent],
    text=[
        f"{rate:.1%} | {leavers}/{customers}"
        for rate, leavers, customers in zip(
            plan_rates["leave_rate"], plan_rates["leavers"], plan_rates["customers"], strict=True
        )
    ],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}: %{x:.1%}<extra></extra>",
))
plan_fig.update_xaxes(title="Leave rate", tickformat=".0%", rangemode="tozero")
plan_fig.update_yaxes(title=None)
style_fig_wm(
    plan_fig,
    theme=theme,
    title="Starter customers left more often in this sample.",
    subtitle="Descriptive rates only. Validation still decides whether this signal earns a model feature.",
    category_policy="preserve",
)
wm_render_figure_card(
    plan_fig,
    theme=theme,
    file_stub="logistic_plan_leave_rate",
    kicker="03, categorical relationship, evidence",
)"""
        ),
        _code(
            """wm_counterintuitive_card(
    theme=theme,
    title="How to read the plan comparison",
    why_misread="The longest bar can look like the plan caused customers to leave.",
    ordinary_process="Plan choice can travel with price sensitivity, tenure, channel, and customer needs.",
    conclusion_boundary="Plan context may improve prediction. The chart does not prove cause or justify different treatment.",
    kicker="03, categorical relationship, reading guide",
)"""
        ),
        _code(
            """association_rows = []
for field in [
    "monthly_spend", "tenure_months", "sessions_30d",
    "days_since_login", "support_tickets", "discount_rate",
]:
    complete = reviewed[[field, "left_service"]].dropna()
    association_rows.append({
        "field": field,
        "correlation with leaving": complete[field].corr(complete["left_service"]),
    })
numeric_associations = (
    pd.DataFrame(association_rows)
    .assign(magnitude=lambda frame: frame["correlation with leaving"].abs())
    .sort_values("magnitude", ascending=True)
)

question_card(
    theme=theme,
    title="Which numeric fields move with leaving before the model combines them?",
    body="Right means a positive association. Left means a negative association. Distance from zero shows strength.",
    kicker="03, numeric relationships, reading guide",
)
association_fig = go.Figure(go.Bar(
    x=numeric_associations["correlation with leaving"],
    y=numeric_associations["field"],
    orientation="h",
    marker_color=[theme.accent if value >= 0 else "#6B7B88" for value in numeric_associations["correlation with leaving"]],
    text=[f"{value:+.2f}" for value in numeric_associations["correlation with leaving"]],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}: %{x:+.3f}<extra></extra>",
))
association_fig.add_vline(x=0, line_color="#38444D", line_width=1)
association_fig.update_xaxes(title="Pearson correlation with leaving", range=[-0.35, 0.45])
association_fig.update_yaxes(title=None)
style_fig_wm(
    association_fig,
    theme=theme,
    title="Recent absence has the clearest one-field association.",
    subtitle="Correlation is descriptive and one field at a time. It is not causation.",
    category_policy="preserve",
)
wm_render_figure_card(
    association_fig,
    theme=theme,
    file_stub="logistic_numeric_target_associations",
    kicker="03, numeric relationships, evidence",
)"""
        ),
        _code(
            """feature_ledger = pd.DataFrame([
    {
        "field": "customer_id", "evidence": "Unique on every row", "transformation": "None",
        "validation": "Confirm exclusion", "boundary": "Direct identifier", "decision": "EXCLUDE",
    },
    {
        "field": "signup_date", "evidence": "Customer signup date", "transformation": "Derive tenure",
        "validation": "Fit derived rules on training only", "boundary": "Time proxy", "decision": "DERIVE",
    },
    {
        "field": "region", "evidence": "19 missing values and four labels", "transformation": "Training-only encoding",
        "validation": "Compare PR and error slices", "boundary": "Fairness and proxy review", "decision": "TEST",
    },
    {
        "field": "comment", "evidence": "27 missing free-text values", "transformation": "Separate text study",
        "validation": "No text in this baseline", "boundary": "Privacy and leakage review", "decision": "HOLD OUT",
    },
])
wm_render_styler(
    feature_ledger.style,
    theme=theme,
    title="The feature decision ledger",
    subtitle="Evidence, transformation, validation, risk boundary, and final decision stay together.",
    kicker="04, feature decisions, audit trail",
)"""
        ),
        _code(
            """question_card(
    theme=theme,
    title="Can we compare models without letting the future leak backward?",
    body="Training learns. Validation chooses the model and threshold. Test is opened once at the end.",
    kicker="04, chronological split, question",
)

validation_start = pd.Timestamp("2024-09-01")
test_start = pd.Timestamp("2024-11-01")
train = reviewed.loc[reviewed["snapshot_month"] < validation_start].copy()
validation = reviewed.loc[
    reviewed["snapshot_month"].between(validation_start, test_start, inclusive="left")
].copy()
test = reviewed.loc[reviewed["snapshot_month"] >= test_start].copy()
assert train["snapshot_month"].max() < validation["snapshot_month"].min()
assert validation["snapshot_month"].max() < test["snapshot_month"].min()

split_rows = [
    ("Training", pd.Timestamp("2024-01-01"), pd.Timestamp("2024-08-31"), len(train), "#222A31"),
    ("Validation", validation_start, pd.Timestamp("2024-10-31"), len(validation), theme.accent),
    ("Test", test_start, pd.Timestamp("2024-12-31"), len(test), "#B74C5F"),
]
split_total = sum(count for _, _, _, count, _ in split_rows)
split_shares = {label: count / split_total for label, _, _, count, _ in split_rows}
split_fig = go.Figure()
for label, start, end, count, color in split_rows:
    split_fig.add_trace(go.Bar(
        # Plotly date axes measure horizontal bar lengths in milliseconds.
        # Passing day counts makes the blocks look like stray dots.
        x=[(end - start).total_seconds() * 1_000],
        y=[label],
        base=[start],
        orientation="h",
        marker={"color": color, "line": {"width": 0}},
        width=0.48,
        text=[f"{start:%b}-{end:%b} | {count:,} rows"],
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate=f"{label}: %{{text}}<extra></extra>",
        showlegend=False,
    ))
split_fig.update_xaxes(title="Observation month", tickformat="%b %Y", type="date")
split_fig.update_yaxes(title=None, categoryorder="array", categoryarray=["Test", "Validation", "Training"])
style_fig_wm(
    split_fig,
    theme=theme,
    title=(
        f"{split_shares['Training']:.0%} train. {split_shares['Validation']:.0%} choose. "
        f"{split_shares['Test']:.0%} test once."
    ),
    subtitle="No imputer, encoder, scaler, model, or threshold learns from the final test window",
    category_policy="preserve",
)
wm_render_figure_card(
    split_fig,
    theme=theme,
    file_stub="logistic_chronological_split",
    kicker="04, train validation test, evidence",
)"""
        ),
        _code(
            """train_median = float(train["monthly_spend"].median())
prepared = reviewed.copy()
prepared["monthly_spend_missing"] = prepared["monthly_spend"].isna()
prepared["monthly_spend"] = prepared["monthly_spend"].fillna(train_median)

decision_log = wm_build_preprocessing_log(
    reviewed,
    prepared,
    [PreprocessingDecision(
        field="monthly_spend",
        action="impute",
        method=f"training median ({train_median:.2f})",
        reason="Preserve rows and keep the missing event visible",
        fit_scope="train_only",
        keep_missing_indicator=True,
    )],
)
wm_render_styler(
    decision_log.style,
    theme=theme,
    title="What training filled / what remains missing",
    subtitle="Monthly spend is filled from training only. Region and comment keep their original gaps.",
    kicker="04, preprocessing, audit trail",
)"""
        ),
        _code(
            r'''target = "left_service"
numeric_features = [
    "monthly_spend", "tenure_months", "sessions_30d", "days_since_login",
    "support_tickets", "discount_rate", "monthly_spend_missing",
]
categorical_features = ["plan", "channel", "region"]
behavior_features = ["tenure_months", "sessions_30d", "days_since_login", "support_tickets"]
model_specs = {
    "Activity only": (behavior_features, []),
    "Activity plus account context": (numeric_features, categorical_features),
}

question_card(
    theme=theme,
    title="Does account context earn its place?",
    body="The larger model must improve later-month ranking enough to justify more fields and more review.",
    kicker="05, model comparison, question",
)
model_contract = pd.DataFrame([
    {
        "model": name,
        "numeric fields": len(numeric),
        "categorical fields": len(categorical),
        "job": "Behavior baseline" if not categorical else "Test whether account context adds signal",
    }
    for name, (numeric, categorical) in model_specs.items()
])
wm_render_styler(
    model_contract.style,
    theme=theme,
    title="What each model is allowed to learn",
    subtitle="Both models learn on the same rows and face the same validation months.",
    kicker="05, model contract, exact fields",
)
wm_formula_card(
    title="Preparation happens inside each model pipeline",
    theme=theme,
    items=[
        {
            "label": "NUMERIC LANE",
            "latex": r"x_{num} \rightarrow \operatorname{median}_{train} \rightarrow \operatorname{scale}",
            "fallback": "numeric -> training median -> standard scale",
        },
        {
            "label": "CATEGORY LANE",
            "latex": r"x_{cat} \rightarrow \operatorname{mode}_{train} \rightarrow \operatorname{one\!-\!hot}",
            "fallback": "category -> training mode -> one-hot columns",
        },
        {
            "label": "MODEL",
            "latex": r"P(y=1 \mid x)=\sigma(\beta_0 + x^T\beta)",
            "fallback": "prepared fields -> probability of leaving next month",
        },
    ],
    kicker="05, model pipeline, formula",
)'''
        ),
        _code(
            """def _pipeline(numeric: list[str], categorical: list[str]) -> Pipeline:
    \"\"\"Build one leakage-safe scikit-learn pipeline.\"\"\"
    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric:
        transformers.append((
            "numeric",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler()),
            ]),
            numeric,
        ))
    if categorical:
        transformers.append((
            "categorical",
            Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encode", OneHotEncoder(handle_unknown="ignore")),
            ]),
            categorical,
        ))
    return Pipeline([
        ("prepare", ColumnTransformer(transformers)),
        ("model", LogisticRegression(max_iter=1_500, random_state=RNG_SEED)),
    ])""",
            noise=True,
        ),
        _code(
            """# Fit is intentionally separate from scoring so the learning boundary stays visible.
train_prepared = prepared.loc[train.index]
validation_prepared = prepared.loc[validation.index]
test_prepared = prepared.loc[test.index]

models: dict[str, Pipeline] = {}
validation_probabilities: dict[str, np.ndarray] = {}
for name, (numeric, categorical) in model_specs.items():
    features = numeric + categorical
    model = _pipeline(numeric, categorical)
    model.fit(train_prepared[features], train_prepared[target])
    models[name] = model
    validation_probabilities[name] = model.predict_proba(validation_prepared[features])[:, 1]"""
        ),
        _code(
            """score_rows = []
for name, probabilities in validation_probabilities.items():
    predictions = (probabilities >= 0.50).astype(int)
    score_rows.append({
        "model": name,
        "accuracy": accuracy_score(validation_prepared[target], predictions),
        "ROC AUC": roc_auc_score(validation_prepared[target], probabilities),
        "PR AUC": average_precision_score(validation_prepared[target], probabilities),
        "precision @ .50": precision_score(validation_prepared[target], predictions, zero_division=0),
        "recall @ .50": recall_score(validation_prepared[target], predictions, zero_division=0),
    })
scores = pd.DataFrame(score_rows).sort_values("PR AUC", ascending=False).reset_index(drop=True)
winner_name = str(scores.iloc[0]["model"])
winner = models[winner_name]
winner_probability = validation_probabilities[winner_name]
validation_prevalence = float(validation_prepared[target].mean())

wm_render_styler(
    scores.style.format({
        "accuracy": "{:.3f}", "ROC AUC": "{:.3f}", "PR AUC": "{:.3f}",
        "precision @ .50": "{:.1%}", "recall @ .50": "{:.1%}",
    }),
    theme=theme,
    title="Which model ranks later-month leavers better?",
    subtitle="PR AUC gets priority because leaving is the less common outcome.",
    kicker="06, validation, exact scores",
)

pr_fig = go.Figure()
for name, probabilities in validation_probabilities.items():
    precision, recall, _ = precision_recall_curve(validation_prepared[target], probabilities)
    pr_fig.add_trace(go.Scatter(
        x=recall,
        y=precision,
        mode="lines",
        name=name,
        line={"width": 3, "color": theme.accent if name == winner_name else "#27384F"},
        hovertemplate="Recall %{x:.1%}<br>Precision %{y:.1%}<extra></extra>",
    ))
pr_fig.add_hline(
    y=validation_prevalence,
    line_dash="dash",
    line_color="#6B7B88",
    annotation_text=f"Random ranking baseline: {validation_prevalence:.1%}",
    annotation_position="bottom right",
)
pr_fig.update_xaxes(title="Recall", tickformat=".0%", range=[0, 1])
pr_fig.update_yaxes(title="Precision", tickformat=".0%", range=[0, 1.02])
style_fig_wm(
    pr_fig,
    theme=theme,
    title=f"{winner_name} keeps more precision as recall grows.",
    subtitle="A useful curve should stay above the random-ranking baseline across the operating range",
    category_policy="preserve",
)
wm_render_figure_card(
    pr_fig,
    theme=theme,
    file_stub="logistic_precision_recall",
    kicker="06, validation, visual evidence",
)"""
        ),
        _code(
            """question_card(
    theme=theme,
    title="Where should the outreach cutoff sit?",
    body=(
        "Lower cutoffs find more leavers and contact more stayers. "
        "For this teaching example, validation F1 chooses the balance point. "
        "A real team would replace that rule with capacity, cost, and goodwill."
    ),
    kicker="07, threshold, human decision",
)

precision_path, recall_path, threshold_path = precision_recall_curve(
    validation_prepared[target], winner_probability
)
f1_path = np.divide(
    2 * precision_path[:-1] * recall_path[:-1],
    precision_path[:-1] + recall_path[:-1],
    out=np.zeros_like(threshold_path),
    where=(precision_path[:-1] + recall_path[:-1]) > 0,
)
selected_threshold = float(threshold_path[int(np.argmax(f1_path))])

candidate_thresholds = sorted(set([0.30, 0.40, 0.50, 0.60, round(selected_threshold, 3)]))
threshold_rows = []
for cutoff in candidate_thresholds:
    predicted = (winner_probability >= cutoff).astype(int)
    tn, fp, fn, tp = confusion_matrix(validation_prepared[target], predicted, labels=[0, 1]).ravel()
    threshold_rows.append({
        "threshold": cutoff,
        "precision": precision_score(validation_prepared[target], predicted, zero_division=0),
        "recall": recall_score(validation_prepared[target], predicted, zero_division=0),
        "F1": f1_score(validation_prepared[target], predicted, zero_division=0),
        "stayers contacted": int(fp),
        "leavers missed": int(fn),
    })
thresholds = pd.DataFrame(threshold_rows)

wm_render_styler(
    thresholds.style.format({
        "threshold": "{:.3f}", "precision": "{:.1%}", "recall": "{:.1%}", "F1": "{:.3f}",
    }),
    theme=theme,
    title="Every cutoff changes who receives outreach.",
    subtitle=f"Validation F1 selects {selected_threshold:.3f} for the demo. It is not a business policy.",
    kicker="07, threshold, exact tradeoff",
)

threshold_fig = go.Figure()
threshold_fig.add_trace(go.Scatter(
    x=thresholds["threshold"], y=thresholds["precision"],
    mode="lines+markers", name="Precision", line={"color": theme.accent, "width": 3},
))
threshold_fig.add_trace(go.Scatter(
    x=thresholds["threshold"], y=thresholds["F1"],
    mode="lines+markers", name="F1 balance", line={"color": "#756A9A", "width": 3, "dash": "dot"},
))
threshold_fig.add_trace(go.Scatter(
    x=thresholds["threshold"], y=thresholds["recall"],
    mode="lines+markers", name="Recall", line={"color": "#B74C5F", "width": 3},
))
threshold_fig.add_vline(
    x=selected_threshold,
    line_dash="dash",
    line_color="#222A31",
    annotation_text=f"Selected by validation F1: {selected_threshold:.3f}",
    annotation_position="top",
)
threshold_fig.update_xaxes(title="Outreach threshold", tickformat=".0%")
threshold_fig.update_yaxes(title="Share", tickformat=".0%", range=[0, 1])
style_fig_wm(
    threshold_fig,
    theme=theme,
    title="Lower cutoffs find more leavers and contact more stayers.",
    subtitle="F1 shows the balance; the table above gives exact false-contact and missed-leaver counts",
    category_policy="preserve",
)
wm_render_figure_card(
    threshold_fig,
    theme=theme,
    file_stub="logistic_threshold_tradeoff",
    kicker="07, threshold, visual tradeoff",
)"""
        ),
        _code(
            """# The test set is opened once, after model and threshold selection are complete.
winner_numeric, winner_categorical = model_specs[winner_name]
winner_features = winner_numeric + winner_categorical
test_probability = winner.predict_proba(test_prepared[winner_features])[:, 1]
test_prediction = (test_probability >= selected_threshold).astype(int)
test_tn, test_fp, test_fn, test_tp = confusion_matrix(
    test_prepared[target], test_prediction, labels=[0, 1]
).ravel()

test_scores = pd.DataFrame([{
    "test rows": len(test_prepared),
    "leavers": int(test_prepared[target].sum()),
    "PR AUC": average_precision_score(test_prepared[target], test_probability),
    "ROC AUC": roc_auc_score(test_prepared[target], test_probability),
    "precision": precision_score(test_prepared[target], test_prediction, zero_division=0),
    "recall": recall_score(test_prepared[target], test_prediction, zero_division=0),
}])
confusion_receipt = pd.DataFrame([
    {"actual": "Stayed", "predicted stayed": int(test_tn), "predicted left": int(test_fp)},
    {"actual": "Left", "predicted stayed": int(test_fn), "predicted left": int(test_tp)},
])
assert int(confusion_receipt[["predicted stayed", "predicted left"]].to_numpy().sum()) == len(test_prepared)

wm_render_styler(
    test_scores.style.format({
        "PR AUC": "{:.3f}", "ROC AUC": "{:.3f}", "precision": "{:.1%}", "recall": "{:.1%}",
    }),
    theme=theme,
    title="The final two months answer the last model question.",
    subtitle=f"{winner_name} and threshold {selected_threshold:.3f} were fixed before this test.",
    kicker="08, final test, scores",
)
wm_render_styler(
    confusion_receipt.style,
    theme=theme,
    title="Who did the final test classify correctly?",
    subtitle="The heatmap below turns the same four counts into a faster read.",
    kicker="08, final test, confusion counts",
)

confusion_values = np.array([[test_tn, test_fp], [test_fn, test_tp]])
confusion_fig = go.Figure(go.Heatmap(
    z=confusion_values,
    x=["Predicted stayed", "Predicted left"],
    y=["Actually stayed", "Actually left"],
    text=confusion_values,
    texttemplate="%{text:,}",
    colorscale=[[0, "#F4F5F2"], [1, theme.accent]],
    showscale=False,
    hovertemplate="%{y}<br>%{x}: %{z:,}<extra></extra>",
))
confusion_fig.update_yaxes(autorange="reversed", title=None)
confusion_fig.update_xaxes(title=None)
style_fig_wm(
    confusion_fig,
    theme=theme,
    title="The final test makes both kinds of error visible.",
    subtitle=f"False contacts: {test_fp:,} | missed leavers: {test_fn:,}",
    category_policy="preserve",
)
wm_render_figure_card(
    confusion_fig,
    theme=theme,
    file_stub="logistic_confusion_matrix",
    kicker="08, final test, visual evidence",
)"""
        ),
        _code(
            """wm_counterintuitive_card(
    theme=theme,
    title="A correct score can still lead to the wrong action.",
    why_misread="A probability above the cutoff can sound like proof that a customer will leave.",
    ordinary_process="The model ranks patterns in this sample. It does not observe motive, consent, or future product changes.",
    conclusion_boundary="Use the score to prioritize review. Keep outreach policy and customer goodwill with people.",
    kicker="08, final test, boundary",
)"""
        ),
        _code(
            """feature_names = winner.named_steps["prepare"].get_feature_names_out()
coefficients = pd.DataFrame({
    "feature": feature_names,
    "coefficient": winner.named_steps["model"].coef_[0],
})
coefficients["absolute weight"] = coefficients["coefficient"].abs()
top_coefficients = coefficients.nlargest(10, "absolute weight").drop(columns="absolute weight")

question_card(
    theme=theme,
    title="Which fitted signals push the score up or pull it down?",
    body="Right increases the fitted log-odds of leaving. Left decreases them. Size is model weight after preprocessing, not business impact.",
    kicker="09, coefficients, reading guide",
)
wm_render_styler(
    top_coefficients.style.format({"coefficient": "{:+.3f}"}),
    theme=theme,
    title="The ten largest fitted coefficients",
    kicker="09, coefficients, exact values",
)

coefficient_plot = top_coefficients.sort_values("coefficient")
coefficient_fig = go.Figure(go.Bar(
    x=coefficient_plot["coefficient"],
    y=coefficient_plot["feature"],
    orientation="h",
    marker_color=[theme.accent if value > 0 else "#6B7B88" for value in coefficient_plot["coefficient"]],
    text=[f"{value:+.2f}" for value in coefficient_plot["coefficient"]],
    textposition="outside",
    cliponaxis=False,
    hovertemplate="%{y}<br>coefficient %{x:+.3f}<extra></extra>",
))
coefficient_fig.add_vline(x=0, line_color="#38444D", line_width=1)
coefficient_fig.update_xaxes(title="Logistic coefficient after preprocessing")
coefficient_fig.update_yaxes(title=None)
style_fig_wm(
    coefficient_fig,
    theme=theme,
    title="The fitted model moves in both directions.",
    subtitle="Coefficient direction is an explanation of the model, not a causal claim",
    category_policy="preserve",
)
wm_render_figure_card(
    coefficient_fig,
    theme=theme,
    file_stub="logistic_coefficient_directions",
    kicker="09, coefficients, visual evidence",
)"""
        ),
        _code(
            """best_validation = scores.iloc[0]
takeaway_card(
    theme=theme,
    title="The model earns a review queue, not the right to contact anyone.",
    metric=f"{winner_name} | validation PR AUC {best_validation['PR AUC']:.3f}",
    body=(
        "The workflow preserved time order, fitted preparation on training rows, selected on validation, "
        "and opened the final test once. That earns a bounded experiment, not automatic outreach."
    ),
    bullets=[
        "Choose operating policy from capacity, cost, consent, and customer goodwill.",
        "Monitor later-month PR AUC, recall, calibration, and error slices.",
        "Keep identifiers and optional text outside this baseline model.",
    ],
    kicker="10, recommendation, human decision",
)"""
        ),
        _markdown(
            """---

Jupyter gave me `df.describe()`.

I wanted `df.explain()`.

The questions are predictable.

**The notebook should be too.**"""
        ),
    ]

    return new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "wm-notecards",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3"},
        },
    )


def main() -> None:
    """Write the deterministic public notebook."""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(build_notebook(), OUTPUT)
    print(f"Wrote {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
